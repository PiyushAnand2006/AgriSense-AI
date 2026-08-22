"""Dashboard aggregation tests — one request, multiple sources, warnings."""


def test_dashboard_aggregates_all_sources(client, auth):
    response = client.get("/api/v1/dashboard", headers=auth["headers"])
    assert response.status_code == 200, response.text
    body = response.json()

    # Crop block (database)
    assert body["crop"]["id"] == "wheat"  # default crop for a fresh user
    assert body["season"] == "RABI"

    # Market block (database / mandi)
    assert body["marketPrice"] > 0
    assert body["marketSource"] in ("mandi-db", "mandi-api")
    assert body["marketTrend"]["direction"] in ("UP", "DOWN", "FLAT")

    # Weather block (external API or local fallback)
    assert body["weather"] is not None
    assert body["weatherSource"] in ("weather-api", "weather-local")

    # Notifications block
    assert body["unreadNotifications"] >= 1

    # Aggregation metadata
    assert isinstance(body["warnings"], list)
    # No ML prediction fields on the dashboard.
    assert "forecastConfidence" not in body
    assert "status" not in body


def test_dashboard_health_score_from_records(client, auth):
    # Log a HIGH severity record -> health score drops to 55.
    client.post(
        "/api/v1/crops/wheat/records",
        json={"recordType": "DISEASE", "name": "Leaf Rust", "severity": "HIGH"},
        headers=auth["headers"],
    )
    body = client.get("/api/v1/dashboard", headers=auth["headers"]).json()
    assert body["healthScore"] == 55
    assert body["healthScoreLabel"] == "Critical"
    assert body["latestRecord"]["name"] == "Leaf Rust"
    assert len(body["healthHistory"]) == 1


def test_dashboard_requires_auth(client):
    assert client.get("/api/v1/dashboard").status_code == 401


def test_dashboard_summary_alias(client, auth):
    # /dashboard/summary kept as an alias of /dashboard.
    alias = client.get("/api/v1/dashboard/summary", headers=auth["headers"])
    assert alias.status_code == 200
    assert alias.json()["crop"]["id"] == "wheat"
