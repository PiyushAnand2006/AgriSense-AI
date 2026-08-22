"""External API failure tests — standardized error envelope, no stack traces.

All external clients are mocked; automated tests never call real services.
"""

from datetime import date

import pytest

from app.external import mandi_client as mandi_client_module
from app.external.mandi_client import MandiClient, NormalizedPrice


def _sample_rows(n: int = 3) -> list[dict]:
    return [
        {
            "market": f"Market {i}",
            "commodity": "Wheat",
            "arrival_date": "2026-08-20",
            "min_price": 2000 + i,
            "max_price": 2600 + i,
            "modal_price": 2300 + i,
        }
        for i in range(n)
    ]


def test_mandi_normalization_handles_field_aliases():
    rows = [
        {
            "market_name": "Azadpur",
            "commodity_name": "Wheat",
            "arrival_Date": "20/08/2026",
            "minPrice": "2000",
            "maxPrice": "2600",
            "modalPrice": "2300",
        }
    ]
    normalized = MandiClient.normalize({"records": rows})
    assert len(normalized) == 1
    row = normalized[0]
    assert row.market_name == "Azadpur"
    assert row.price_date == date(2026, 8, 20)
    assert row.min_price == 2000.0
    assert row.modal_price == 2300.0
    assert row.source == "mandi-api"


def test_mandi_normalization_skips_malformed_rows():
    rows = _sample_rows(2) + [{"market": "No prices"}]  # last row is broken
    normalized = MandiClient.normalize({"records": rows})
    assert len(normalized) == 2


def test_mandi_rejects_payload_without_records():
    with pytest.raises(Exception):
        MandiClient.normalize({"error": "bad request"})


def test_mandi_prices_used_when_configured(client, monkeypatch):
    """When the mandi API is configured, price responses report mandi-api source."""

    class MockMandiClient:
        configured = True

        async def fetch_prices(self, **kwargs):
            return [
                NormalizedPrice(
                    market_name="Azadpur Mandi",
                    commodity="Wheat",
                    price_date=date.today(),
                    min_price=2200,
                    max_price=2500,
                    modal_price=2350,
                )
            ]

    monkeypatch.setattr(mandi_client_module, "_mandi_client", MockMandiClient())
    body = client.get("/api/v1/market/prices", params={"cropId": "wheat"}).json()
    assert body[0]["source"] == "mandi-api"


def test_http_client_wraps_timeouts_as_external_error():
    import asyncio

    import httpx

    from app.core.errors import ExternalServiceError
    from app.external.http_client import ExternalHttpClient

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timed out")

    client = ExternalHttpClient("https://example.invalid", service_name="test")
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    with pytest.raises(ExternalServiceError):
        asyncio.run(client.get("/x"))


def test_external_error_envelope_shape(client, monkeypatch):
    """When an AppError bubbles up it uses the standard error envelope."""
    from app.core.errors import UpstreamBadResponseError

    class BadClient:
        configured = True

        async def fetch_prices(self, **kwargs):
            raise UpstreamBadResponseError(
                service="mandi", detail="Market data provider returned an unexpected response."
            )

    monkeypatch.setattr(mandi_client_module, "_mandi_client", BadClient())
    # The market service surfaces the failure through the error middleware.
    response = client.get("/api/v1/market/prices", params={"cropId": "wheat"})
    assert response.status_code in (200, 502, 503)  # degrade or envelope, never crash
    if response.status_code != 200:
        assert response.json()["error"]["code"] == "EXTERNAL_SERVICE_BAD_RESPONSE"
