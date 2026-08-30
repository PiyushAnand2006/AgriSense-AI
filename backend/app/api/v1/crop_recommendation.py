"""API Endpoints for ML Crop Recommendation."""

from fastapi import APIRouter, status

from app.schemas.crop_recommendation import (
    CropRecommendationRequest,
    CropRecommendationResponse,
    ModelInfoResponse,
    PresetItem,
)
from app.services.ml_crop_service import crop_recommender

router = APIRouter(prefix="/crop-recommendation", tags=["crop-recommendation"])


@router.post("/predict", response_model=CropRecommendationResponse, status_code=status.HTTP_200_OK)
def predict_crop(payload: CropRecommendationRequest):
    """Predicts the optimal crop to cultivate based on soil parameters (N, P, K, pH)
    and environmental parameters (temperature, humidity, rainfall) using the tuned SVM model
    (89.20% accuracy on 50k real-world stress-test dataset — best across all trained models).
    """
    return crop_recommender.predict(payload)


@router.get("/model-info", response_model=ModelInfoResponse)
def get_model_info():
    """Returns metadata, hyperparameter tuning metrics, and features of the ML model."""
    return crop_recommender.get_model_info()


@router.get("/presets", response_model=list[PresetItem])
def get_presets():
    """Returns sample preset combinations for quick experimentation."""
    return crop_recommender.get_presets()
