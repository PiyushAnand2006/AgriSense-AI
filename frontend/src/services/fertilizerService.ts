/** Fertilizer information, rule-based guidance, and ML-based prediction APIs. */
import { apiClient } from "./apiClient";
import type {
  FertilizerGuidance,
  FertilizerGuidanceRequest,
  FertilizerInfo,
  FertilizerPresetItem,
  MLFertilizerModelInfo,
  MLFertilizerPredictionRequest,
  MLFertilizerPredictionResponse,
} from "@/types/api";

export const fertilizerService = {
  // 1. API / Rule-based guidance
  catalog: () => apiClient.get<FertilizerInfo[]>("/fertilizers"),
  cropCatalog: (cropId: string) =>
    apiClient.get<FertilizerInfo[]>(`/crops/${cropId}/fertilizers`),
  detail: (fertilizerId: string) =>
    apiClient.get<FertilizerInfo>(`/fertilizers/${fertilizerId}`),
  guidance: (request: FertilizerGuidanceRequest) =>
    apiClient.post<FertilizerGuidance>("/fertilizer-guidance", request),

  // 2. ML-based XGBoost prediction
  mlPredict: (request: MLFertilizerPredictionRequest) =>
    apiClient.post<MLFertilizerPredictionResponse>("/fertilizer/ml-predict", request),
  mlInfo: () => apiClient.get<MLFertilizerModelInfo>("/fertilizer/ml-info"),
  mlPresets: () => apiClient.get<FertilizerPresetItem[]>("/fertilizer/ml-presets"),
};
