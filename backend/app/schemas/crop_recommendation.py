"""Schemas for ML-based Crop Recommendation."""

from pydantic import BaseModel, Field


class CropRecommendationRequest(BaseModel):
    nitrogen: float = Field(
        ...,
        ge=0,
        le=300,
        description="Soil Nitrogen content (N) in kg/ha",
        examples=[90.0],
    )
    phosphorus: float = Field(
        ...,
        ge=0,
        le=200,
        description="Soil Phosphorus content (P) in kg/ha",
        examples=[42.0],
    )
    potassium: float = Field(
        ...,
        ge=0,
        le=300,
        description="Soil Potassium content (K) in kg/ha",
        examples=[43.0],
    )
    temperature: float = Field(
        ...,
        ge=-10,
        le=60,
        description="Ambient Temperature in °C",
        examples=[20.8],
    )
    humidity: float = Field(
        ...,
        ge=0,
        le=100,
        description="Relative Humidity in percentage (%)",
        examples=[82.0],
    )
    ph: float = Field(
        ...,
        ge=0,
        le=14,
        description="Soil pH value (0 - 14)",
        examples=[6.5],
    )
    rainfall: float = Field(
        ...,
        ge=0,
        le=1000,
        description="Annual / Seasonal Rainfall in mm",
        examples=[202.9],
    )


class CropAlternative(BaseModel):
    crop: str
    cropLabel: str
    probability: float = Field(..., description="Prediction probability in percentage (0-100)")


class AgronomicGuide(BaseModel):
    season: str
    waterRequirement: str
    soilType: str
    growthDurationDays: str
    fertilizerTip: str
    advisoryNote: str
    icon: str = "🌾"


class CropRecommendationResponse(BaseModel):
    recommendedCrop: str
    cropLabel: str
    confidence: float = Field(..., description="Top recommendation confidence in percentage (0-100)")
    alternatives: list[CropAlternative]
    agronomicGuide: AgronomicGuide
    modelName: str
    modelAccuracy: float
    inputParameters: dict[str, float]


class ModelInfoResponse(BaseModel):
    modelName: str
    modelType: str
    testAccuracy: float
    crossValScore: float
    totalClasses: int
    classes: list[str]
    features: list[str]


class PresetItem(BaseModel):
    id: str
    title: str
    description: str
    values: CropRecommendationRequest
