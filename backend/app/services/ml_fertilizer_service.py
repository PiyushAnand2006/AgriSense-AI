"""Machine Learning Fertilizer Prediction Service.

Loads the tuned XGBoost classifier trained on soil, environmental, and nutrient parameters
(Temparature, Humidity, Moisture, Soil Type, Crop Type, Nitrogen, Potassium, Phosphorous, Season)
to predict the most appropriate commercial fertilizer formulation.

Trained Target Classes:
  0: 10-26-26  (High Phosphorus & Potassium Complex)
  1: 14-35-14  (High Phosphorus Root Starter)
  2: 17-17-17  (Balanced Complete NPK)
  3: 20-20     (Ammonium Phosphate Sulfate + Sulfur)
  4: 28-28     (High Nitrogen-Phosphorus Complex)
  5: DAP       (Di-Ammonium Phosphate 18-46-0)
  6: Urea      (High Nitrogen 46-0-0)

Dataset Note:
  The feature 'Temparature' is intentionally spelled with the dataset schema name during
  dummy-variable preprocessing to ensure 100% matrix alignment with the serialized XGBoost tree graph.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.schemas.ml_fertilizer import (
    DISCLAIMER,
    FertilizerInputSummary,
    FertilizerNutrientProfile,
    FertilizerPresetItem,
    FertilizerProbabilityItem,
    MLFertilizerModelInfoResponse,
    MLFertilizerPredictionRequest,
    MLFertilizerPredictionResponse,
)

logger = logging.getLogger(__name__)

# Target fertilizer labels mapped from LabelEncoder fit on training data
FERTILIZER_CLASSES: dict[int, str] = {
    0: "10-26-26",
    1: "14-35-14",
    2: "17-17-17",
    3: "20-20",
    4: "28-28",
    5: "DAP",
    6: "Urea",
}

# Supported categories from the training dataset
SOIL_TYPES: list[str] = ["Black", "Clayey", "Loamy", "Red", "Sandy"]

SEASONS: list[str] = ["Kharif", "Rabi", "Zaid"]

CROP_SEASON_MAP: dict[str, list[str]] = {
    "Kharif": [
        "blackgram",
        "brinjal",
        "cotton",
        "jute",
        "kidneybeans",
        "maize",
        "mothbeans",
        "mungbean",
        "okra",
        "pigeonpeas",
        "rice",
    ],
    "Rabi": [
        "cabbage",
        "carrot",
        "cauliflower",
        "chickpea",
        "lentil",
        "mustard",
        "onion",
        "peas",
        "potato",
        "tomato",
        "wheat",
    ],
    "Zaid": [
        "cucumber",
        "muskmelon",
        "watermelon",
    ],
}

ALL_CROPS: list[str] = sorted(
    {crop for crops in CROP_SEASON_MAP.values() for crop in crops}
)

# Exact 39 dummy-encoded feature columns expected by the trained XGBoost model
FEATURE_COLUMNS: list[str] = [
    "Temparature",
    "Humidity",
    "Moisture",
    "Nitrogen",
    "Potassium",
    "Phosphorous",
    "Soil Type_Black",
    "Soil Type_Clayey",
    "Soil Type_Loamy",
    "Soil Type_Red",
    "Soil Type_Sandy",
    "Crop Type_blackgram",
    "Crop Type_brinjal",
    "Crop Type_cabbage",
    "Crop Type_carrot",
    "Crop Type_cauliflower",
    "Crop Type_chickpea",
    "Crop Type_cotton",
    "Crop Type_cucumber",
    "Crop Type_jute",
    "Crop Type_kidneybeans",
    "Crop Type_lentil",
    "Crop Type_maize",
    "Crop Type_mothbeans",
    "Crop Type_mungbean",
    "Crop Type_muskmelon",
    "Crop Type_mustard",
    "Crop Type_okra",
    "Crop Type_onion",
    "Crop Type_peas",
    "Crop Type_pigeonpeas",
    "Crop Type_potato",
    "Crop Type_rice",
    "Crop Type_tomato",
    "Crop Type_watermelon",
    "Crop Type_wheat",
    "Season_Kharif",
    "Season_Rabi",
    "Season_Zaid",
]

# Agronomic knowledge & nutrient profile for each predicted fertilizer class
FERTILIZER_PROFILES: dict[str, FertilizerNutrientProfile] = {
    "Urea": FertilizerNutrientProfile(
        npk_ratio="46-0-0 (46% Nitrogen)",
        primary_function="Concentrated nitrogen for rapid vegetative growth, lush green foliage, tillering, and protein synthesis.",
        application_advice="Apply in split doses (basal, active tillering, panicle initiation). Avoid surface runoff or broadcasting on dry soil.",
    ),
    "DAP": FertilizerNutrientProfile(
        npk_ratio="18-46-0 (18% Nitrogen, 46% Phosphorus P2O5)",
        primary_function="High-phosphorus starter fertilizer promoting robust root architecture, seedling establishment, and early cell division.",
        application_advice="Best applied as a basal placement below seed depth during sowing or transplanting for optimal root interception.",
    ),
    "17-17-17": FertilizerNutrientProfile(
        npk_ratio="17-17-17 (Equal parts N, P2O5, K2O)",
        primary_function="Complete balanced multi-nutrient complex ensuring uniform vegetative, root, and reproductive development.",
        application_advice="Ideal for basal dressing across cereal crops, commercial vegetables, and fruit orchards where soil has moderate fertility.",
    ),
    "10-26-26": FertilizerNutrientProfile(
        npk_ratio="10-26-26 (10% N, 26% P2O5, 26% K2O)",
        primary_function="High Phosphorus & Potassium complex enhancing root anchorage, flowering, grain weight, and drought resistance.",
        application_advice="Excellent basal and top-dressing choice for tuber crops (potato), oilseeds, pulses, and sugarcane.",
    ),
    "14-35-14": FertilizerNutrientProfile(
        npk_ratio="14-35-14 (14% N, 35% P2O5, 14% K2O)",
        primary_function="Phosphorus-rich formulation designed to trigger vigorous rooting and early flower initiation while supplying starter N and K.",
        application_advice="Apply at land preparation or sowing stage. Particularly beneficial in soils with high potassium reserves.",
    ),
    "20-20": FertilizerNutrientProfile(
        npk_ratio="20-20-0 + 13% Sulfur (Ammonium Phosphate Sulfate)",
        primary_function="Dual nitrogen-phosphorus source enriched with essential Sulfur for oil content in mustard/groundnut and protein synthesis.",
        application_advice="Apply as basal or early vegetative dressing in sulfur-deficient soils, oilseeds, and leguminous pulses.",
    ),
    "28-28": FertilizerNutrientProfile(
        npk_ratio="28-28-0 (28% N, 28% P2O5)",
        primary_function="High-potency nitrogen and phosphorus complex accelerating vegetative canopy and root establishment in heavy-feeding crops.",
        application_advice="Apply in early split dressing for maize, cotton, and sugarcane during vigorous vegetative stages.",
    ),
}

PRESETS: list[FertilizerPresetItem] = [
    FertilizerPresetItem(
        id="rice-kharif-urea",
        title="Rice / Kharif High-N Need",
        description="Clayey soil, moderate NPK, warm and humid monsoon conditions",
        values=MLFertilizerPredictionRequest(
            crop="rice",
            season="Kharif",
            soil_type="Clayey",
            nitrogen=35.0,
            phosphorous=18.0,
            potassium=12.0,
            temperature=26.0,
            humidity=70.0,
            moisture=35.0,
        ),
    ),
    FertilizerPresetItem(
        id="cotton-kharif-balanced",
        title="Cotton / Black Soil Complex",
        description="Black soil with balanced N-P-K demand and warm temperature",
        values=MLFertilizerPredictionRequest(
            crop="cotton",
            season="Kharif",
            soil_type="Black",
            nitrogen=42.0,
            phosphorous=32.0,
            potassium=40.0,
            temperature=29.0,
            humidity=65.0,
            moisture=30.0,
        ),
    ),
    FertilizerPresetItem(
        id="wheat-rabi-basal",
        title="Wheat / Rabi Root Starter",
        description="Loamy winter soil requiring high initial phosphorus for root anchoring",
        values=MLFertilizerPredictionRequest(
            crop="wheat",
            season="Rabi",
            soil_type="Loamy",
            nitrogen=22.0,
            phosphorous=65.0,
            potassium=28.0,
            temperature=18.0,
            humidity=45.0,
            moisture=40.0,
        ),
    ),
    FertilizerPresetItem(
        id="watermelon-zaid-summer",
        title="Watermelon / Zaid Summer",
        description="Sandy soil with high Potassium requirement for fruit sweetening",
        values=MLFertilizerPredictionRequest(
            crop="watermelon",
            season="Zaid",
            soil_type="Sandy",
            nitrogen=18.0,
            phosphorous=42.0,
            potassium=52.0,
            temperature=33.0,
            humidity=50.0,
            moisture=25.0,
        ),
    ),
]


class MLFertilizerPredictor:
    """Manages XGBoost fertilizer model loading, feature encoding, inference, and fallbacks."""

    def __init__(self) -> None:
        self._model: Any | None = None
        self._model_path: Path | None = None
        self._loaded: bool = False
        self._attempted_load: bool = False

    def _locate_model_file(self) -> Path | None:
        """Finds the tuned XGBoost fertilizer model across package resources and workspace paths."""
        pkg_path = Path(__file__).resolve().parent.parent / "ml_models" / "xgb_tunned_model.pkl"
        candidates = [
            pkg_path,
            Path("datasets/Fertilizer prediction/model/xgb_tunned_model.pkl"),
            Path("../datasets/Fertilizer prediction/model/xgb_tunned_model.pkl"),
            Path(r"c:\Users\thaku\hackathon&projects\AgriSense AI\datasets\Fertilizer prediction\model\xgb_tunned_model.pkl"),
            Path(r"c:\Users\thaku\hackathon&projects\AgriSense AI\backend\app\ml_models\xgb_tunned_model.pkl"),
        ]
        for path in candidates:
            if path.is_file():
                return path.resolve()
        return None

    def _load_model(self) -> None:
        if self._attempted_load:
            return
        self._attempted_load = True
        try:
            import joblib

            path = self._locate_model_file()
            if path and path.exists():
                self._model = joblib.load(str(path))
                self._model_path = path
                self._loaded = True
                logger.info("Loaded XGBoost Fertilizer model from %s", path)
            else:
                logger.warning("XGBoost fertilizer model file not found at expected paths.")
        except Exception as exc:
            logger.error("Failed to load XGBoost fertilizer model: %s", exc)
            self._loaded = False

    def is_loaded(self) -> bool:
        if not self._loaded and not self._attempted_load:
            self._load_model()
        return self._loaded and self._model is not None

    def get_model_info(self) -> MLFertilizerModelInfoResponse:
        return MLFertilizerModelInfoResponse(
            model_name="XGBoost Classifier (Hyperparameter Tuned)",
            model_type="Extreme Gradient Boosting with Multi-Class Logloss (n_estimators=300, max_depth=5, lr=0.2)",
            test_accuracy=98.5,
            total_classes=len(FERTILIZER_CLASSES),
            classes=list(FERTILIZER_CLASSES.values()),
            features=FEATURE_COLUMNS,
            supported_crops=CROP_SEASON_MAP,
            supported_soils=SOIL_TYPES,
            supported_seasons=SEASONS,
        )

    def get_presets(self) -> list[FertilizerPresetItem]:
        return PRESETS

    def _normalize_category(self, val: str, allowed: list[str]) -> str:
        """Finds case-insensitive matching category name."""
        val_clean = val.strip().lower()
        for candidate in allowed:
            if candidate.lower() == val_clean:
                return candidate
        return val.strip()

    def _build_feature_row(self, req: MLFertilizerPredictionRequest) -> dict[str, float]:
        """Constructs the exact 39-feature dictionary expected by the trained XGBoost model."""
        import pandas as pd  # noqa: F401

        # Normalize categorical strings
        norm_soil = self._normalize_category(req.soil_type, SOIL_TYPES)
        norm_season = self._normalize_category(req.season, SEASONS)
        norm_crop = req.crop.strip().lower()

        # Initialize all 39 columns to 0.0
        row: dict[str, float] = {col: 0.0 for col in FEATURE_COLUMNS}

        # Numeric features
        row["Temparature"] = float(req.temperature)
        row["Humidity"] = float(req.humidity)
        row["Moisture"] = float(req.moisture)
        row["Nitrogen"] = float(req.nitrogen)
        row["Potassium"] = float(req.potassium)
        row["Phosphorous"] = float(req.phosphorous)

        # One-hot encoded soil
        soil_col = f"Soil Type_{norm_soil}"
        if soil_col in row:
            row[soil_col] = 1.0

        # One-hot encoded crop
        crop_col = f"Crop Type_{norm_crop}"
        if crop_col in row:
            row[crop_col] = 1.0

        # One-hot encoded season
        season_col = f"Season_{norm_season}"
        if season_col in row:
            row[season_col] = 1.0

        return row

    def predict(self, req: MLFertilizerPredictionRequest) -> MLFertilizerPredictionResponse:
        """Runs XGBoost inference and returns prediction, confidence, and nutrient profile."""
        if not self.is_loaded():
            self._load_model()

        if not self.is_loaded() or self._model is None:
            raise RuntimeError("Fertilizer ML model artifact could not be loaded.")

        import pandas as pd

        # Validate categorical domains
        norm_crop = req.crop.strip().lower()
        norm_soil = self._normalize_category(req.soil_type, SOIL_TYPES)
        norm_season = self._normalize_category(req.season, SEASONS)

        if norm_crop not in ALL_CROPS:
            raise ValueError(
                f"Crop '{req.crop}' is not supported by the fertilizer ML model. "
                f"Supported crops: {', '.join(ALL_CROPS)}"
            )
        if norm_soil not in SOIL_TYPES:
            raise ValueError(
                f"Soil type '{req.soil_type}' is not supported by the fertilizer ML model. "
                f"Supported soil types: {', '.join(SOIL_TYPES)}"
            )
        if norm_season not in SEASONS:
            raise ValueError(
                f"Season '{req.season}' is not supported by the fertilizer ML model. "
                f"Supported seasons: {', '.join(SEASONS)}"
            )

        # Create 1-row DataFrame with exact columns
        feature_dict = self._build_feature_row(req)
        df_input = pd.DataFrame([feature_dict], columns=FEATURE_COLUMNS)

        # Inference
        pred_array = self._model.predict(df_input)
        pred_idx = int(pred_array[0])
        pred_label = FERTILIZER_CLASSES.get(pred_idx, "Urea")

        # Probabilities & Confidence
        probabilities: list[FertilizerProbabilityItem] = []
        confidence_val = 0.95
        if hasattr(self._model, "predict_proba"):
            raw_probas = self._model.predict_proba(df_input)[0]
            confidence_val = float(raw_probas[pred_idx])
            for idx, prob in enumerate(raw_probas):
                lbl = FERTILIZER_CLASSES.get(idx, f"Class_{idx}")
                probabilities.append(
                    FertilizerProbabilityItem(
                        fertilizer=lbl,
                        probability=round(float(prob), 4),
                    )
                )
            # Sort by highest probability descending
            probabilities.sort(key=lambda x: x.probability, reverse=True)

        summary = FertilizerInputSummary(
            crop=norm_crop,
            season=norm_season,
            soil_type=norm_soil,
            nitrogen=req.nitrogen,
            phosphorous=req.phosphorous,
            potassium=req.potassium,
            temperature=req.temperature,
            humidity=req.humidity,
            moisture=req.moisture,
        )

        return MLFertilizerPredictionResponse(
            status="success",
            prediction=pred_label,
            confidence=round(confidence_val, 4),
            confidence_pct=round(confidence_val * 100, 1),
            profile=FERTILIZER_PROFILES.get(pred_label),
            input_summary=summary,
            probabilities=probabilities,
            disclaimer=DISCLAIMER,
        )


# Singleton instance shared across requests
ml_fertilizer_predictor = MLFertilizerPredictor()
