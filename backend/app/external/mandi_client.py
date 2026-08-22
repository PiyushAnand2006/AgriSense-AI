"""Mandi (agricultural market price) API client.

Integrates with a data.gov.in / AGMARKNET-style mandi price endpoint. The
endpoint and key are configurable (``MANDI_API_URL`` / ``MANDI_API_KEY``).
When the integration is not configured the market service transparently
serves normalized prices from the local database — the response always
carries a ``source`` field so consumers know the origin:

    {"market": ..., "commodity": ..., "date": ..., "minPrice": ...,
     "maxPrice": ..., "modalPrice": ..., "unit": "quintal",
     "source": "mandi-api" | "mandi-db"}

Third-party mandi payloads use inconsistent field names; this client is the
single place where they are validated and normalized to the internal
``NormalizedPrice`` structure.
"""

import logging
from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from app.core.errors import UpstreamBadResponseError
from app.external.http_client import ExternalHttpClient

logger = logging.getLogger("agrisense.external.mandi")

SOURCE_MANDI_API = "mandi-api"
SOURCE_MANDI_DB = "mandi-db"


class NormalizedPrice(BaseModel):
    """The internal, stable representation of one mandi price row."""

    market_id: str = ""
    market_name: str
    crop_id: str = ""
    commodity: str
    price_date: date
    min_price: float = Field(gt=0)
    max_price: float = Field(gt=0)
    modal_price: float = Field(gt=0)
    unit: str = "quintal"
    source: str = SOURCE_MANDI_API


class MandiClient:
    """Client for an AGMARKNET-style price feed."""

    def __init__(self, base_url: str, api_key: str = "") -> None:
        params_key = {"apikey": api_key} if api_key else None
        self._http = ExternalHttpClient(
            base_url,
            api_key="",  # key travels as a query param for this provider
            service_name="mandi",
            headers=None,
        )
        self._api_key = api_key
        self._extra_params = params_key or {}

    @property
    def configured(self) -> bool:
        return bool(self._http.base_url)

    async def fetch_prices(
        self,
        *,
        commodity: str | None = None,
        market: str | None = None,
        state: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 50,
    ) -> list[NormalizedPrice]:
        params: dict[str, Any] = {
            "format": "json",
            "limit": max(1, min(limit, 100)),
            **self._extra_params,
        }
        if commodity:
            params["filters[commodity]"] = commodity
        if market:
            params["filters[market]"] = market
        if state:
            params["filters[state]"] = state
        if date_from:
            params["filters[arrival_date_from]"] = date_from.isoformat()
        if date_to:
            params["filters[arrival_date_to]"] = date_to.isoformat()

        payload = await self._http.get("", params=params)
        return self.normalize(payload)

    @staticmethod
    def normalize(payload: Any) -> list[NormalizedPrice]:
        """Validate + map provider rows (many possible field spellings)."""
        records = payload.get("records") if isinstance(payload, dict) else payload
        if not isinstance(records, list):
            logger.warning("mandi payload failed validation: missing records list")
            raise UpstreamBadResponseError(
                service="mandi", detail="Market data provider returned an unexpected response."
            )

        normalized: list[NormalizedPrice] = []
        for row in records:
            try:
                item = _normalize_row(row)
            except (KeyError, TypeError, ValueError) as exc:
                # Skip malformed individual rows instead of failing the batch.
                logger.warning("skipping malformed mandi row: %s", exc)
                continue
            normalized.append(item)

        if not normalized and records:
            raise UpstreamBadResponseError(
                service="mandi", detail="Market data provider rows could not be parsed."
            )
        return normalized


def _pick(row: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in row and row[name] not in (None, ""):
            return row[name]
    raise KeyError(f"none of {names} present")


def _normalize_row(row: dict[str, Any]) -> NormalizedPrice:
    return NormalizedPrice(
        market_name=str(_pick(row, "market", "market_name", "Market")),
        commodity=str(_pick(row, "commodity", "commodity_name", "Commodity")),
        price_date=_parse_date(_pick(row, "arrival_date", "arrival_Date", "date", "Date")),
        min_price=float(_pick(row, "min_price", "minPrice", "Min Price")),
        max_price=float(_pick(row, "max_price", "maxPrice", "Max Price")),
        modal_price=float(_pick(row, "modal_price", "modalPrice", "Modal Price")),
        source=SOURCE_MANDI_API,
    )


def _parse_date(raw: Any) -> date:
    from datetime import datetime

    text = str(raw).split(" ")[0]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unparseable date: {raw!r}")


_mandi_client: MandiClient | None = None


def get_mandi_client() -> MandiClient:
    global _mandi_client  # noqa: PLW0603
    if _mandi_client is None:
        from app.core.config import get_settings

        settings = get_settings()
        _mandi_client = MandiClient(settings.mandi_api_url, settings.mandi_api_key)
    return _mandi_client


def reset_mandi_client(client: MandiClient | None = None) -> None:
    """Test seam: inject a mock client or reset the singleton."""
    global _mandi_client  # noqa: PLW0603
    _mandi_client = client
