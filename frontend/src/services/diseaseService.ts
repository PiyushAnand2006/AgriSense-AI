/** Disease information API — educational content service. */
import { apiClient } from "./apiClient";
import type { DiseaseInfo, Treatment } from "@/types/api";

export const diseaseService = {
  list: (cropId?: string) =>
    apiClient.get<DiseaseInfo[]>("/diseases", cropId ? { cropId } : undefined),
  detail: (diseaseId: string) => apiClient.get<DiseaseInfo>(`/diseases/${diseaseId}`),
  treatments: (diseaseId: string) =>
    apiClient.get<Treatment[]>(`/diseases/${diseaseId}/treatments`),
};

export const treatmentService = {
  list: () => apiClient.get<Treatment[]>("/treatments"),
  detail: (treatmentId: string) => apiClient.get<Treatment>(`/treatments/${treatmentId}`),
};
