"""Crop catalog + farmer crop CRUD tests."""

API = "/api/v1/crops"


def test_catalog_lists_all_season_crops(client):
    crops = client.get(API).json()
    ids = {c["id"] for c in crops}
    assert {"wheat", "chickpea", "mustard", "potato", "watermelon", "cucumber", "muskmelon", "moong"} <= ids
    assert all(c["season"] in ("RABI", "ZAID") for c in crops)


def test_season_filter(client):
    rabi = client.get(API, params={"season": "RABI"}).json()
    zaid = client.get(API, params={"season": "ZAID"}).json()
    assert {c["id"] for c in rabi} == {"wheat", "chickpea", "mustard", "potato"}
    assert {c["id"] for c in zaid} == {"watermelon", "cucumber", "muskmelon", "moong"}


def test_farmer_crop_crud(client, auth):
    # create
    response = client.post(
        API,
        json={"cropId": "wheat", "farmSize": 2.0, "location": "Baragaon"},
        headers=auth["headers"],
    )
    assert response.status_code == 201, response.text
    planting = response.json()
    assert planting["cropId"] == "wheat"
    assert planting["season"] == "RABI"
    assert planting["crop"]["name"] == "Wheat"
    assert planting["status"] == "ACTIVE"

    # mine
    mine = client.get(f"{API}/mine", headers=auth["headers"]).json()
    assert any(p["id"] == planting["id"] for p in mine)

    # update
    response = client.patch(
        f"{API}/{planting['id']}", json={"farmSize": 3.5}, headers=auth["headers"]
    )
    assert response.status_code == 200
    assert response.json()["farmSize"] == 3.5

    # crop-scoped information sub-resources work
    assert client.get(f"{API}/wheat/diseases").status_code == 200
    assert client.get(f"{API}/wheat/pests").status_code == 200
    assert client.get(f"{API}/wheat/treatments").status_code == 200
    assert client.get(f"{API}/wheat/fertilizers").status_code == 200

    # delete
    assert client.delete(f"{API}/{planting['id']}", headers=auth["headers"]).status_code == 204
    mine = client.get(f"{API}/mine", headers=auth["headers"]).json()
    assert all(p["id"] != planting["id"] for p in mine)


def test_create_with_unknown_crop_fails(client, auth):
    response = client.post(API, json={"cropId": "banana"}, headers=auth["headers"])
    assert response.status_code == 400


def test_planting_isolation_between_users(client, auth):
    from tests.conftest import register_user

    response = client.post(API, json={"cropId": "moong"}, headers=auth["headers"])
    planting_id = response.json()["id"]

    other = register_user(client)
    other_headers = {"Authorization": f"Bearer {other['token']}"}
    assert client.patch(
        f"{API}/{planting_id}", json={"farmSize": 9}, headers=other_headers
    ).status_code == 404
