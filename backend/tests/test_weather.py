"""Weather endpoint tests.

External weather API calls are always mocked here — automated tests never
hit real third-party services.
"""

from datetime import date, timedelta

import pytest

from app.external import weather_client as weather_client_module
from app.external.weather_client import WeatherClient


def _mock_payload(days: int = 8) -> dict:
    """Build a valid Open-Meteo-shaped payload."""
    today = date.today()
    return {
        "current": {
            "temperature_2m": 24.0,
            "relative_humidity_2m": 60.0,
            "wind_speed_10m": 12.0,
            "weather_code": 0,
        },
        "daily": {
            "time": [(today + timedelta(days=i)).isoformat() for i in range(days)],
            "temperature_2m_max": [30.0 + i for i in range(days)],
            "temperature_2m_min": [18.0 + i for i in range(days)],
            "relative_humidity_2m_mean": [60.0] * days,
            "precipitation_probability_max": [10.0] * days,
            "wind_speed_10m_max": [12.0] * days,
            "weather_code": [0] * days,
        }
    }


@pytest.fixture()
def mocked_weather_client():
    class MockClient:
        async def fetch_forecast(self, lat, lon, days=8):
            return WeatherClient.normalize(_mock_payload(days))

    original = weather_client_module._weather_client
    weather_client_module._weather_client = MockClient()
    yield MockClient()
    weather_client_module._weather_client = original


@pytest.fixture(autouse=True)
def clear_weather_cache():
    """Weather responses are cached — reset the cache around each test."""
    from app.core import cache

    cache._cache = None  # force a fresh MemoryCache
    yield
    cache._cache = None


def test_current_weather_with_mocked_api(client, mocked_weather_client):
    body = client.get("/api/v1/weather/current", params={"lat": 25.3, "lon": 83.0}).json()
    assert body["source"] == "weather-api"
    assert body["location"]
    assert body["today"]["condition"] == "Sunny"  # weather_code 0
    assert body["today"]["temperatureC"] == 24.0  # (30 + 18) / 2
    assert len(body["forecast"]) == 7
    assert isinstance(body["alerts"], list)


def test_weather_forecast_endpoint(client, mocked_weather_client):
    body = client.get("/api/v1/weather/forecast", params={"lat": 25.3, "lon": 83.0, "days": 5}).json()
    assert len(body["forecast"]) == 5


def test_weather_location_endpoint(client):
    body = client.get("/api/v1/weather/location", params={"lat": 25.3, "lon": 83.0}).json()
    assert body["lat"] == 25.3 and body["lon"] == 83.0


def test_weather_validates_coordinates(client):
    # Outside India bounds -> 422 with the error envelope.
    response = client.get("/api/v1/weather/current", params={"lat": 50.0, "lon": 10.0})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_weather_falls_back_when_api_fails(client, monkeypatch):
    from app.core.errors import ExternalServiceError

    class FailingClient:
        async def fetch_forecast(self, lat, lon, days=8):
            raise ExternalServiceError(service="weather", detail="down")

    original = weather_client_module._weather_client
    weather_client_module._weather_client = FailingClient()
    try:
        response = client.get("/api/v1/weather/current")
        assert response.status_code == 200  # graceful degradation, not 503
        body = response.json()
        assert body["source"] == "weather-local"
        assert body["today"]["condition"] in ("Sunny", "Cloudy", "Rain")
    finally:
        weather_client_module._weather_client = original


def test_normalizer_rejects_malformed_payload():
    with pytest.raises(Exception):
        WeatherClient.normalize({"unexpected": "shape"})
