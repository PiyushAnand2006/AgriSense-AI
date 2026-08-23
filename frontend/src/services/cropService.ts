/**
 * Crop API — catalog, crop-scoped information sub-resources and farmer
 * planting CRUD. All application data flows through these typed services.
 */
import { apiClient } from "./apiClient";
import type {
  Crop,
  DiseaseInfo,
  FarmerCrop,
  FarmerCropInput,
  FertilizerInfo,
  PestInfo,
  Season,
  Treatment,
} from "@/types/api";

export const cropService = {
  catalog(season?: Season, search?: string) {
    return apiClient.get<Crop[]>("/crops", { season, search });
  },
  cropDetail(cropId: string) {
    return apiClient.get<Crop>(`/crops/${cropId}`);
  },
  myCrops(status?: string) {
    return apiClient.get<FarmerCrop[]>("/crops/mine", { status_filter: status });
  },
  createPlanting(input: FarmerCropInput) {
    return apiClient.post<FarmerCrop>("/crops", input);
  },
  updatePlanting(id: string, input: Partial<FarmerCropInput> & { status?: string }) {
    return apiClient.patch<FarmerCrop>(`/crops/${id}`, input);
  },
  deletePlanting(id: string) {
    return apiClient.delete<void>(`/crops/${id}`);
  },

  // Crop-scoped information sub-resources (information services).
  diseases(cropId: string) {
    return apiClient.get<DiseaseInfo[]>(`/crops/${cropId}/diseases`);
  },
  pests(cropId: string) {
    return apiClient.get<PestInfo[]>(`/crops/${cropId}/pests`);
  },
  treatments(cropId: string) {
    return apiClient.get<Treatment[]>(`/crops/${cropId}/treatments`);
  },
  fertilizers(cropId: string) {
    return apiClient.get<FertilizerInfo[]>(`/crops/${cropId}/fertilizers`);
  },
};
