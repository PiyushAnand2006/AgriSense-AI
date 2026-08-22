"""Weather schemas — standardized regardless of provider."""

from datetime import date

from app.schemas.common import CamelModel


class WeatherDay(CamelModel):
    date: date
    temperature_c: float
    humidity_pct: float
    rain_probability: float
    wind_kph: float
    condition: str  # Sunny | Mostly Sunny | Cloudy | Foggy | Showers | Rain


class WeatherAlert(CamelModel):
    severity: str  # INFO | WARNING | CRITICAL
    title: str
    message: str


class WeatherLocation(CamelModel):
    lat: float
    lon: float
    name: str


class WeatherResponse(CamelModel):
    location: str = "Default Region, India"
    lat: float | None = None
    lon: float | None = None
    today: WeatherDay
    forecast: list[WeatherDay]
    alerts: list[WeatherAlert]
    source: str  # "weather-api" | "weather-local"
