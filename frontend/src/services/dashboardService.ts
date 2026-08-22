/**
 * Dashboard API — one aggregated request powering the whole page.
 * The backend gathers crop, market, weather and notification data.
 */
import { apiClient } from "./apiClient";
import type { DashboardSummary, SystemStatus } from "@/types/api";

export const dashboardService = {
  summary: (cropId?: string) => apiClient.get<DashboardSummary>("/dashboard", { cropId }),
  systemStatus: () => apiClient.get<SystemStatus>("/system"),
};
