# AgriSense AI — Architecture

AgriSense AI is a REST API-driven agricultural information and decision-support
platform. The backend is the central API orchestration layer: it owns the
database, integrates external APIs, normalizes their responses and serves a
single standardized contract to the frontend.

## High-level architecture

```
Frontend (React + TypeScript + Vite)
    |
    | REST + JSON, /api/v1/*, JWT Bearer auth
    v
FastAPI application
    |  middleware stack: CORS -> RequestContext (X-Request-ID,
    |  structured logs) -> RateLimit (auth/assistant/uploads)
    |  exception handlers -> {"error": {code, message, requestId}}
    v
Router layer (app/api/v1/*)      — thin: validate, delegate, serialize
    |
    v
Service layer (app/services/*)   — all business logic
    |                |                |              |
    v                v                v              v
Repository/ORM   External clients   Rules engine   Cache
(SQLAlchemy)     (app/external/*)   (trends,       (Redis or
                  httpx wrapper      sell/hold)     in-memory TTL)
    |                |
    v                v
PostgreSQL /   Open-Meteo (weather) · Mandi feed (prices) ·
SQLite (dev)   Assistant API (optional)
```

## Layer responsibilities

| Layer | Directory | Responsibility |
|---|---|---|
| Routers | `app/api/v1/` | Request/response contracts, Pydantic validation, auth dependencies, HTTP status codes. **No business logic.** |
| Services | `app/services/` | Business logic: market normalization, weather integration + fallback, rule-based sell/hold, dashboard aggregation, knowledge/info services, assistant providers. |
| External clients | `app/external/` | Outbound HTTP via one shared `ExternalHttpClient` (timeout, retry, backoff, logging). Validate and normalize third-party payloads. |
| Middleware | `app/middleware/` | Request correlation IDs + structured logging; fixed-window rate limiting. |
| Models | `app/models/` | SQLAlchemy ORM (users, crops, market prices min/max/modal, health records, listings, notifications, ...). |
| Schemas | `app/schemas/` | Pydantic models, snake_case -> camelCase wire format via `CamelModel`. |
| Core | `app/core/` | Settings, JWT/bcrypt security, cache backends, error types. |

## Key design rules

1. **The frontend never calls third-party APIs.** Weather, mandi and assistant
   integrations live behind the backend. Responses carry a `source` field
   (`weather-api` / `weather-local`, `mandi-api` / `mandi-db`) so consumers
   always know the origin.
2. **Normalized market structure everywhere.** Third-party mandi feeds use
   inconsistent field names; `app/external/mandi_client.py` maps every variant
   to the internal `{min, max, modal} price, unit, source` shape. No frontend
   component is coupled to a provider format.
3. **Graceful degradation for non-critical sources.** If the weather API fails,
   the dashboard returns local seasonal data and adds a warning — it never
   fails entirely.
4. **Centralized errors.** `AppError` subclasses map to a stable envelope:
   `{"error": {"code": "EXTERNAL_SERVICE_UNAVAILABLE", "message": ..., "requestId": ...}}`.
   Stack traces never reach clients.
5. **Correlation.** Every request gets an `X-Request-ID` (echoed if provided)
   returned in the response header and included in every log line.

## Data flow example — market prices

```
GET /api/v1/market/prices?cropId=wheat&sort=price_asc&page=1
  router (validation) -> market_service
    -> cache (markets metadata, 1h TTL)
    -> database: latest MarketPrice rows per crop x market
    -> compute_trends (7/14/30-day % change over recorded history)
    -> PriceSummary responses (normalized, source-labelled)
  -> JSON (camelCase) -> frontend marketService -> MarketPage
```

## Database schema (core tables)

```
users, farmer_profiles          auth + profile
crops, farmer_crops             catalog + per-farmer plantings
markets, market_prices          mandis + daily min/max/modal prices (INR/quintal)
health_records                  farmer-logged disease/pest observations
sell_hold_recommendations       rule-engine history
crop_listings                   marketplace
notifications                   per-user event feed
assistant_conversations/messages assistant persistence
weather_snapshots               persisted weather observations
```

Seeding (`app/db/seed.py`) is idempotent and date-deterministic: 8 crops ×
8 mandis × 120 days of prices, a demo account, sample records and listings.

## Security

- bcrypt password hashing; JWT access tokens (`Authorization: Bearer`).
- Ownership checks on all farmer-owned resources (404 on foreign ids).
- Fixed-window rate limits on `/auth/*` (30/min/IP), `/assistant/*` (20),
  `/uploads` (30).
- Upload validation: MIME sniffing by magic bytes, extension + size caps,
  UUID filenames.
- Weather coordinates validated against India bounds (rejects arbitrary SSRF-ish
  probes); outbound HTTP only to configured base URLs.
- CORS allow-list from settings; secrets only via environment.

## Caching

`app/core/cache.py` provides one interface with two backends:
- `RedisCache` — used when `REDIS_URL` is set and `redis` is installed.
- `MemoryCache` — process-local TTL store (default, zero infrastructure).

Cached: weather responses (30 min), market metadata (1 h). Keys include all
query parameters. Rapidly-changing data is not cached.
