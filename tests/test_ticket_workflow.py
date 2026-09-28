from app.database import get_db_connection


def create_user(client, name, email, role):
    with client.application.app_context():
        connection = get_db_connection()

        cursor = connection.execute(
            """
            INSERT INTO users
            (name, email, password, role)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, "test123", role)
        )

        connection.commit()
        user_id = cursor.lastrowid
        connection.close()

        return user_id


def test_complete_ticket_workflow(client):

    # -------------------------------------------------
    # 1. Create employee and agent
    # -------------------------------------------------

    employee_id = create_user(
        client,
        "Test Employee",
        "employee@test.com",
        "EMPLOYEE"
    )

    agent_id = create_user(
        client,
        "Test Agent",
        "agent@test.com",
        "AGENT"
    )

    # -------------------------------------------------
    # 2. Employee creates ticket
    # -------------------------------------------------

    response = client.post(
        "/api/tickets",
        json={
            "title": "VPN not working",
            "description": "Unable to connect to company VPN",
            "category": "NETWORK",
            "priority": "HIGH",
            "created_by": employee_id
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    ticket_id = data["ticket_id"]

    assert data["status"] == "NEW"

    # -------------------------------------------------
    # 3. Agent gets assigned
    # -------------------------------------------------

    response = client.put(
        f"/api/tickets/{ticket_id}/assign",
        json={
            "assigned_to": agent_id
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "ASSIGNED"
    assert data["assigned_to"] == agent_id

    # -------------------------------------------------
    # 4. Agent starts working
    # -------------------------------------------------

    response = client.put(
        f"/api/tickets/{ticket_id}/status",
        json={
            "status": "IN_PROGRESS",
            "changed_by": agent_id
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "IN_PROGRESS"

    # -------------------------------------------------
    # 5. Agent resolves ticket
    # -------------------------------------------------

    response = client.put(
        f"/api/tickets/{ticket_id}/status",
        json={
            "status": "RESOLVED",
            "changed_by": agent_id
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "RESOLVED"

    # -------------------------------------------------
    # 6. Employee confirms resolution
    # -------------------------------------------------

    response = client.put(
        f"/api/tickets/{ticket_id}/confirm",
        json={
            "user_id": employee_id
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["user_confirmed"] is True

    # -------------------------------------------------
    # 7. Agent closes ticket
    # -------------------------------------------------

    response = client.put(
        f"/api/tickets/{ticket_id}/close",
        json={
            "closed_by": agent_id
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "CLOSED"

    # -------------------------------------------------
    # 8. Verify final database state
    # -------------------------------------------------

    with client.application.app_context():

        connection = get_db_connection()

        ticket = connection.execute(
            """
            SELECT
                status,
                assigned_to,
                user_confirmed,
                resolved_at,
                closed_at
            FROM tickets
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchone()

        assert ticket is not None
        assert ticket["status"] == "CLOSED"
        assert ticket["assigned_to"] == agent_id
        assert ticket["user_confirmed"] == 1
        assert ticket["resolved_at"] is not None
        assert ticket["closed_at"] is not None

        connection.close()