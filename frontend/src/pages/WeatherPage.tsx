import { useCallback, useEffect, useRef, useState } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useToast } from "@/components/ui/Toast";
import { weatherService } from "@/services/weatherService";
import { LoadingState, ErrorState, OfflineBanner } from "@/components/common/states";
import { formatDate } from "@/utils/format";
import type { LocationSearchResult, WeatherAlert } from "@/types/api";

const CONDITION_EMOJI: Record<string, string> = {
  Sunny: "☀️",
  "Mostly Sunny": "🌤️",
  Cloudy: "☁️",
  Foggy: "🌫️",
  Showers: "🌦️",
  Rain: "🌧️",
};

const ALERT_STYLES: Record<WeatherAlert["severity"], string> = {
  INFO: "border-primary-300 bg-primary-50 text-primary-900 dark:border-primary-700 dark:bg-primary-900/30 dark:text-primary-200",
  WARNING: "border-accent-300 bg-accent-50 text-accent-800 dark:border-accent-700 dark:bg-accent-900/30 dark:text-accent-200",
  CRITICAL: "border-red-300 bg-red-50 text-red-800 dark:border-red-700 dark:bg-red-900/30 dark:text-red-200",
};

const CITY_PRESETS = [
  { name: "Varanasi", lat: "25.32", lon: "82.98" },
  { name: "Bengaluru", lat: "12.97", lon: "77.59" },
  { name: "Delhi", lat: "28.61", lon: "77.21" },
  { name: "Nashik", lat: "19.99", lon: "73.79" },
  { name: "Jaipur", lat: "26.91", lon: "75.79" },
  { name: "Kolkata", lat: "22.57", lon: "88.36" },
];

export default function WeatherPage() {
  const { t } = useI18n();
  const { showToast } = useToast();
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");
  const [locating, setLocating] = useState(false);

  // ─── Place search autocomplete state ───
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<LocationSearchResult[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [searching, setSearching] = useState(false);
  const [selectedPlace, setSelectedPlace] = useState("");
  const [highlightIdx, setHighlightIdx] = useState(-1);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Debounced place search
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    const q = searchQuery.trim();
    if (q.length < 2) {
      setSearchResults([]);
      setShowDropdown(false);
      return;
    }
    setSearching(true);
    debounceRef.current = setTimeout(async () => {
      const results = await weatherService.searchPlaces(q);
      setSearchResults(results);
      setShowDropdown(results.length > 0);
      setHighlightIdx(-1);
      setSearching(false);
    }, 350);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [searchQuery]);

  const selectPlace = (place: LocationSearchResult) => {
    const pLat = place.latitude.toFixed(2);
    const pLon = place.longitude.toFixed(2);
    setLat(pLat);
    setLon(pLon);
    const label = [place.name, place.admin1, place.country].filter(Boolean).join(", ");
    setSelectedPlace(label);
    setSearchQuery(label);
    setShowDropdown(false);
  };

  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showDropdown || searchResults.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightIdx((prev) => (prev < searchResults.length - 1 ? prev + 1 : 0));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightIdx((prev) => (prev > 0 ? prev - 1 : searchResults.length - 1));
    } else if (e.key === "Enter" && highlightIdx >= 0) {
      e.preventDefault();
      selectPlace(searchResults[highlightIdx]);
    } else if (e.key === "Escape") {
      setShowDropdown(false);
    }
  };

  const handleCurrentLocation = () => {
    if (!navigator.geolocation) {
      showToast(t("weather.locationError"), "error");
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocating(false);
        const userLat = position.coords.latitude.toFixed(2);
        const userLon = position.coords.longitude.toFixed(2);
        setLat(userLat);
        setLon(userLon);
        setSelectedPlace(`${userLat}°N, ${userLon}°E`);
        setSearchQuery(`📍 ${userLat}°N, ${userLon}°E`);
        showToast(`📍 ${userLat}°N, ${userLon}°E`, "success");
      },
      () => {
        setLocating(false);
        showToast(t("weather.locationError"), "error");
      },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  };

  const validLat = lat.trim() && !isNaN(Number(lat)) ? Number(lat) : undefined;
  const validLon = lon.trim() && !isNaN(Number(lon)) ? Number(lon) : undefined;

  const activeLat = validLat !== undefined && validLon !== undefined ? validLat : undefined;
  const activeLon = validLat !== undefined && validLon !== undefined ? validLon : undefined;

  const fetchWeather = useCallback(
    () => weatherService.current(activeLat, activeLon),
    [activeLat, activeLon],
  );
  const { data, loading, error, stale, fetchedAt, refetch } = useApiQuery(fetchWeather, [activeLat, activeLon]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h1 className="font-display text-2xl font-extrabold">{t("weather.title")}</h1>
        {data && (
          <span
            className={`chip ${
              data.source === "weather-api"
                ? "bg-primary-50 text-primary-800 dark:bg-primary-900/40 dark:text-primary-200"
                : "bg-accent-50 text-accent-800 dark:bg-accent-900/40 dark:text-accent-200"
            }`}
          >
            {data.source === "weather-api" ? `⚡ ${t("weather.liveSource")}` : `🌦️ ${t("weather.localSource")}`}
          </span>
        )}
      </div>

      {stale && <OfflineBanner fetchedAt={fetchedAt} />}

      {/* ─── Search bar + GPS + Quick presets ─── */}
      <div className="card space-y-3 p-4">
        <div className="flex flex-wrap items-center gap-2">
          {/* Search input with autocomplete */}
          <div className="relative flex-1 min-w-[200px]" ref={dropdownRef}>
            <div className="relative">
              <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-soil-400">
                🔍
              </span>
              <input
                ref={inputRef}
                id="weather-search"
                className="input w-full pl-9 pr-3"
                type="text"
                placeholder={t("weather.searchPlaceholder")}
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setSelectedPlace("");
                }}
                onFocus={() => {
                  if (searchResults.length > 0) setShowDropdown(true);
                }}
                onKeyDown={handleSearchKeyDown}
                autoComplete="off"
              />
              {searching && (
                <span className="absolute inset-y-0 right-3 flex items-center">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-primary-600 border-t-transparent dark:border-primary-400" />
                </span>
              )}
            </div>

            {/* Dropdown results */}
            {showDropdown && (
              <ul className="absolute left-0 right-0 top-full z-50 mt-1 max-h-60 overflow-y-auto rounded-xl border border-soil-200 bg-white shadow-lg dark:border-soil-700 dark:bg-soil-900">
                {searchResults.map((place, idx) => {
                  return (
                    <li key={place.id}>
                      <button
                        type="button"
                        onClick={() => selectPlace(place)}
                        className={`flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm transition-colors ${
                          idx === highlightIdx
                            ? "bg-primary-50 text-primary-900 dark:bg-primary-900/40 dark:text-primary-200"
                            : "hover:bg-soil-50 dark:hover:bg-soil-800"
                        }`}
                      >
                        <span className="shrink-0 text-base">📍</span>
                        <span className="flex-1">
                          <span className="font-medium">{place.name}</span>
                          {(place.admin1 || place.country) && (
                            <span className="text-soil-500 dark:text-soil-400">
                              {" — "}
                              {[place.admin1, place.country].filter(Boolean).join(", ")}
                            </span>
                          )}
                        </span>
                        {(place.countryCode === "IN" || place.country === "India") && (
                          <span className="shrink-0 text-xs font-semibold text-primary-600 dark:text-primary-400">
                            🇮🇳
                          </span>
                        )}
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          {/* GPS button */}
          <button
            type="button"
            onClick={handleCurrentLocation}
            disabled={locating}
            className="btn btn-secondary inline-flex items-center gap-1.5 text-xs py-2 px-3 shrink-0"
            title={t("weather.useCurrentLocation")}
          >
            {locating ? (
              <>
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-primary-600 border-t-transparent dark:border-primary-400" />
                <span>{t("weather.locating")}</span>
              </>
            ) : (
              <>
                <span>📍</span>
                <span>{t("weather.useCurrentLocation")}</span>
              </>
            )}
          </button>
        </div>

        {/* Quick presets row */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs font-medium text-soil-500 dark:text-soil-400">Quick:</span>
          {CITY_PRESETS.map((city) => (
            <button
              key={city.name}
              type="button"
              onClick={() => {
                setLat(city.lat);
                setLon(city.lon);
                setSelectedPlace(city.name);
                setSearchQuery(city.name);
              }}
              className={`chip transition-colors ${
                lat === city.lat && lon === city.lon
                  ? "bg-primary-600 text-white"
                  : "bg-soil-100 text-soil-700 hover:bg-soil-200 dark:bg-soil-800 dark:text-soil-300 dark:hover:bg-soil-700"
              }`}
            >
              {city.name}
            </button>
          ))}
        </div>

        {/* Active location indicator */}
        {selectedPlace && data && (
          <p className="text-sm font-medium text-soil-600 dark:text-soil-300">📍 {data.location}</p>
        )}
      </div>

      {loading ? (
        <LoadingState rows={2} />
      ) : error ? (
        <ErrorState message={error.message} onRetry={() => void refetch()} />
      ) : data ? (
        <>
          {/* Today */}
          <div className="card flex flex-wrap items-center gap-6 p-6">
            <span aria-hidden className="text-6xl">
              {CONDITION_EMOJI[data.today.condition] ?? "🌡️"}
            </span>
            <div>
              <p className="font-display text-4xl font-extrabold">{data.today.temperatureC}°C</p>
              <p className="text-sm font-medium text-soil-600 dark:text-soil-300">
                {data.today.condition} · {t("weather.today")}
              </p>
            </div>
            <dl className="ml-auto grid grid-cols-3 gap-6 text-sm">
              <div>
                <dt className="text-xs text-soil-500 dark:text-soil-400">{t("weather.humidity")}</dt>
                <dd className="font-bold">{data.today.humidityPct}%</dd>
              </div>
              <div>
                <dt className="text-xs text-soil-500 dark:text-soil-400">{t("weather.rainChance")}</dt>
                <dd className="font-bold">{data.today.rainProbability}%</dd>
              </div>
              <div>
                <dt className="text-xs text-soil-500 dark:text-soil-400">{t("weather.wind")}</dt>
                <dd className="font-bold">{data.today.windKph} km/h</dd>
              </div>
            </dl>
          </div>

          {/* Alerts */}
          {data.alerts.length > 0 && (
            <section aria-label={t("weather.alerts")} className="space-y-2">
              {data.alerts.map((alert) => (
                <div
                  key={alert.title}
                  role="status"
                  className={`rounded-xl border px-4 py-3 text-sm font-medium ${ALERT_STYLES[alert.severity]}`}
                >
                  <strong>{alert.title}</strong> — {alert.message}
                </div>
              ))}
            </section>
          )}

          {/* 7-day forecast */}
          <section aria-label={t("weather.forecast7")}>
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
              {t("weather.forecast7")}
            </h2>
            <ul className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-7">
              {data.forecast.map((day) => (
                <li key={day.date} className="card flex flex-col items-center gap-1.5 p-4 text-center">
                  <p className="text-xs font-semibold text-soil-500 dark:text-soil-400">
                    {formatDate(day.date)}
                  </p>
                  <span aria-hidden className="text-3xl">
                    {CONDITION_EMOJI[day.condition] ?? "🌡️"}
                  </span>
                  <p className="text-lg font-bold">{day.temperatureC}°C</p>
                  <p className="text-xs text-soil-500 dark:text-soil-400">
                    💧 {day.humidityPct}% · 🌧 {day.rainProbability}%
                  </p>
                </li>
              ))}
            </ul>
          </section>
        </>
      ) : (
        <ErrorState onRetry={() => void refetch()} />
      )}
    </div>
  );
}
