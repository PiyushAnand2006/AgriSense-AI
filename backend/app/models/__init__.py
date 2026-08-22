"""SQLAlchemy models. Importing this package registers all tables."""

from app.models.user import AssistantConversation, AssistantMessage, FarmerProfile, Notification, User
from app.models.crop import Crop, FarmerCrop
from app.models.analysis import HealthRecord, SellHoldRecommendation
from app.models.market import Market, MarketPrice
from app.models.listing import CropListing
from app.models.weather import WeatherSnapshot

__all__ = [
    "User",
    "FarmerProfile",
    "Notification",
    "AssistantConversation",
    "AssistantMessage",
    "Crop",
    "FarmerCrop",
    "HealthRecord",
    "SellHoldRecommendation",
    "Market",
    "MarketPrice",
    "CropListing",
    "WeatherSnapshot",
]
