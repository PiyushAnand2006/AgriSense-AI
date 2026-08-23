"""Marketplace listing CRUD + authorization tests."""

API = "/api/v1/listings"


def test_listings_seeded_and_paginated(client):
    body = client.get(API).json()
    assert body["total"] >= 7
    assert body["pageSize"] == 12
    assert all("cropName" in item for item in body["items"])


def test_listing_search_and_filters(client):
    mustard = client.get(API, params={"search": "mustard"}).json()
    assert mustard["total"] >= 1
    assert all("Mustard" in item["cropName"] for item in mustard["items"])

    grade_a = client.get(API, params={"grade": "A"}).json()
    assert all(item["qualityGrade"] == "A" for item in grade_a["items"])


def test_listing_crud_and_ownership(client, auth):
    create = client.post(
        API,
        json={"cropId": "wheat", "quantity": 50, "askingPrice": 2500, "qualityGrade": "B", "location": "Varanasi"},
        headers=auth["headers"],
    )
    assert create.status_code == 201, create.text
    listing = create.json()
    assert listing["cropName"] == "Wheat"
    assert listing["farmerName"] == "Test Farmer"

    # visible in board
    board = client.get(API, params={"search": "Varanasi"}).json()
    assert any(item["id"] == listing["id"] for item in board["items"])

    # owner can update
    patch = client.patch(
        f"{API}/{listing['id']}", json={"askingPrice": 2550, "status": "SOLD"}, headers=auth["headers"]
    )
    assert patch.status_code == 200
    assert patch.json()["askingPrice"] == 2550
    assert patch.json()["status"] == "SOLD"

    # owner can delete
    assert client.delete(f"{API}/{listing['id']}", headers=auth["headers"]).status_code == 204


def test_listing_ownership_enforced(client, auth):
    from tests.conftest import register_user

    create = client.post(
        API, json={"cropId": "moong", "quantity": 10, "askingPrice": 7400}, headers=auth["headers"]
    )
    listing_id = create.json()["id"]

    other = register_user(client)
    other_headers = {"Authorization": f"Bearer {other['token']}"}
    assert client.patch(
        f"{API}/{listing_id}", json={"askingPrice": 1}, headers=other_headers
    ).status_code == 403
    assert client.delete(f"{API}/{listing_id}", headers=other_headers).status_code == 403


def test_assistant_chat_flow(client, auth):
    response = client.post(
        "/api/v1/assistant/chat", json={"message": "wheat price today"}, headers=auth["headers"]
    )
    assert response.status_code == 200
    body = response.json()
    assert body["conversationId"]
    assert "₹" in body["reply"]["content"] or "Demo" in body["reply"]["content"]

    conversations = client.get("/api/v1/assistant/conversations", headers=auth["headers"]).json()
    assert any(c["id"] == body["conversationId"] for c in conversations)

    detail = client.get(f"/api/v1/assistant/conversations/{body['conversationId']}", headers=auth["headers"])
    assert detail.status_code == 200
    messages = detail.json()["messages"]
    assert len(messages) >= 2
    assert messages[0]["role"] == "user"


def test_dashboard_summary(client, auth):
    client.post("/api/v1/crops", json={"cropId": "wheat"}, headers=auth["headers"])
    body = client.get("/api/v1/dashboard/summary", params={"cropId": "wheat"}, headers=auth["headers"]).json()
    assert body["crop"]["id"] == "wheat"
    assert body["season"] == "RABI"
    assert 0 <= body["healthScore"] <= 100
    assert body["marketPrice"] > 0
    assert body["marketTrend"]["direction"] in ("UP", "DOWN", "FLAT")
    assert body["weather"] is not None
    assert isinstance(body["warnings"], list)
    # No prediction-style fields on the dashboard.
    assert "predictedPrice" not in body
    assert "status" not in body
