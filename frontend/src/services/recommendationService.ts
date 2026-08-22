/**
 * Sell/Hold recommendation API.
 *
 * The backend decision engine owns this logic — the frontend never computes
 * a recommendation. Results are transparent rules over recorded trends,
 * labelled as decision support (not financial advice).
 */
import { apiClient } from "./apiClient";
import type { SellHoldRequest, SellHoldResult } from "@/types/api";

export const recommendationService = {
  sellHold: (request: SellHoldRequest) =>
    apiClient.post<SellHoldResult>("/recommendations/sell-hold", request),
  history: (limit = 10) =>
    apiClient.get<SellHoldResult[]>("/recommendations/history", { limit }),
};
