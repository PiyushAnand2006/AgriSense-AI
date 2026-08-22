"""Sell/Hold rule-based decision engine tests (no ML — transparent rules)."""

API = "/api/v1/recommendations/sell-hold"


def _request(client, headers, **overrides):
    payload = {"cropId": "wheat", "marketId": "delhi-azadpur", "quantity": 100, "storageDays": 14}
    payload.update(overrides)
    return client.post(API, json=payload, headers=headers)


def test_sell_hold_decision(client, auth):
    response = _request(client, auth["headers"])
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["recommendation"] in ("SELL", "HOLD")
    assert body["trend"] in ("UPWARD", "DOWNWARD", "FLAT")
    assert body["risk"] in ("LOW", "MEDIUM", "HIGH")
    # Decision math is internally consistent.
    expected_return = round(body["projectedPrice"] - body["currentPrice"] - body["storageCost"], 1)
    assert abs(body["expectedAdditionalReturn"] - expected_return) < 1.5
    # Transparent, labelled output — not a prediction.
    assert body["reason"]
    assert "not financial advice" in body["disclaimer"].lower()
    assert "confidence" not in body
    assert "status" not in body


def test_high_storage_cost_pushes_to_sell(client, auth):
    # Explicit storage cost larger than any plausible trend gain -> SELL.
    body = _request(client, auth["headers"], storageCost=5000).json()
    assert body["recommendation"] == "SELL"
    assert body["expectedAdditionalReturn"] < 0


def test_risk_tolerance_changes_thresholds(client, auth):
    low = _request(client, auth["headers"], riskTolerance="LOW").json()
    high = _request(client, auth["headers"], riskTolerance="HIGH").json()
    # A LOW-risk farmer requires a bigger expected gain to HOLD, so when both
    # get the same inputs LOW can only be more conservative.
    if low["recommendation"] == "HOLD":
        assert high["recommendation"] == "HOLD"


def test_history_is_recorded(client, auth):
    _request(client, auth["headers"])
    history = client.get("/api/v1/recommendations/history", headers=auth["headers"]).json()
    assert history
    assert history[0]["recommendation"] in ("SELL", "HOLD")


def test_validation_rejects_bad_input(client, auth):
    assert _request(client, auth["headers"], storageDays=0).status_code == 422
    assert _request(client, auth["headers"], quantity=-1).status_code == 422
    assert _request(client, auth["headers"], riskTolerance="EXTREME").status_code == 422


def test_unknown_crop_or_market_is_400(client, auth):
    assert _request(client, auth["headers"], cropId="banana").status_code == 400


def test_requires_auth(client):
    assert client.post(
        API, json={"cropId": "wheat", "quantity": 10, "storageDays": 7}
    ).status_code == 401
