/** Weather API — the backend integrates the weather provider, never the frontend. */
import { apiClient } from "./apiClient";
import type { WeatherResponse } from "@/types/api";

export const weatherService = {
  current: (lat?: number, lon?: number) =>
    apiClient.get<WeatherResponse>("/weather/current", { lat, lon }),
  forecast: (lat?: number, lon?: number, days = 7) =>
    apiClient.get<WeatherResponse>("/weather/forecast", { lat, lon, days }),
};
