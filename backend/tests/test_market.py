"""Market intelligence tests — normalized structure, filters, trends."""

API = "/api/v1/market"


def test_markets_catalog(client):
    markets = client.get(f"{API}/markets").json()
    assert len(markets) >= 8
    assert {"id", "name", "city", "state"} <= set(markets[0])


def test_price_board_normalized_structure(client):
    prices = client.get(f"{API}/prices", params={"limit": 100}).json()
    assert len(prices) >= 8  # 8 crops x 8 markets (paginated)
    first = prices[0]
    # Normalized mandi fields — the standardized contract.
    assert {
        "cropId", "cropName", "marketId", "marketName",
        "minPrice", "maxPrice", "modalPrice", "unit", "source",
        "currentPrice", "previousPrice", "changePct",
        "trend7d", "trend14d", "trend30d",
    } <= set(first)
    assert first["unit"] == "quintal"
    assert first["source"] in ("mandi-api", "mandi-db")
    assert first["minPrice"] <= first["modalPrice"] <= first["maxPrice"]


def test_price_board_filters(client):
    wheat = client.get(f"{API}/prices", params={"cropId": "wheat"}).json()
    assert wheat and all(p["cropId"] == "wheat" for p in wheat)
    assert all(p["currentPrice"] > 0 for p in wheat)

    delhi = client.get(f"{API}/prices", params={"state": "Delhi"}).json()
    assert delhi and all(p["marketId"] == "delhi-azadpur" for p in delhi)


def test_price_board_sort_and_pagination(client):
    asc = client.get(f"{API}/prices", params={"sort": "price_asc", "limit": 5}).json()
    values = [p["currentPrice"] for p in asc]
    assert values == sorted(values)
    assert len(asc) == 5

    page2 = client.get(f"{API}/prices", params={"page": 2, "limit": 5}).json()
    assert [p["id"] if "id" in p else p["cropId"] + p["marketId"] for p in page2]


def test_price_history(client):
    response = client.get(f"{API}/prices/wheat", params={"days": 30}).json()
    assert len(response["history"]) == 30
    assert response["currentPrice"] == response["history"][-1]["modalPrice"]
    point = response["history"][0]
    assert {"date", "minPrice", "maxPrice", "modalPrice", "unit"} <= set(point)
    assert response["trends"]["trend7d"] != 0 or response["trends"]["trend30d"] != 0


def test_market_trend_is_rule_computed(client):
    body = client.get(f"{API}/trends/wheat", params={"days": 30}).json()
    assert body["direction"] in ("UP", "DOWN", "FLAT")
    assert body["days"] == 30
    # Trend is computed from actual history, not forecast.
    expected_pct = round(
        (body["currentPrice"] - body["startPrice"]) / body["startPrice"] * 100, 2
    )
    assert body["changePct"] == expected_pct
    assert "not a price forecast" in body["note"]
    # No prediction-style fields anywhere.
    assert "confidence" not in body
    assert "status" not in body


def test_unknown_crop_404(client):
    assert client.get(f"{API}/prices/banana").status_code == 404
    assert client.get(f"{API}/trends/banana").status_code == 404
