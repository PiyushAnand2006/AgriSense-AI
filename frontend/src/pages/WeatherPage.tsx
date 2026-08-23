import { useCallback, useState } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { useApiQuery } from "@/hooks/useApiQuery";
import { weatherService } from "@/services/weatherService";
import { LoadingState, ErrorState, OfflineBanner } from "@/components/common/states";
import { formatDate } from "@/utils/format";
import type { WeatherAlert } from "@/types/api";

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
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");

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

      {/* Location input & Quick City Presets */}
      <div className="card flex flex-wrap items-end gap-3 p-4">
        <div className="w-28">
          <label htmlFor="weather-lat" className="label">
            {t("weather.location")} — lat
          </label>
          <input
            id="weather-lat"
            className="input"
            type="number"
            step="0.01"
            placeholder="25.32"
            value={lat}
            onChange={(event) => setLat(event.target.value)}
          />
        </div>
        <div className="w-28">
          <label htmlFor="weather-lon" className="label">
            lon
          </label>
          <input
            id="weather-lon"
            className="input"
            type="number"
            step="0.01"
            placeholder="82.98"
            value={lon}
            onChange={(event) => setLon(event.target.value)}
          />
        </div>

        <div className="flex flex-wrap items-center gap-1.5 pb-1">
          <span className="text-xs font-medium text-soil-500 dark:text-soil-400">Quick Presets:</span>
          {CITY_PRESETS.map((city) => (
            <button
              key={city.name}
              type="button"
              onClick={() => {
                setLat(city.lat);
                setLon(city.lon);
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

        {data && (
          <p className="ml-auto text-sm font-medium text-soil-600 dark:text-soil-300">📍 {data.location}</p>
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
