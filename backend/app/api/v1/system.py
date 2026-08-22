"""System status + central feature flags.

Feature flags describe which API integrations are active — the backend is
the source of truth for the frontend.
"""

from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings

router = APIRouter(prefix="/system", tags=["system"])


@router.get("")
def system_status():
    settings = get_settings()
    return {
        "status": "ok",
        "app": "AgriSense AI API",
        "version": __version__,
        "integrations": {
            "weatherApi": settings.weather_integration_active,
            "mandiApi": settings.mandi_integration_active,
            "assistantApi": settings.assistant_integration_active,
            "redisCache": bool(settings.redis_url),
        },
        "features": {
            "cropCatalog": True,
            "diseaseInfo": True,
            "pestInfo": True,
            "treatmentInfo": True,
            "fertilizerGuidance": True,
            "marketPrices": True,
            "marketTrends": True,
            "sellHoldRules": True,
            "marketplace": True,
            "assistant": True,
            "notifications": True,
            "healthRecords": True,
        },
    }
