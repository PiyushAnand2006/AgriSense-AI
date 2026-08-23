"""Upload security + farmer-logged health record tests.

Farmers browse disease/pest information and log their own field
observations (optionally with a photo).
"""

from tests.conftest import PNG_BYTES


def test_upload_validates_mime_type(client, auth):
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        headers=auth["headers"],
    )
    assert response.status_code == 415


def test_upload_validates_content(client, auth):
    # JPEG content-type but PNG bytes -> rejected
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("fake.png", PNG_BYTES, "image/jpeg")},
        headers=auth["headers"],
    )
    assert response.status_code == 415


def test_upload_and_log_record_flow(client, auth):
    upload = client.post(
        "/api/v1/uploads",
        files={"file": ("leaf.png", PNG_BYTES, "image/png")},
        headers=auth["headers"],
    )
    assert upload.status_code == 200, upload.text
    image_url = upload.json()["url"]

    # Log a farmer-observed disease record referencing the uploaded photo.
    response = client.post(
        "/api/v1/crops/wheat/records",
        json={
            "recordType": "DISEASE",
            "name": "Leaf Rust",
            "severity": "MODERATE",
            "imageUrl": image_url,
            "notes": "Spotted during morning scouting.",
        },
        headers=auth["headers"],
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["cropName"] == "Wheat"
    assert body["recordType"] == "DISEASE"
    assert body["severity"] == "MODERATE"
    assert body["imageUrl"] == image_url
    # The record is a plain observation, not a prediction.
    assert "confidence" not in body
    assert "status" not in body

    # history contains the record
    history = client.get("/api/v1/crops/wheat/records", headers=auth["headers"]).json()
    assert any(item["id"] == body["id"] for item in history)

    # a notification was generated
    notifications = client.get("/api/v1/notifications", headers=auth["headers"]).json()
    assert notifications["unreadCount"] >= 2  # welcome + record logged


def test_record_types_and_isolation(client, auth):
    for record_type in ("DISEASE", "PEST"):
        response = client.post(
            "/api/v1/crops/moong/records",
            json={"recordType": record_type, "name": "Whitefly", "severity": "LOW"},
            headers=auth["headers"],
        )
        assert response.status_code == 201

    filtered = client.get(
        "/api/v1/crops/moong/records", params={"recordType": "PEST"}, headers=auth["headers"]
    ).json()
    assert all(r["recordType"] == "PEST" for r in filtered)

    # Another user cannot see these records.
    from tests.conftest import register_user

    other = register_user(client)
    other_headers = {"Authorization": f"Bearer {other['token']}"}
    other_records = client.get("/api/v1/crops/moong/records", headers=other_headers).json()
    assert other_records == []


def test_record_validation(client, auth):
    # Invalid record type / severity rejected with 422.
    bad = client.post(
        "/api/v1/crops/wheat/records",
        json={"recordType": "VIRUS", "name": "Something", "severity": "LOW"},
        headers=auth["headers"],
    )
    assert bad.status_code == 422
    assert bad.json()["error"]["code"] == "VALIDATION_ERROR"

    # Unknown crop is a 404.
    missing_crop = client.post(
        "/api/v1/crops/banana/records",
        json={"recordType": "DISEASE", "name": "Leaf Spot", "severity": "LOW"},
        headers=auth["headers"],
    )
    assert missing_crop.status_code == 404


def test_records_require_auth(client):
    assert client.post(
        "/api/v1/crops/wheat/records",
        json={"recordType": "DISEASE", "name": "Leaf Rust", "severity": "LOW"},
    ).status_code == 401
