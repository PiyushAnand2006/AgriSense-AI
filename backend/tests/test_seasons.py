"""Season endpoint tests — database-driven season catalog."""

API = "/api/v1/seasons"


def test_list_seasons(client):
    seasons = client.get(API).json()
    ids = {s["id"] for s in seasons}
    assert {"rabi", "kharif", "zaid"} <= ids
    assert all("name" in s and "label" in s for s in seasons)


def test_season_detail(client):
    rabi = client.get(f"{API}/rabi").json()
    assert rabi["id"] == "rabi"
    assert rabi["name"] == "Rabi"

    kharif = client.get(f"{API}/kharif").json()
    assert kharif["id"] == "kharif"
    assert "Kharif" in kharif["name"]


def test_unknown_season_404(client):
    assert client.get(f"{API}/monsoon-extra").status_code == 404


def test_season_crops(client):
    body = client.get(f"{API}/rabi/crops").json()
    assert body["season"]["id"] == "rabi"
    crop_ids = {c["id"] for c in body["crops"]}
    assert {"wheat", "chickpea", "mustard", "potato"} <= crop_ids
    assert all(c["season"] == "RABI" for c in body["crops"])

    kharif = client.get(f"{API}/kharif/crops").json()
    assert {"rice", "maize", "cotton", "pigeonpeas"} <= {c["id"] for c in kharif["crops"]}

    zaid = client.get(f"{API}/zaid/crops").json()
    assert {"watermelon", "cucumber", "muskmelon", "moong"} <= {c["id"] for c in zaid["crops"]}


def test_season_crops_includes_growing_info(client):
    wheat = next(c for c in client.get(f"{API}/rabi/crops").json()["crops"] if c["id"] == "wheat")
    assert wheat["growingPeriodDays"] == 150
    assert wheat["sowingWindow"]
    assert wheat["harvestWindow"]
