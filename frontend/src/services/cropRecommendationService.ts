/**
 * ML Crop Recommendation API client service.
 */
import { apiClient } from "./apiClient";
import type {
  CropRecommendationInput,
  CropRecommendationResult,
  ModelInfo,
  PresetItem,
} from "@/types/api";

export const cropRecommendationService = {
  predict: (payload: CropRecommendationInput) =>
    apiClient.post<CropRecommendationResult>("/crop-recommendation/predict", payload),

  modelInfo: () =>
    apiClient.get<ModelInfo>("/crop-recommendation/model-info"),

  presets: () =>
    apiClient.get<PresetItem[]>("/crop-recommendation/presets"),
};
