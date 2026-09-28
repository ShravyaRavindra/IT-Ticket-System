def test_create_ticket(client):

    # Create an employee first
    client.application.config["TESTING"] = True

    from app.database import get_db_connection

    with client.application.app_context():

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO users
            (name, email, password, role)
            VALUES (?, ?, ?, ?)
            """,
            (
                "Test Employee",
                "testemployee@example.com",
                "test123",
                "EMPLOYEE"
            )
        )

        connection.commit()

        user_id = connection.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = ?
            """,
            ("testemployee@example.com",)
        ).fetchone()["user_id"]

        connection.close()

    response = client.post(
        "/api/tickets",
        json={
            "title": "Test WiFi Issue",
            "description": "WiFi is not working",
            "category": "NETWORK",
            "priority": "HIGH",
            "created_by": user_id
        }
    )

    assert response.status_code in (200, 201)

    data = response.get_json()

    assert "ticket_id" in data