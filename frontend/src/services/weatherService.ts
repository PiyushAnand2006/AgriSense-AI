import { apiClient } from "./apiClient";
import type { LocationSearchResult, WeatherResponse } from "@/types/api";

export const weatherService = {
  current: (lat?: number, lon?: number) =>
    apiClient.get<WeatherResponse>("/weather/current", { lat, lon }),
  forecast: (lat?: number, lon?: number, days = 7) =>
    apiClient.get<WeatherResponse>("/weather/forecast", { lat, lon, days }),
  searchPlaces: async (query: string): Promise<LocationSearchResult[]> => {
    const q = query.trim();
    if (!q || q.length < 2) return [];
    try {
      const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(
        q,
      )}&count=10&language=en&format=json`;
      const res = await fetch(url, { headers: { Accept: "application/json" } });
      if (!res.ok) return [];
      const json = await res.json();
      const rawList = (json.results || []) as Array<{
        id: number;
        name: string;
        latitude: number;
        longitude: number;
        admin1?: string;
        country?: string;
        country_code?: string;
      }>;

      const mapped: LocationSearchResult[] = rawList.map((item) => ({
        id: item.id,
        name: item.name,
        latitude: item.latitude,
        longitude: item.longitude,
        admin1: item.admin1,
        country: item.country,
        countryCode: item.country_code,
      }));

      return mapped.sort((a, b) => {
        const aIn = a.countryCode === "IN" || a.country === "India" ? 1 : 0;
        const bIn = b.countryCode === "IN" || b.country === "India" ? 1 : 0;
        return bIn - aIn;
      });
    } catch {
      return [];
    }
  },
};
