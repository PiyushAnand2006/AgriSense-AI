"""Fertilizer information + guidance endpoints.

Two Partitioned Approaches:
1. API-Based Recommendation:
   - GET  /fertilizers                 fertilizer category catalog
   - GET  /fertilizers/{id}            catalog detail
   - POST /fertilizer-guidance         validated rule-based guidance

2. ML-Based Fertilizer Prediction:
   - POST /fertilizer/ml-predict       XGBoost ML-driven fertilizer classification
   - POST /fertilizers/ml-predict      Alias route for ML prediction
   - GET  /fertilizer/ml-info          Model metadata & supported features
   - GET  /fertilizer/ml-presets       Curated preset scenarios for rapid testing
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.crop import Crop
from app.models.user import User
from app.schemas.fertilizer import (
    FertilizerGuidanceRequest,
    FertilizerGuidanceResult,
    FertilizerInfoOut,
)
from app.schemas.ml_fertilizer import (
    FertilizerPresetItem,
    MLFertilizerModelInfoResponse,
    MLFertilizerPredictionRequest,
    MLFertilizerPredictionResponse,
)
from app.services.knowledge import get_fertilizer, get_fertilizer_guidance, list_fertilizers
from app.services.ml_fertilizer_service import ml_fertilizer_predictor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fertilizers", tags=["fertilizers"])
guidance_router = APIRouter(prefix="/fertilizer-guidance", tags=["fertilizers"])
ml_router = APIRouter(prefix="/fertilizer", tags=["fertilizers"])


def _info_out(entry: dict) -> FertilizerInfoOut:
    return FertilizerInfoOut.model_validate(entry)


# --- 1. API / Rule-Based Catalog Endpoints ---


@router.get("", response_model=list[FertilizerInfoOut])
def list_catalog():
    return [_info_out(f) for f in list_fertilizers()]


@router.get("/{fertilizer_id}", response_model=FertilizerInfoOut)
def fertilizer_detail(fertilizer_id: str):
    entry = get_fertilizer(fertilizer_id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fertilizer not found."
        )
    return _info_out(entry)


@guidance_router.post("", response_model=FertilizerGuidanceResult)
def fertilizer_guidance(
    payload: FertilizerGuidanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    crop = db.get(Crop, payload.crop_id)
    if crop is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown crop id.")

    guidance = get_fertilizer_guidance(
        crop.name, payload.growth_stage.upper(), payload.soil_condition.upper(), payload.npk
    )
    return FertilizerGuidanceResult(
        crop=crop.name,
        growth_stage=payload.growth_stage.upper(),
        soil_condition=payload.soil_condition.upper(),
        recommended_category=guidance["recommended_category"],
        recommended_fertilizer_id=guidance["recommended_fertilizer_id"],
        application_timing=guidance["application_timing"],
        soil_note=guidance["soil_note"],
        guidance=guidance["guidance"],
    )


# --- 2. ML-Based Fertilizer Prediction Endpoints ---


def _run_ml_prediction(payload: MLFertilizerPredictionRequest) -> MLFertilizerPredictionResponse:
    try:
        return ml_fertilizer_predictor.predict(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Unexpected error during ML fertilizer prediction: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during fertilizer ML inference.",
        )


@ml_router.post("/ml-predict", response_model=MLFertilizerPredictionResponse)
def ml_fertilizer_predict(payload: MLFertilizerPredictionRequest):
    """Predicts optimal commercial fertilizer formulation using trained XGBoost classifier."""
    return _run_ml_prediction(payload)


@router.post("/ml-predict", response_model=MLFertilizerPredictionResponse)
def ml_fertilizers_predict_alias(payload: MLFertilizerPredictionRequest):
    """Alias for /api/v1/fertilizer/ml-predict."""
    return _run_ml_prediction(payload)


@ml_router.get("/ml-info", response_model=MLFertilizerModelInfoResponse)
def ml_fertilizer_info():
    """Returns metadata about the trained XGBoost fertilizer classifier."""
    return ml_fertilizer_predictor.get_model_info()


@ml_router.get("/ml-presets", response_model=list[FertilizerPresetItem])
def ml_fertilizer_presets():
    """Returns quick test scenarios for the ML fertilizer prediction form."""
    return ml_fertilizer_predictor.get_presets()
