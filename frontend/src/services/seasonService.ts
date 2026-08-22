/** Season API — database-driven season catalog (never hard-coded). */
import { apiClient } from "./apiClient";
import type { SeasonInfo, SeasonCrops } from "@/types/api";

export const seasonService = {
  list: () => apiClient.get<SeasonInfo[]>("/seasons"),
  detail: (seasonId: string) => apiClient.get<SeasonInfo>(`/seasons/${seasonId}`),
  crops: (seasonId: string) => apiClient.get<SeasonCrops>(`/seasons/${seasonId}/crops`),
  /** Convenience: crops for the RABI/ZAID wire value ("rabi"/"zaid"). */
  cropsBySeasonValue: (season: "RABI" | "ZAID") =>
    apiClient.get<SeasonCrops>(`/seasons/${season.toLowerCase()}/crops`),
};
