# External API Integrations

All outbound integrations live in `backend/app/external/` and share one HTTP
wrapper (`http_client.py`): 8-second timeout, 2 retries with backoff on
transient failures, structured latency logging, and consistent
`ExternalServiceError` signalling. The frontend never calls any of these
directly.

| Integration | Client | Config | Fallback when unavailable |
|---|---|---|---|
| Weather | `weather_client.py` | `WEATHER_API_URL`, `WEATHER_API_KEY` | Local deterministic seasonal data (`source: "weather-local"`) |
| Mandi prices | `mandi_client.py` | `MANDI_API_URL`, `MANDI_API_KEY` | Seeded database prices (`source: "mandi-db"`) |
| Assistant | `assistant_client.py` | `ASSISTANT_API_URL`, `ASSISTANT_API_KEY` | Built-in rule-based assistant (`status: "RULE_BASED"`) |

## Weather — Open-Meteo (default, no key required)

- Endpoint: `GET {WEATHER_API_URL}/forecast?latitude=&longitude=&daily=...`
- Requested fields: daily max/min temperature, mean humidity, max precipitation
  probability, max wind speed, weather code.
- Normalization (`WeatherClient.normalize`): mean of max/min temperature,
  `weather_code` + rain probability mapped to a condition word
  (Sunny / Mostly Sunny / Cloudy / Foggy / Showers / Rain).
- Coordinate validation: requests are restricted to India bounds
  (lat 6–37, lon 68–97.5); anything else is a 422.
- Caching: 30-minute TTL, key includes coordinates.

To point at another Open-Meteo-compatible provider, set `WEATHER_API_URL`
(and `WEATHER_API_KEY` if required — sent as `Authorization: Bearer`).

## Mandi prices — AGMARKNET-style feed (optional)

- Endpoint: `GET {MANDI_API_URL}?format=json&limit=&apikey=&filters[...]=`
  with optional commodity / market / state / arrival-date filters.
- Third-party rows arrive with inconsistent field spellings; the normalizer
  accepts the common variants:
  - market: `market` / `market_name` / `Market`
  - commodity: `commodity` / `commodity_name` / `Commodity`
  - date: `arrival_date` / `arrival_Date` / `date` / `Date` (`Y-m-d`, `d/m/Y`, `d-m-Y`)
  - prices: `min_price|minPrice|Min Price`, `max_price|maxPrice|Max Price`,
    `modal_price|modalPrice|Modal Price`
- Malformed rows are skipped (logged); a payload with no records or zero
  parseable rows raises `UpstreamBadResponseError` (502 envelope).
- Internal normalized shape (also the wire format):

```json
{
  "market": "Azadpur Mandi",
  "commodity": "Wheat",
  "date": "2026-08-20",
  "min_price": 2200,
  "max_price": 2500,
  "modal_price": 2350,
  "unit": "quintal",
  "source": "mandi-api"
}
```

When `MANDI_API_URL` is empty, market endpoints serve the seeded database and
label every response `source: "mandi-db"`.

## Assistant — external conversational API (optional)

- Endpoint: `POST {ASSISTANT_API_URL}/chat` with
  `{message, system, history[]}` (history capped to 8 turns).
- Reply extraction accepts `reply` / `response` / `answer` / `text` /
  `message` or an OpenAI-style `choices[0].message.content`.
- The API key stays backend-only (Bearer header) and is never exposed to the
  frontend. On failure the service falls back to the rule-based assistant and
  reports `status: "RULE_BASED"`.

## Testing

Automated tests never call real third-party services. The clients expose
module-level singletons with reset seams
(`reset_weather_client`, `reset_mandi_client`, `reset_assistant_client`)
and the test suite injects mocks (see `tests/test_weather.py`,
`tests/test_external_errors.py`).
