# API Reference (v1)

Base URL: `/api/v1` · Interactive docs: `/docs` (Swagger) and `/redoc`.
Wire format is JSON with camelCase keys. Authentication uses
`Authorization: Bearer <token>` unless noted.

Error envelope (all standardized errors):

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "storageDays: Input should be greater than or equal to 1",
    "requestId": "b1a3f572b6b64418"
  }
}
```

Codes: `VALIDATION_ERROR` 422 · `RATE_LIMITED` 429 · `NOT_FOUND` 404 ·
`EXTERNAL_SERVICE_UNAVAILABLE` 503 · `EXTERNAL_SERVICE_TIMEOUT` 504 ·
`EXTERNAL_SERVICE_BAD_RESPONSE` 502 · `INTERNAL_ERROR` 500.
Every response carries an `X-Request-ID` header.

Rate limits (fixed window, per IP): `/auth/*` 30/min · `/assistant/*` 20/min ·
`/uploads` 30/min. Configurable via env.

## System & health

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/system` | — | Feature flags + active integrations |
| GET | `/health` | — | Liveness (version) |
| GET | `/health/live` | — | Liveness |
| GET | `/health/ready` | — | Readiness (database round-trip) |

## Auth

| Method | Path | Auth | Body | Notes |
|---|---|---|---|---|
| POST | `/auth/register` | — | name, email, password (≥8), village?, district?, state? | 201 → token + user; 409 duplicate |
| POST | `/auth/login` | — | email, password | 200 → token; 401 bad credentials |
| POST | `/auth/logout` | Bearer | — | always succeeds |
| GET | `/auth/me` | Bearer | — | current user + profile |
| PATCH | `/auth/me` | Bearer | name?, phone?, village?, district?, state?, farmSizeAcres? | updated user |

## Seasons (database-driven)

| Method | Path | Description |
|---|---|---|
| GET | `/seasons` | seasons that have crops registered |
| GET | `/seasons/{season}` | detail (404 for unknown, e.g. `kharif`) |
| GET | `/seasons/{season}/crops` | crops for the season + growing calendar fields |

## Crops

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/crops?season=&search=` | — | catalog |
| GET | `/crops/mine?status_filter=` | Bearer | the farmer's plantings |
| POST | `/crops` | Bearer | add planting (400 unknown cropId) |
| GET | `/crops/{crop_id}` | — | catalog detail |
| PATCH | `/crops/{planting_id}` | Bearer | update own planting (404 foreign) |
| DELETE | `/crops/{planting_id}` | Bearer | delete own planting → 204 |

Crop-scoped information (all public):

| Path | Description |
|---|---|
| `GET /crops/{crop_id}/diseases` | common diseases (symptoms, management, prevention) |
| `GET /crops/{crop_id}/pests` | common pests |
| `GET /crops/{crop_id}/treatments` | treatment guidance for the crop's diseases + pests |
| `GET /crops/{crop_id}/fertilizers` | fertilizer catalog |

Health records (farmer-logged observations, no inference):

| Method | Path | Auth | Body |
|---|---|---|---|
| GET | `/crops/{crop_id}/records?recordType=` | Bearer | — |
| POST | `/crops/{crop_id}/records` | Bearer | recordType (DISEASE\|PEST), name, severity (LOW\|MODERATE\|HIGH), imageUrl?, notes? → 201 |

## Diseases / pests / treatments

| Method | Path | Description |
|---|---|---|
| GET | `/diseases?cropId=` | all diseases, optional crop filter |
| GET | `/diseases/{disease_id}` | detail incl. educational knowledge |
| GET | `/diseases/{disease_id}/treatments` | educational treatment guidance |
| GET | `/pests?cropId=` | all pests, optional crop filter |
| GET | `/pests/{pest_id}` | detail |
| GET | `/pests/{pest_id}/treatments` | treatment guidance |
| GET | `/treatments` | full catalog |
| GET | `/treatments/{treatment_id}` | detail |

All guidance fields carry `sourceNote: "Educational information — not verified
agricultural guidance."` No chemical dosages are served.

## Fertilizers

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/fertilizers` | — | category catalog (growth stages per entry) |
| GET | `/fertilizers/{id}` | — | detail |
| POST | `/fertilizer-guidance` | Bearer | cropId, growthStage, soilCondition (enums), npk? → rule-based guidance (422 on bad enums) |

## Market (normalized mandi structure)

Every price object: `cropId, cropName, marketId, marketName, currentPrice,
minPrice, maxPrice, modalPrice, unit ("quintal"), previousPrice, change,
changePct, trend7d/14d/30d, lastUpdated, source ("mandi-api" | "mandi-db")`.

| Method | Path | Query |
|---|---|---|
| GET | `/market/markets` | — (cached 1 h) |
| GET | `/market/prices` | cropId?, marketId?, state?, search?, sort (name\|price_asc\|price_desc\|change_desc), page (≥1), limit (1–100) |
| GET | `/market/prices/{crop_id}` | marketId?, days (7–365) → history points |
| GET | `/market/trends/{crop_id}` | marketId?, days (7–120) → direction, changePct, trend windows, history. **Computed from recorded prices — not a forecast.** |

## Weather (backend-owned integration)

| Method | Path | Query |
|---|---|---|
| GET | `/weather/current` | lat?, lon? (validated against India bounds, else 422) |
| GET | `/weather/forecast` | lat?, lon?, days (1–15) |
| GET | `/weather/location` | lat, lon |

Response: `{location, lat, lon, today, forecast[], alerts[], source}` with
`source: "weather-api" | "weather-local"` (cached 30 min).

## Recommendations (rule-based decision support)

| Method | Path | Auth | Body |
|---|---|---|---|
| POST | `/recommendations/sell-hold` | Bearer | cropId, marketId?, quantity (0–100000), storageDays (1–180), storageCost?, riskTolerance (LOW\|MEDIUM\|HIGH) |
| GET | `/recommendations/history?limit=` | Bearer | — |

Response: `{recommendation (SELL|HOLD), reason, trend (UPWARD|DOWNWARD|FLAT),
trendChangePct, projectedPrice, storageCost, expectedAdditionalReturn, risk,
disclaimer}`. Thresholds: LOW risk requires +2% expected gain to HOLD,
MEDIUM +0.5%, HIGH 0%. Projection is trend extrapolation capped at ±20%.

## Dashboard (aggregation)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/dashboard?cropId=` | Bearer | crop + health score + market price & trend + weather + notifications in one call |
| GET | `/dashboard/summary` | Bearer | alias |

Partial failures of non-critical sources appear in `warnings[]`.

## Marketplace

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/listings?search=&cropId=&grade=&status=&maxPrice=&sort=&page=&pageSize=` | — | paginated `Page<ListingOut>` |
| POST | `/listings` | Bearer | cropId, quantity, unit, askingPrice, qualityGrade?, location? → 201 |
| GET | `/listings/{id}` | — | detail |
| PATCH | `/listings/{id}` | Bearer | own listings only (403 foreign) |
| DELETE | `/listings/{id}` | Bearer | own listings only → 204 |

## Assistant

| Method | Path | Auth | Body |
|---|---|---|---|
| POST | `/assistant/chat` | Bearer | message, conversationId? → `{conversationId, reply, status: "RULE_BASED" \| "EXTERNAL_API"}` |
| GET | `/assistant/conversations` | Bearer | last 30 |
| GET | `/assistant/conversations/{id}` | Bearer | full thread (404 foreign) |

## Notifications

| Method | Path | Auth |
|---|---|---|
| GET | `/notifications?unreadOnly=&limit=` | Bearer |
| PATCH | `/notifications/{id}/read` | Bearer |
| PATCH | `/notifications/read-all` | Bearer |

## Uploads

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/uploads` (multipart `file`) | Bearer | JPEG/PNG/WebP only (magic-byte sniffed), ≤8 MB → `{url}` |

Files are stored with generated UUID filenames and served from `/uploads`.
There is **no ML inference attached to uploads** — images reference
farmer-logged health records.
