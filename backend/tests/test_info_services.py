"""Disease / pest / treatment / fertilizer information service tests."""

DISEASES = "/api/v1/diseases"
PESTS = "/api/v1/pests"
TREATMENTS = "/api/v1/treatments"
FERTILIZERS = "/api/v1/fertilizers"


def test_list_diseases(client):
    diseases = client.get(DISEASES).json()
    assert len(diseases) >= 10
    leaf_rust = next(d for d in diseases if d["id"] == "leaf-rust")
    assert leaf_rust["name"] == "Leaf Rust"
    assert "wheat" in leaf_rust["cropIds"]
    assert leaf_rust["knowledge"]["symptoms"]
    assert leaf_rust["knowledge"]["prevention"]
    # Educational labelling is mandatory — no unverified agronomic claims.
    assert "not verified" in leaf_rust["knowledge"]["sourceNote"].lower()


def test_disease_detail(client):
    body = client.get(f"{DISEASES}/leaf-rust").json()
    assert body["name"] == "Leaf Rust"
    assert body["knowledge"]["treatment"]
    assert "Educational guidance" in body["knowledge"]["treatment"]


def test_diseases_filtered_by_crop(client):
    wheat = client.get(DISEASES, params={"cropId": "wheat"}).json()
    names = {d["name"] for d in wheat}
    assert {"Leaf Rust", "Powdery Mildew", "Loose Smut"} <= names


def test_crop_diseases_subresource(client):
    wheat = client.get("/api/v1/crops/wheat/diseases").json()
    assert {d["id"] for d in wheat} >= {"leaf-rust", "powdery-mildew", "loose-smut"}


def test_unknown_disease_404(client):
    assert client.get(f"{DISEASES}/does-not-exist").status_code == 404


def test_pests(client):
    pests = client.get(PESTS).json()
    assert len(pests) >= 8
    aphid = next(p for p in pests if p["id"] == "aphid")
    assert aphid["knowledge"]["symptoms"]
    assert aphid["knowledge"]["recommendedAction"]  # camelCase wire format

    wheat_pests = client.get(f"{PESTS}", params={"cropId": "wheat"}).json()
    assert "Aphid" in {p["name"] for p in wheat_pests}


def test_treatments(client):
    treatments = client.get(TREATMENTS).json()
    assert len(treatments) >= 18  # one per disease + pest

    detail = client.get(f"{TREATMENTS}/leaf-rust-treatment").json()
    assert detail["targetType"] == "DISEASE"
    assert detail["targetName"] == "Leaf Rust"
    assert detail["chemicalGuidance"]
    assert detail["organicAlternatives"]

    # No chemical dosage instructions anywhere in treatment guidance.
    for t in treatments:
        lowered = t["chemicalGuidance"].lower()
        assert "ml per" not in lowered and "kg per acre" not in lowered and "g/l" not in lowered


def test_disease_scoped_treatments(client):
    scoped = client.get(f"{DISEASES}/leaf-rust/treatments").json()
    assert len(scoped) == 1
    assert scoped[0]["id"] == "leaf-rust-treatment"

    pest_scoped = client.get(f"{PESTS}/aphid/treatments").json()
    assert pest_scoped[0]["targetType"] == "PEST"


def test_crop_treatments(client):
    wheat = client.get("/api/v1/crops/wheat/treatments").json()
    targets = {t["targetName"] for t in wheat}
    assert "Leaf Rust" in targets and "Aphid" in targets


def test_fertilizer_catalog(client):
    catalog = client.get(FERTILIZERS).json()
    assert len(catalog) >= 6
    entry = next(f for f in catalog if f["id"] == "npk-basal")
    assert entry["growthStages"] == ["SOWING"]
    assert client.get(f"{FERTILIZERS}/npk-basal").status_code == 200
    assert client.get(f"{FERTILIZERS}/nope").status_code == 404


def test_fertilizer_guidance(client, auth):
    response = client.post(
        "/api/v1/fertilizer-guidance",
        json={"cropId": "wheat", "growthStage": "SOWING", "soilCondition": "SANDY"},
        headers=auth["headers"],
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["recommendedFertilizerId"] == "npk-basal"
    assert "leach" in body["soilNote"].lower()
    assert "soil test" in body["guidance"].lower()


def test_fertilizer_guidance_validation(client, auth):
    # Invalid enum values are rejected early with 422.
    bad = client.post(
        "/api/v1/fertilizer-guidance",
        json={"cropId": "wheat", "growthStage": "MIDWAY", "soilCondition": "SANDY"},
        headers=auth["headers"],
    )
    assert bad.status_code == 422
    assert bad.json()["error"]["code"] == "VALIDATION_ERROR"

    # Unknown crop id is a 400 from the route.
    unknown = client.post(
        "/api/v1/fertilizer-guidance",
        json={"cropId": "dragonfruit", "growthStage": "SOWING", "soilCondition": "SANDY"},
        headers=auth["headers"],
    )
    assert unknown.status_code == 400
