def test_create_ticket_missing_title(client):

    response = client.post(
        "/api/tickets",
        json={
            "description": "WiFi is not working",
            "category": "NETWORK",
            "priority": "HIGH",
            "created_by": 1
        }
    )

    assert response.status_code in (400, 422)