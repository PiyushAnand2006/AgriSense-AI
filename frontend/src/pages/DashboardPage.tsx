import { useCallback } from "react";
import { Link } from "react-router-dom";
import { useI18n } from "@/i18n/I18nProvider";
import { useAuth } from "@/auth/AuthProvider";
import { useApiQuery } from "@/hooks/useApiQuery";
import { dashboardService } from "@/services/dashboardService";
import { LoadingState, ErrorState, OfflineBanner } from "@/components/common/states";
import { RiskBadge, SeasonBadge, TrendIndicator } from "@/components/common/badges";
import { formatINR } from "@/utils/format";

function scoreTone(label: string): string {
  if (label === "Excellent") return "text-primary-700 dark:text-primary-300";
  if (label === "Good") return "text-primary-600 dark:text-primary-400";
  if (label === "Watch") return "text-accent-600 dark:text-accent-300";
  return "text-red-600 dark:text-red-400";
}

export default function DashboardPage() {
  const { t } = useI18n();
  const { user } = useAuth();

  const fetcher = useCallback(() => dashboardService.summary(), []);
  const { data, loading, error, stale, fetchedAt, refetch } = useApiQuery(fetcher, []);

  if (loading) return <LoadingState rows={4} />;
  if (error || !data)
    return <ErrorState message={error?.message} onRetry={() => void refetch()} />;

  const trend = data.marketTrend;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-extrabold">{t("dashboard.title")}</h1>
          <p className="text-sm text-soil-500 dark:text-soil-400">
            {t("dashboard.greeting")}, {user?.name?.split(" ")[0]} 👋
          </p>
        </div>
        <SeasonBadge season={data.season} />
      </div>

      {stale && <OfflineBanner fetchedAt={fetchedAt} />}
      {data.warnings.length > 0 && (
        <div role="status" className="rounded-xl border border-accent-300 bg-accent-50 px-4 py-3 text-sm font-medium text-accent-800 dark:border-accent-700 dark:bg-accent-900/30 dark:text-accent-200">
          {data.warnings.map((warning) => (
            <p key={warning}>⚠️ {warning}</p>
          ))}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Crop card */}
        <div className="card p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
            {t("dashboard.currentCrop")}
          </p>
          <p className="mt-2 font-display text-xl font-bold">{data.crop.name}</p>
          <p className="mt-1 text-sm text-soil-500 dark:text-soil-400">
            {data.crop.sowingWindow ? `${t("crops.sowingWindow")}: ${data.crop.sowingWindow}` : data.season}
          </p>
        </div>

        {/* Health card */}
        <div className="card p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
            {t("dashboard.cropHealth")}
          </p>
          <p className={`mt-2 font-display text-xl font-bold ${scoreTone(data.healthScoreLabel)}`}>
            {data.healthScore} · {data.healthScoreLabel}
          </p>
          {data.latestRecord ? (
            <p className="mt-1 truncate text-sm text-soil-500 dark:text-soil-400">
              {data.latestRecord.name} ({data.latestRecord.severity.toLowerCase()})
            </p>
          ) : (
            <p className="mt-1 text-sm text-soil-500 dark:text-soil-400">{t("health.noRecords")}</p>
          )}
        </div>

        {/* Market card */}
        <div className="card p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
            {t("dashboard.marketPrice")}
          </p>
          <p className="mt-2 font-display text-xl font-bold">{formatINR(data.marketPrice)}</p>
          {trend && (
            <p className="mt-1 flex items-center gap-2 text-sm">
              <TrendIndicator value={trend.changePct} />
              <span className="text-soil-500 dark:text-soil-400">{data.marketName}</span>
            </p>
          )}
        </div>

        {/* Weather card */}
        <div className="card p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
            {t("dashboard.weatherNow")}
          </p>
          {data.weather ? (
            <>
              <p className="mt-2 font-display text-xl font-bold">
                {data.weather.temperatureC}°C · {data.weather.condition}
              </p>
              <p className="mt-1 text-sm text-soil-500 dark:text-soil-400">
                💧 {data.weather.humidityPct}% · 🌧 {data.weather.rainProbability}%
              </p>
            </>
          ) : (
            <p className="mt-2 text-sm text-soil-500 dark:text-soil-400">—</p>
          )}
        </div>
      </div>

      {/* Recommendation + trend row */}
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
            {t("dashboard.recommendation")}
          </p>
          {data.recommendation ? (
            <div className="mt-2 flex items-center gap-3">
              <span
                className={`rounded-xl px-3 py-1.5 font-display text-lg font-extrabold ${
                  data.recommendation === "HOLD"
                    ? "bg-primary-100 text-primary-800 dark:bg-primary-900/50 dark:text-primary-200"
                    : "bg-accent-100 text-accent-800 dark:bg-accent-900/50 dark:text-accent-200"
                }`}
              >
                {data.recommendation}
              </span>
              {data.recommendationRisk && <RiskBadge risk={data.recommendationRisk} />}
            </div>
          ) : (
            <p className="mt-2 text-sm text-soil-500 dark:text-soil-400">
              {t("dashboard.noRecommendation")}
            </p>
          )}
          {data.expectedAdditionalReturn !== null && (
            <p className="mt-2 text-sm text-soil-600 dark:text-soil-300">
              {t("recommendation.expectedReturn")}: {formatINR(data.expectedAdditionalReturn)}
              {t("common.perQuintal")}
            </p>
          )}
        </div>

        <div className="card p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
            {t("dashboard.marketTrend")} · {trend?.days ?? 30}d
          </p>
          {trend ? (
            <>
              <div className="mt-3 flex items-center gap-6 text-sm">
                <span className="flex flex-col">
                  <span className="text-xs text-soil-500 dark:text-soil-400">{t("market.currentPrice")}</span>
                  <span className="font-bold">{formatINR(trend.currentPrice)}</span>
                </span>
                <span className="flex flex-col">
                  <span className="text-xs text-soil-500 dark:text-soil-400">7d / 30d</span>
                  <span className="flex items-center gap-2 font-bold">
                    <TrendIndicator value={trend.trend7d} />
                    <TrendIndicator value={trend.trend30d} />
                  </span>
                </span>
              </div>
              {/* Simple sparkline of recorded modal prices */}
              <div className="mt-4 flex h-16 items-end gap-1" aria-hidden>
                {trend.history.slice(-30).map((point) => {
                  const values = trend.history.map((p) => p.modalPrice);
                  const min = Math.min(...values);
                  const max = Math.max(...values);
                  const height = max === min ? 50 : 8 + ((point.modalPrice - min) / (max - min)) * 56;
                  return (
                    <span
                      key={point.date}
                      className="flex-1 rounded-t bg-primary-400/70 dark:bg-primary-500/60"
                      style={{ height: `${height}%` }}
                    />
                  );
                })}
              </div>
              <p className="mt-2 text-xs text-soil-500 dark:text-soil-400">{t("market.notAForecast")}</p>
            </>
          ) : (
            <p className="mt-2 text-sm text-soil-500 dark:text-soil-400">—</p>
          )}
        </div>
      </div>

      {/* Health history */}
      {data.healthHistory.length > 0 && (
        <div className="card p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
            {t("dashboard.healthOverTime")}
          </p>
          <ul className="mt-3 space-y-2">
            {[...data.healthHistory].reverse().slice(0, 5).map((point) => (
              <li key={`${point.date}-${point.name}`} className="flex items-center justify-between text-sm">
                <span className="font-medium">
                  {point.name} · {point.severity?.toLowerCase()}
                </span>
                <span className="text-soil-500 dark:text-soil-400">
                  {new Date(point.date).toLocaleDateString()} · {point.score}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ML Crop Recommendation Spotlight Banner */}
      <div className="relative overflow-hidden rounded-2xl border border-primary-300/80 bg-gradient-to-r from-primary-600 via-primary-700 to-soil-800 p-6 text-white shadow-md dark:border-primary-600/40">
        <div className="relative z-10 flex flex-wrap items-center justify-between gap-4">
          <div className="max-w-xl space-y-1.5">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-white/20 px-3 py-1 text-xs font-bold uppercase tracking-wider backdrop-blur">
              ✨ {t("cropRec.badge")}
            </span>
            <h2 className="font-display text-xl font-black sm:text-2xl">
              {t("cropRec.dashboardBannerTitle")}
            </h2>
            <p className="text-xs leading-relaxed text-primary-100 sm:text-sm">
              {t("cropRec.dashboardBannerText")}
            </p>
          </div>
          <Link
            to="/crop-recommendation"
            className="rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-primary-800 shadow-sm transition hover:bg-primary-50 hover:shadow-md dark:bg-soil-900 dark:text-primary-300 dark:hover:bg-soil-800"
          >
            🌾 {t("cropRec.getStarted")} →
          </Link>
        </div>
      </div>

      {/* Quick actions */}
      <div className="card flex flex-wrap gap-3 p-5">
        <p className="w-full text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
          {t("dashboard.quickActions")}
        </p>
        <Link to="/crop-recommendation" className="btn-primary">
          🌾 {t("nav.cropRecommendation")}
        </Link>
        <Link to="/health" className="btn-secondary">{t("dashboard.browseHealth")}</Link>
        <Link to="/market" className="btn-secondary">{t("dashboard.openMarket")}</Link>
        <Link to="/recommendation" className="btn-secondary">{t("dashboard.sellHold")}</Link>
      </div>
    </div>
  );
}
