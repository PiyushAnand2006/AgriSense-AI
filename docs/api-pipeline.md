# API Pipelines — End-to-End Data Flows

This document walks through the six canonical request lifecycles in AgriSense
AI. Each one demonstrates a layer of the architecture: routing, validation,
authentication, service logic, database, external APIs, transformation,
caching, error handling, logging and the standardized response.

---

## 1. Frontend → Backend → Database

**User opens the crop catalog (Rabi season).**

```
React CropsPage
  -> seasonService.cropsBySeasonValue("RABI")
  -> GET /api/v1/seasons/rabi/crops
       |
       v
  router seasons.season_crops       (validates path param)
       -> knowledge.SEASONS metadata + SQLAlchemy query
          SELECT * FROM crops WHERE season = 'RABI' ORDER BY name
       -> [CropOut] (camelCase: growingPeriodDays, sowingWindow, ...)
       v
JSON response -> React renders catalog cards
```

Notes:
- The frontend never hard-codes the crop list — it is database-driven.
- Growing calendar fields (growing period, sowing/harvest windows) come from
  the `crops` table.

## 2. Frontend → Backend → External API → Frontend

**User opens the Weather page.**

```
React WeatherPage
  -> weatherService.current(lat?, lon?)
  -> GET /api/v1/weather/current?lat=25.32&lon=82.98
       |
       v
  router weather.current_weather   (Query validation: lat/lon ranges)
       -> weather_service.get_weather()
           1. cache lookup (key includes lat/lon/days, TTL 30 min)
           2. MISS -> WeatherClient.fetch_forecast()
                -> shared ExternalHttpClient (timeout 8s, 2 retries, logs)
                -> GET https://api.open-meteo.com/v1/forecast?...
           3. WeatherClient.normalize() — validate payload, map field names,
              derive condition text from weather codes
           4. cache response (camelCase JSON)
       -> WeatherResponse { location, today, forecast[], alerts[], source }
       v
JSON -> React renders today card, alerts, 7-day strip
```

Failure path: if the provider fails after retries, the service falls back to
deterministic local seasonal data and the response says
`source: "weather-local"` — the UI labels it accordingly.

## 3. Dashboard API aggregation

**User opens the Dashboard. One request powers the whole page.**

```
React DashboardPage
  -> GET /api/v1/dashboard
       |
       v
  dashboard_service.build_dashboard(db, user)
       |            |             |              |
       v            v             v              v
   crops/health  market prices  weather       notifications
   (database)    (database +    (external     (database)
   health score  trend rules)    API + cache,
   from records                 fallback)
       |
       v
  DashboardSummary {
    crop, healthScore, latestRecord,
    marketPrice, marketSource, marketTrend,
    weather, weatherSource,
    recommendation, unreadNotifications,
    warnings[]     <- e.g. "Weather service unavailable — showing local
                        seasonal estimate."
  }
```

Non-critical source failures are collected into `warnings` instead of failing
the response.

## 4. Authentication flow

```
Register:
POST /api/v1/auth/register {name, email, password, ...}
  -> rate limit check (30/min/IP)
  -> bcrypt hash -> INSERT users + farmer_profiles
  -> JWT (HS256, JWT_SECRET, 7-day expiry)
  <- {token, tokenType: "bearer", expiresInDays, user}

Every protected request:
  Authorization: Bearer <token>
  -> get_current_user dependency: decode JWT -> load user
  -> request.state.user_id (surfaced in the request log line)

Login failure: 401 with WWW-Authenticate: Bearer
Foreign resources: e.g. PATCH /crops/{other-users-planting} -> 404
```

## 5. Error flow

**A third-party API is down.**

```
GET /api/v1/weather/current
  -> ExternalHttpClient: timeout -> retry x2 (backoff) -> still failing
  -> raises ExternalServiceError(service="weather")
  -> weather service: non-critical -> local fallback + warning
  <- 200 with source: "weather-local"

For critical sources (none today by design) the centralized handler returns:

  503 {
    "error": {
      "code": "EXTERNAL_SERVICE_UNAVAILABLE",
      "message": "weather service is temporarily unavailable.",
      "requestId": "b1a3f572b6b64418"
    }
  }
```

Other standardized codes: `VALIDATION_ERROR` (422), `RATE_LIMITED` (429),
`EXTERNAL_SERVICE_TIMEOUT` (504), `EXTERNAL_SERVICE_BAD_RESPONSE` (502),
`NOT_FOUND` (404), `INTERNAL_ERROR` (500). No stack traces are ever exposed.

## 6. Cached external API flow

```
First request (cache MISS):
  GET /api/v1/weather/current?lat=..&lon=..
    -> get_cache() -> MISS
    -> external call (latency logged: "external call service=weather ...")
    -> normalize -> cache.set(key, payload, ttl=1800)
    <- 200 fresh data

Second request within TTL:
    -> get_cache() -> HIT
    <- 200 (no outbound call; X-Request-ID still unique per request)

Cache backends:
  REDIS_URL set + redis installed -> RedisCache (shared across workers)
  otherwise                        -> MemoryCache (process-local)
Keys always include the query parameters (lat, lon, days).
```

---

## Bonus: Sell/Hold decision pipeline (rules, not ML)

```
POST /api/v1/recommendations/sell-hold
  {cropId, marketId, quantity, storageDays, riskTolerance}
       |
       v
  recommendation_service.compute_sell_hold()
    1. load current modal price + 90-day recorded history (database)
    2. trends = 7/14/30-day % change (rule computation)
    3. projected price = trend extrapolation, capped ±20%
    4. expected_return = projected - current - storage_cost
    5. HOLD if expected_return% > threshold(LOW=2%, MEDIUM=0.5%, HIGH=0%)
       else SELL
    6. risk label from horizon + trend flatness
    7. persist record + notification
       v
  SellHoldResult {recommendation, reason, trend, projectedPrice,
                  storageCost, expectedAdditionalReturn, risk,
                  disclaimer: "Decision-support rule — not financial advice."}
```

Every step is transparent and documented — there is no model confidence or
opaque score.
