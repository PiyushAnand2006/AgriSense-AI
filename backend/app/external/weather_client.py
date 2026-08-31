"""Weather provider client.

Default integration target is Open-Meteo (https://open-meteo.com) because it
requires no API key; any Open-Meteo-compatible endpoint can be configured via
``WEATHER_API_URL`` / ``WEATHER_API_KEY``.

Responsibility of this module:

1. call the external weather API through the shared HTTP client
2. validate the raw payload shape
3. normalize it into AgriSense's internal ``WeatherDay`` structure

It never talks to the database and never decides caching policy — that is the
weather service's job.
"""

import logging
from datetime import date, timedelta
from typing import Any

from app.core.errors import UpstreamBadResponseError
from app.external.http_client import ExternalHttpClient

logger = logging.getLogger("agrisense.external.weather")

DEFAULT_WEATHER_API_URL = "https://api.open-meteo.com/v1"

# Latitude/longitude bounds for India — inputs outside these are rejected to
# keep the integration honest (and avoid SSRF-ish abuse of arbitrary queries).
INDIA_LAT_BOUNDS = (6.0, 37.0)
INDIA_LON_BOUNDS = (68.0, 97.5)


def validate_coordinates(lat: float, lon: float) -> None:
    if not (INDIA_LAT_BOUNDS[0] <= lat <= INDIA_LAT_BOUNDS[1]):
        raise ValueError(f"Latitude {lat} is outside the supported region (India).")
    if not (INDIA_LON_BOUNDS[0] <= lon <= INDIA_LON_BOUNDS[1]):
        raise ValueError(f"Longitude {lon} is outside the supported region (India).")


class WeatherClient:
    """Normalized access to an Open-Meteo-compatible forecast endpoint."""

    def __init__(self, base_url: str = "", api_key: str = "") -> None:
        self._http = ExternalHttpClient(
            base_url or DEFAULT_WEATHER_API_URL,
            api_key=api_key,
            service_name="weather",
        )

    async def fetch_forecast(self, lat: float, lon: float, days: int = 8) -> list[dict[str, Any]]:
        """Return normalized day dicts for today + the next ``days - 1`` days.

        Raises ExternalServiceError (connectivity) or UpstreamBadResponseError
        (malformed payload).
        """
        validate_coordinates(lat, lon)
        payload = await self._http.get(
            "/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,relative_humidity_2m_mean,"
                         "precipitation_probability_max,wind_speed_10m_max,weather_code",
                "forecast_days": max(1, min(days, 16)),
                "timezone": "auto",
            },
        )
        return self.normalize(payload)

    @staticmethod
    def normalize(payload: Any) -> list[dict[str, Any]]:
        """Map the provider's field names onto the internal structure."""
        try:
            daily = payload["daily"]
            current = payload.get("current")
            count = len(daily["time"])
            days: list[dict[str, Any]] = []
            for i in range(count):
                temp_max = float(daily["temperature_2m_max"][i])
                temp_min = float(daily["temperature_2m_min"][i])
                rain_prob = float(daily["precipitation_probability_max"][i] or 0)
                weather_code = int(daily["weather_code"][i] or 0)

                # For Today (index 0), use the exact real-time live current measurement if available
                if i == 0 and current is not None:
                    temp_c = float(current.get("temperature_2m", (temp_max + temp_min) / 2))
                    humidity_pct = float(current.get("relative_humidity_2m", daily["relative_humidity_2m_mean"][i] or 0))
                    wind_kph = float(current.get("wind_speed_10m", daily["wind_speed_10m_max"][i] or 0))
                    condition_code = int(current.get("weather_code", weather_code))
                elif i == 0:
                    temp_c = (temp_max + temp_min) / 2
                    humidity_pct = float(daily["relative_humidity_2m_mean"][i] or 0)
                    wind_kph = float(daily["wind_speed_10m_max"][i] or 0)
                    condition_code = weather_code
                else:
                    temp_c = temp_max
                    humidity_pct = float(daily["relative_humidity_2m_mean"][i] or 0)
                    wind_kph = float(daily["wind_speed_10m_max"][i] or 0)
                    condition_code = weather_code

                days.append(
                    {
                        "date": date.fromisoformat(daily["time"][i]),
                        "temperature_c": round(temp_c, 1),
                        "humidity_pct": round(humidity_pct),
                        "rain_probability": round(rain_prob),
                        "wind_kph": round(wind_kph, 1),
                        "condition": _condition_from_code(condition_code, rain_prob),
                    }
                )
            return days
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            logger.warning("weather payload failed validation: %s", exc)
            raise UpstreamBadResponseError(
                service="weather", detail="Weather provider returned an unexpected response."
            ) from exc


def _condition_from_code(code: int, rain_prob: float) -> str:
    if code == 0:
        return "Sunny"
    if code in (1, 2):
        return "Mostly Sunny"
    if code == 3:
        return "Cloudy"
    if 45 <= code <= 48:
        return "Foggy"
    if rain_prob >= 65 or code >= 95:
        return "Rain"
    if 51 <= code <= 80:
        return "Showers"
    return "Cloudy"


_weather_client: WeatherClient | None = None


def get_weather_client() -> WeatherClient:
    global _weather_client  # noqa: PLW0603
    if _weather_client is None:
        from app.core.config import get_settings

        settings = get_settings()
        _weather_client = WeatherClient(
            base_url=settings.weather_api_url,
            api_key=settings.weather_api_key,
        )
    return _weather_client


def reset_weather_client(client: WeatherClient | None = None) -> None:
    """Test seam: inject a mock client or reset the singleton."""
    global _weather_client  # noqa: PLW0603
    _weather_client = client
