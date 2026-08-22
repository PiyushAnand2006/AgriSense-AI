"""Weather endpoints — external API integration through the service layer.

- GET /weather/current?lat=&lon=    today + alerts
- GET /weather/forecast?lat=&lon=   7-day forecast
- GET /weather/location?lat=&lon=   location metadata

The backend owns the external weather integration; the frontend never calls
the weather provider directly. Invalid coordinates return 422; provider
failures degrade to local seasonal data with ``source: "weather-local"``.
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.schemas.weather import WeatherLocation, WeatherResponse
from app.services.weather_service import get_weather

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/current", response_model=WeatherResponse)
async def current_weather(
    lat: float | None = Query(default=None, ge=-90, le=90),
    lon: float | None = Query(default=None, ge=-180, le=180),
):
    try:
        return await get_weather(lat=lat, lon=lon, days=8)
    except ValueError as exc:
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "VALIDATION_ERROR", "message": str(exc)}},
        )


@router.get("/forecast", response_model=WeatherResponse)
async def weather_forecast(
    lat: float | None = Query(default=None, ge=-90, le=90),
    lon: float | None = Query(default=None, ge=-180, le=180),
    days: int = Query(default=7, ge=1, le=15),
):
    try:
        return await get_weather(lat=lat, lon=lon, days=days + 1)
    except ValueError as exc:
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "VALIDATION_ERROR", "message": str(exc)}},
        )


@router.get("/location", response_model=WeatherLocation)
async def weather_location(
    lat: float = Query(ge=-90, le=90),
    lon: float = Query(ge=-180, le=180),
):
    from app.external.weather_client import validate_coordinates

    try:
        validate_coordinates(lat, lon)
    except ValueError as exc:
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "VALIDATION_ERROR", "message": str(exc)}},
        )
    return WeatherLocation(lat=lat, lon=lon, name=f"{lat:.2f}°N, {lon:.2f}°E")
