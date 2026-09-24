from flask import Blueprint, render_template, request, jsonify
from app.database import get_db_connection

ticket_bp = Blueprint("tickets", __name__)


@ticket_bp.route("/")
def home():
    connection = get_db_connection()

    tickets = connection.execute(
        """
        SELECT
            t.ticket_id,
            t.title,
            t.category,
            t.priority,
            t.status,
            t.user_confirmed,
            t.created_at,
            t.assigned_to,
            u.name AS employee_name
        FROM tickets t
        JOIN users u ON t.created_by = u.user_id
        ORDER BY t.ticket_id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        tickets=tickets
    )


@ticket_bp.route("/api/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json()

    # Check that request contains JSON
    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    # Required fields
    required_fields = [
        "title",
        "description",
        "category",
        "priority",
        "created_by"
    ]

    # Check mandatory fields
    missing_fields = [
        field for field in required_fields
        if field not in data or not str(data[field]).strip()
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing mandatory fields",
            "fields": missing_fields
        }), 400

    connection = get_db_connection()

    try:
        # Check whether employee exists
        user = connection.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id = ?
            """,
            (data["created_by"],)
        ).fetchone()

        if user is None:
            return jsonify({
                "error": "User does not exist"
            }), 404

        # Validate priority
        allowed_priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

        priority = str(data["priority"]).upper()

        if priority not in allowed_priorities:
            return jsonify({
                "error": "Invalid priority",
                "allowed_values": allowed_priorities
            }), 400

        # Create ticket
        cursor = connection.execute(
            """
            INSERT INTO tickets
            (
                title,
                description,
                category,
                priority,
                status,
                created_by
            )
            VALUES (?, ?, ?, ?, 'NEW', ?)
            """,
            (
                data["title"].strip(),
                data["description"].strip(),
                data["category"].strip(),
                priority,
                data["created_by"]
            )
        )

        ticket_id = cursor.lastrowid

        # Record initial status
        connection.execute(
            """
            INSERT INTO ticket_history
            (
                ticket_id,
                old_status,
                new_status,
                changed_by
            )
            VALUES (?, NULL, 'NEW', ?)
            """,
            (
                ticket_id,
                data["created_by"]
            )
        )

        connection.commit()

        return jsonify({
            "message": "Ticket created successfully",
            "ticket_id": ticket_id,
            "status": "NEW"
        }), 201

    except Exception as error:
        connection.rollback()

        return jsonify({
            "error": "Failed to create ticket",
            "details": str(error)
        }), 500

    finally:
        connection.close()
@ticket_bp.route("/api/tickets/<int:ticket_id>/assign", methods=["PUT"])
def assign_ticket(ticket_id):
    data = request.get_json()

    if not data or "assigned_to" not in data:
        return jsonify({
            "error": "assigned_to is required"
        }), 400

    assigned_to = data["assigned_to"]

    connection = get_db_connection()

    try:
        # Check that the ticket exists
        ticket = connection.execute(
            """
            SELECT ticket_id, status
            FROM tickets
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchone()

        if ticket is None:
            return jsonify({
                "error": "Ticket not found"
            }), 404

        # Ticket must be NEW before assignment
        if ticket["status"] != "NEW":
            return jsonify({
                "error": "Only NEW tickets can be assigned"
            }), 400

        # Check that assigned user exists and is an agent/admin
        agent = connection.execute(
            """
            SELECT user_id, role
            FROM users
            WHERE user_id = ?
            """,
            (assigned_to,)
        ).fetchone()

        if agent is None:
            return jsonify({
                "error": "Assigned user does not exist"
            }), 404

        if agent["role"] not in ("AGENT", "ADMIN"):
            return jsonify({
                "error": "Ticket can only be assigned to an AGENT or ADMIN"
            }), 400

        # Assign ticket
        connection.execute(
            """
            UPDATE tickets
            SET assigned_to = ?,
                status = 'ASSIGNED',
                updated_at = CURRENT_TIMESTAMP
            WHERE ticket_id = ?
            """,
            (assigned_to, ticket_id)
        )

        # Record status change
        connection.execute(
            """
            INSERT INTO ticket_history
            (
                ticket_id,
                old_status,
                new_status,
                changed_by
            )
            VALUES (?, 'NEW', 'ASSIGNED', ?)
            """,
            (ticket_id, assigned_to)
        )

        connection.commit()

        return jsonify({
            "message": "Ticket assigned successfully",
            "ticket_id": ticket_id,
            "assigned_to": assigned_to,
            "status": "ASSIGNED"
        }), 200

    except Exception as error:
        connection.rollback()

        return jsonify({
            "error": "Failed to assign ticket",
            "details": str(error)
        }), 500

    finally:
        connection.close()
@ticket_bp.route("/api/tickets/<int:ticket_id>/status", methods=["PUT"])
def update_ticket_status(ticket_id):
    data = request.get_json()

    if not data or "status" not in data or "changed_by" not in data:
        return jsonify({
            "error": "status and changed_by are required"
        }), 400

    new_status = str(data["status"]).upper()
    changed_by = data["changed_by"]

    allowed_statuses = [
        "IN_PROGRESS",
        "RESOLVED"
    ]

    if new_status not in allowed_statuses:
        return jsonify({
            "error": "Invalid status",
            "allowed_values": allowed_statuses
        }), 400

    connection = get_db_connection()

    try:
        ticket = connection.execute(
            """
            SELECT ticket_id, status, assigned_to
            FROM tickets
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchone()

        if ticket is None:
            return jsonify({
                "error": "Ticket not found"
            }), 404

        current_status = ticket["status"]

        # Define valid workflow transitions
        valid_transitions = {
            "ASSIGNED": ["IN_PROGRESS"],
            "IN_PROGRESS": ["RESOLVED"]
        }

        if (
            current_status not in valid_transitions
            or new_status not in valid_transitions[current_status]
        ):
            return jsonify({
                "error": f"Invalid status transition: {current_status} → {new_status}"
            }), 400

        # Update ticket
        if new_status == "RESOLVED":
            connection.execute(
                """
                UPDATE tickets
                SET status = ?,
                    resolved_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE ticket_id = ?
                """,
                (new_status, ticket_id)
            )
        else:
            connection.execute(
                """
                UPDATE tickets
                SET status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE ticket_id = ?
                """,
                (new_status, ticket_id)
            )

        # Record history
        connection.execute(
            """
            INSERT INTO ticket_history
            (
                ticket_id,
                old_status,
                new_status,
                changed_by
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                ticket_id,
                current_status,
                new_status,
                changed_by
            )
        )

        connection.commit()

        return jsonify({
            "message": "Ticket status updated successfully",
            "ticket_id": ticket_id,
            "old_status": current_status,
            "new_status": new_status
        }), 200

    except Exception as error:
        connection.rollback()

        return jsonify({
            "error": "Failed to update ticket status",
            "details": str(error)
        }), 500

    finally:
        connection.close()
@ticket_bp.route("/api/tickets/<int:ticket_id>/confirm", methods=["PUT"])
def confirm_ticket(ticket_id):
    data = request.get_json()

    if not data or "user_id" not in data:
        return jsonify({
            "error": "user_id is required"
        }), 400

    user_id = data["user_id"]

    connection = get_db_connection()

    try:
        ticket = connection.execute(
            """
            SELECT ticket_id, status, created_by
            FROM tickets
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchone()

        if ticket is None:
            return jsonify({
                "error": "Ticket not found"
            }), 404

        # Only the employee who created the ticket can confirm it
        if ticket["created_by"] != user_id:
            return jsonify({
                "error": "Only the ticket creator can confirm the ticket"
            }), 403

        # Only RESOLVED tickets can be confirmed
        if ticket["status"] != "RESOLVED":
            return jsonify({
                "error": "Only RESOLVED tickets can be confirmed"
            }), 400

        connection.execute(
            """
            UPDATE tickets
            SET user_confirmed = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        )

        connection.commit()

        return jsonify({
            "message": "Ticket confirmed successfully",
            "ticket_id": ticket_id,
            "user_confirmed": True
        }), 200

    except Exception as error:
        connection.rollback()

        return jsonify({
            "error": "Failed to confirm ticket",
            "details": str(error)
        }), 500

    finally:
        connection.close()
@ticket_bp.route("/api/tickets/<int:ticket_id>/close", methods=["PUT"])
def close_ticket(ticket_id):
    data = request.get_json()

    if not data or "closed_by" not in data:
        return jsonify({
            "error": "closed_by is required"
        }), 400

    closed_by = data["closed_by"]

    connection = get_db_connection()

    try:
        ticket = connection.execute(
            """
            SELECT
                ticket_id,
                status,
                user_confirmed
            FROM tickets
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchone()

        if ticket is None:
            return jsonify({
                "error": "Ticket not found"
            }), 404

        # Ticket must be RESOLVED
        if ticket["status"] != "RESOLVED":
            return jsonify({
                "error": "Only RESOLVED tickets can be closed"
            }), 400

        # Employee confirmation is mandatory
        if ticket["user_confirmed"] != 1:
            return jsonify({
                "error": "Employee confirmation is required before closing the ticket"
            }), 400

        connection.execute(
            """
            UPDATE tickets
            SET status = 'CLOSED',
                closed_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        )

        connection.execute(
            """
            INSERT INTO ticket_history
            (
                ticket_id,
                old_status,
                new_status,
                changed_by
            )
            VALUES (?, 'RESOLVED', 'CLOSED', ?)
            """,
            (ticket_id, closed_by)
        )

        connection.commit()

        return jsonify({
            "message": "Ticket closed successfully",
            "ticket_id": ticket_id,
            "status": "CLOSED"
        }), 200

    except Exception as error:
        connection.rollback()

        return jsonify({
            "error": "Failed to close ticket",
            "details": str(error)
        }), 500

    finally:
        connection.close()
@ticket_bp.route("/agent")
def agent_dashboard():
    connection = get_db_connection()

    tickets = connection.execute(
        """
        SELECT
            t.ticket_id,
            t.title,
            t.description,
            t.category,
            t.priority,
            t.status,
            t.created_at,
            t.assigned_to,
            u.name AS employee_name
        FROM tickets t
        JOIN users u ON t.created_by = u.user_id
        ORDER BY
            CASE t.status
                WHEN 'NEW' THEN 1
                WHEN 'ASSIGNED' THEN 2
                WHEN 'IN_PROGRESS' THEN 3
                WHEN 'RESOLVED' THEN 4
                WHEN 'CLOSED' THEN 5
            END,
            t.ticket_id DESC
        """
    ).fetchall()

    agents = connection.execute(
        """
        SELECT user_id, name
        FROM users
        WHERE role IN ('AGENT', 'ADMIN')
        """
    ).fetchall()

    connection.close()

    return render_template(
        "agent.html",
        tickets=tickets,
        agents=agents
    )