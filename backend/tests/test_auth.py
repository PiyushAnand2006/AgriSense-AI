"""Auth flow tests."""


def test_system_status(client):
    response = client.get("/api/v1/system")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["features"]["marketplace"] is True
    assert body["features"]["diseaseInfo"] is True
    assert "integrations" in body


def test_register_login_me_flow(client):
    from tests.conftest import register_user

    payload = register_user(client)
    assert payload["token"]
    assert payload["user"]["email"].endswith("@example.com")
    assert payload["user"]["profile"]["state"] == "Uttar Pradesh"

    # camelCase contract check
    assert "expiresInDays" in payload
    assert "farmSizeAcres" not in payload["user"] or payload["user"]["farmSizeAcres"] is None


def test_duplicate_register_conflicts(client):
    from tests.conftest import TEST_PASSWORD, register_user

    first = register_user(client)
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Dup", "email": first["user"]["email"], "password": TEST_PASSWORD},
    )
    assert response.status_code == 409


def test_login_wrong_password(client):
    from tests.conftest import TEST_PASSWORD, register_user

    payload = register_user(client)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": payload["user"]["email"], "password": f"wrong-{TEST_PASSWORD}"},
    )
    assert response.status_code == 401


def test_me_requires_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-token"})
    assert response.status_code == 401


def test_login_success(client):
    from tests.conftest import TEST_PASSWORD, register_user

    payload = register_user(client)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": payload["user"]["email"], "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    assert response.json()["token"]
