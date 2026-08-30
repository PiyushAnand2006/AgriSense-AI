"""Versioned API router assembly."""

from fastapi import APIRouter

from app.api.v1 import (
    assistant,
    auth,
    crop_recommendation,
    crops,
    dashboard,
    diseases,
    fertilizers,
    listings,
    market,
    notifications,
    pests,
    recommendations,
    seasons,
    system,
    treatments,
    uploads,
    weather,
)

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(auth.router)
api_router.include_router(seasons.router)
api_router.include_router(dashboard.router)
api_router.include_router(crops.router)
api_router.include_router(diseases.router)
api_router.include_router(pests.router)
api_router.include_router(treatments.router)
api_router.include_router(fertilizers.router)
api_router.include_router(fertilizers.guidance_router)
api_router.include_router(market.router)
api_router.include_router(recommendations.router)
api_router.include_router(crop_recommendation.router)
api_router.include_router(weather.router)
api_router.include_router(listings.router)
api_router.include_router(assistant.router)
api_router.include_router(notifications.router)
api_router.include_router(uploads.router)
