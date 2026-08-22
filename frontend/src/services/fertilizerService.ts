/** Fertilizer information + rule-based guidance API. */
import { apiClient } from "./apiClient";
import type {
  FertilizerGuidance,
  FertilizerGuidanceRequest,
  FertilizerInfo,
} from "@/types/api";

export const fertilizerService = {
  catalog: () => apiClient.get<FertilizerInfo[]>("/fertilizers"),
  cropCatalog: (cropId: string) =>
    apiClient.get<FertilizerInfo[]>(`/crops/${cropId}/fertilizers`),
  detail: (fertilizerId: string) =>
    apiClient.get<FertilizerInfo>(`/fertilizers/${fertilizerId}`),
  guidance: (request: FertilizerGuidanceRequest) =>
    apiClient.post<FertilizerGuidance>("/fertilizer-guidance", request),
};
