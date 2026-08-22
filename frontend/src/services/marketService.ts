/**
 * Market API — normalized mandi prices and rule-computed trends.
 *
 * The backend owns the external mandi integration and normalization; the
 * frontend only ever sees the standardized structure (min/max/modal, unit,
 * source). There is no price forecast — trends are computed from recorded
 * history.
 */
import { apiClient } from "./apiClient";
import type { Market, MarketTrend, PriceHistory, PriceSummary } from "@/types/api";

export interface PriceBoardQuery {
  cropId?: string;
  marketId?: string;
  state?: string;
  search?: string;
  sort?: string;
  page?: number;
  limit?: number;
}

export const marketService = {
  markets: () => apiClient.get<Market[]>("/market/markets"),
  priceBoard: (query?: PriceBoardQuery) => {
    const params: Record<string, string | number | boolean | undefined> = query
      ? { ...query }
      : {};
    return apiClient.get<PriceSummary[]>("/market/prices", params);
  },
  priceHistory: (cropId: string, marketId?: string, days = 90) =>
    apiClient.get<PriceHistory>(`/market/prices/${cropId}`, { marketId, days }),
  trend: (cropId: string, marketId?: string, days = 30) =>
    apiClient.get<MarketTrend>(`/market/trends/${cropId}`, { marketId, days }),
};
