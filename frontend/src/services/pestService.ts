/** Pest information API — educational content service. */
import { apiClient } from "./apiClient";
import type { PestInfo, Treatment } from "@/types/api";

export const pestService = {
  list: (cropId?: string) => apiClient.get<PestInfo[]>("/pests", cropId ? { cropId } : undefined),
  detail: (pestId: string) => apiClient.get<PestInfo>(`/pests/${pestId}`),
  treatments: (pestId: string) => apiClient.get<Treatment[]>(`/pests/${pestId}/treatments`),
};
