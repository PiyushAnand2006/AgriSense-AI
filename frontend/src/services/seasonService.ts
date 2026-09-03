/** Season API — database-driven season catalog (never hard-coded). */
import { apiClient } from "./apiClient";
import type { SeasonInfo, SeasonCrops, Season } from "@/types/api";

export const seasonService = {
  list: () => apiClient.get<SeasonInfo[]>("/seasons"),
  detail: (seasonId: string) => apiClient.get<SeasonInfo>(`/seasons/${seasonId}`),
  crops: (seasonId: string) => apiClient.get<SeasonCrops>(`/seasons/${seasonId}/crops`),
  /** Convenience: crops for the RABI/KHARIF/ZAID wire value. */
  cropsBySeasonValue: (season: Season) =>
    apiClient.get<SeasonCrops>(`/seasons/${season.toLowerCase()}/crops`),
};
