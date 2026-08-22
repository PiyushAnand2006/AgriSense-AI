"""Weather service — external API integration with cache + local fallback.

Pipeline:

    GET /api/v1/weather/current?lat=&lon=
        -> cache lookup (30 min TTL)
        -> MISS -> weather client -> external API
        -> normalize into WeatherDay structures
        -> cache
        -> response (source: "weather-api")

If the external API is unavailable the service falls back to deterministic
local seasonal data (source: "weather-local") instead of failing — the
response always states where the data came from.
"""

import hashlib
import logging
import math
from datetime import date, timedelta

from app.core.cache import WEATHER_TTL, cache_key, get_cache
from app.core.errors import ExternalServiceError
from app.schemas.weather import WeatherAlert, WeatherDay, WeatherResponse

logger = logging.getLogger("agrisense.weather")

SOURCE_API = "weather-api"
SOURCE_LOCAL = "weather-local"

DEFAULT_LAT, DEFAULT_LON = 25.32, 82.98  # Varanasi region, India


# --- Local deterministic fallback ------------------------------------------------


def _hash_float(key: str) -> float:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def _day_weather(day: date) -> WeatherDay:
    doy = day.timetuple().tm_yday
    # North-India-like seasonal temperature curve, 16C (Jan) to 39C (Jun).
    seasonal = 27.5 + 11.5 * math.sin((doy - 105) / 365 * 2 * math.pi)
    temp = seasonal + (_hash_float(f"t{day}") - 0.5) * 5
    humidity = 35 + _hash_float(f"h{day}") * 50
    rain_prob = round(_hash_float(f"r{day}") * 100, 0)
    # Monsoon months get a rain boost.
    if 6 <= day.month <= 9:
        rain_prob = min(95, rain_prob + 30)
    wind = 5 + _hash_float(f"w{day}") * 20
    if rain_prob >= 65:
        condition = "Rain"
    elif rain_prob >= 40:
        condition = "Cloudy"
    else:
        condition = "Sunny"
    return WeatherDay(
        date=day,
        temperature_c=round(temp, 1),
        humidity_pct=round(humidity, 0),
        rain_probability=rain_prob,
        wind_kph=round(wind, 1),
        condition=condition,
    )


def _local_forecast(days: int = 8) -> list[WeatherDay]:
    today = date.today()
    return [_day_weather(today + timedelta(days=offset)) for offset in range(days)]


# --- Alerts (agricultural interpretation of forecast data) -----------------------


def _build_alerts(days: list[WeatherDay]) -> list[WeatherAlert]:
    alerts: list[WeatherAlert] = []
    today = days[0]
    if today.rain_probability >= 70:
        alerts.append(
            WeatherAlert(
                severity="WARNING",
                title="Heavy rain likely",
                message="High rain probability today. Avoid pesticide spraying and delay irrigation.",
            )
        )
    if today.temperature_c >= 40:
        alerts.append(
            WeatherAlert(
                severity="CRITICAL",
                title="Heat stress risk",
                message="Very high temperatures. Irrigate early morning or evening to reduce crop stress.",
            )
        )
    if today.humidity_pct <= 30 and today.temperature_c >= 33:
        alerts.append(
            WeatherAlert(
                severity="WARNING",
                title="Dry conditions",
                message="Low humidity with high temperature increases pest and mite pressure. Scout fields.",
            )
        )
    rainy_week = sum(1 for d in days if d.rain_probability >= 60)
    if rainy_week >= 3:
        alerts.append(
            WeatherAlert(
                severity="INFO",
                title="Wet week ahead",
                message="Multiple rainy days forecast. Watch for fungal disease pressure in standing crops.",
            )
        )
    return alerts


# --- Service entry points ---------------------------------------------------------


def _location_name(lat: float, lon: float) -> str:
    return f"{lat:.2f}°N, {lon:.2f}°E"


async def get_weather(lat: float | None = None, lon: float | None = None, days: int = 8) -> WeatherResponse:
    """Current + forecast weather with caching and graceful fallback.

    Raises ValueError for coordinates outside the supported region (caller
    translates that into a 422). External API failures fall back to local
    seasonal data — the response's ``source`` field says which one served it.
    """
    from app.external.weather_client import get_weather_client, validate_coordinates

    lat = lat if lat is not None else DEFAULT_LAT
    lon = lon if lon is not None else DEFAULT_LON
    validate_coordinates(lat, lon)

    cache = await get_cache()
    key = cache_key("weather", lat=lat, lon=lon, days=days)
    cached = await cache.get(key)
    if cached is not None:
        return WeatherResponse.model_validate(cached)

    day_dicts: list[dict] | None = None
    source = SOURCE_API
    client = get_weather_client()
    try:
        day_dicts = await client.fetch_forecast(lat, lon, days=days)
    except ExternalServiceError as exc:
        # Non-critical source: fall back to local data and say so.
        logger.warning("weather API unavailable, using local fallback: %s", exc)
        source = SOURCE_LOCAL
        day_dicts = None

    if day_dicts is None:
        weather_days = _local_forecast(days)
    else:
        weather_days = [WeatherDay.model_validate(d) for d in day_dicts]

    response = WeatherResponse(
        location=_location_name(lat, lon),
        lat=lat,
        lon=lon,
        today=weather_days[0],
        forecast=weather_days[1:],
        alerts=_build_alerts(weather_days),
        source=source,
    )
    await cache.set(key, response.model_dump(mode="json"), ttl=WEATHER_TTL)
    return response
