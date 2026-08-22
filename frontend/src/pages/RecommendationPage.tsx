import { useCallback, useState } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useCropSelection } from "@/store/CropContext";
import { cropService } from "@/services/cropService";
import { marketService } from "@/services/marketService";
import { recommendationService } from "@/services/recommendationService";
import { useToast } from "@/components/ui/Toast";
import { LoadingState } from "@/components/common/states";
import { RiskBadge, TrendIndicator } from "@/components/common/badges";
import { ApiError } from "@/services/apiClient";
import { formatINR } from "@/utils/format";
import type { SellHoldResult } from "@/types/api";

export default function RecommendationPage() {
  const { t } = useI18n();
  const { showToast } = useToast();
  const { season, cropId, setCrop } = useCropSelection();

  const [marketId, setMarketId] = useState("");
  const [quantity, setQuantity] = useState("100");
  const [storageDays, setStorageDays] = useState("14");
  const [storageCost, setStorageCost] = useState("");
  const [riskTolerance, setRiskTolerance] = useState<"LOW" | "MEDIUM" | "HIGH">("MEDIUM");
  const [result, setResult] = useState<SellHoldResult | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const fetchCrops = useCallback(() => cropService.catalog(season), [season]);
  const { data: crops } = useApiQuery(fetchCrops, [season]);
  const activeCropId = cropId ?? crops?.[0]?.id ?? "";

  const fetchMarkets = useCallback(() => marketService.markets(), []);
  const { data: markets } = useApiQuery(fetchMarkets, []);

  const fetchHistory = useCallback(() => recommendationService.history(5), [result]);
  const { data: history } = useApiQuery(fetchHistory, [result]);

  const submit = async () => {
    if (!activeCropId || submitting) return;
    setSubmitting(true);
    try {
      const response = await recommendationService.sellHold({
        cropId: activeCropId,
        marketId: marketId || undefined,
        quantity: Number(quantity),
        storageDays: Number(storageDays),
        storageCost: storageCost ? Number(storageCost) : undefined,
        riskTolerance,
      });
      setResult(response.data);
      showToast(t("recommendation.calculate"), "success");
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : t("common.error"), "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="font-display text-2xl font-extrabold">{t("recommendation.title")}</h1>

      <div className="card space-y-4 p-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="rec-crop" className="label">
              {t("common.selectCrop")}
            </label>
            <select
              id="rec-crop"
              className="input cursor-pointer"
              value={activeCropId}
              onChange={(event) => setCrop(event.target.value)}
            >
              {(crops ?? []).map((crop) => (
                <option key={crop.id} value={crop.id}>
                  {crop.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="rec-market" className="label">
              {t("common.selectMarket")}
            </label>
            <select
              id="rec-market"
              className="input cursor-pointer"
              value={marketId}
              onChange={(event) => setMarketId(event.target.value)}
            >
              <option value="">{t("common.all")}</option>
              {(markets ?? []).map((market) => (
                <option key={market.id} value={market.id}>
                  {market.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <label htmlFor="rec-quantity" className="label">
              {t("recommendation.quantity")}
            </label>
            <input
              id="rec-quantity"
              type="number"
              min="1"
              className="input"
              value={quantity}
              onChange={(event) => setQuantity(event.target.value)}
            />
          </div>
          <div>
            <label htmlFor="rec-days" className="label">
              {t("recommendation.storageDays")}
            </label>
            <input
              id="rec-days"
              type="number"
              min="1"
              max="180"
              className="input"
              value={storageDays}
              onChange={(event) => setStorageDays(event.target.value)}
            />
          </div>
          <div>
            <label htmlFor="rec-cost" className="label">
              {t("recommendation.storageCost")}
            </label>
            <input
              id="rec-cost"
              type="number"
              min="0"
              className="input"
              value={storageCost}
              onChange={(event) => setStorageCost(event.target.value)}
            />
          </div>
          <div>
            <label htmlFor="rec-risk" className="label">
              {t("recommendation.riskTolerance")}
            </label>
            <select
              id="rec-risk"
              className="input cursor-pointer"
              value={riskTolerance}
              onChange={(event) => setRiskTolerance(event.target.value as "LOW" | "MEDIUM" | "HIGH")}
            >
              {(["LOW", "MEDIUM", "HIGH"] as const).map((risk) => (
                <option key={risk} value={risk}>
                  {risk}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button type="button" className="btn-primary" onClick={() => void submit()} disabled={submitting || !activeCropId}>
          {t("recommendation.calculate")}
        </button>
      </div>

      {result && (
        <div className="card space-y-5 p-6" aria-live="polite">
          <div className="flex flex-wrap items-center gap-4">
            <span
              className={`rounded-2xl px-6 py-3 font-display text-3xl font-extrabold ${
                result.recommendation === "HOLD"
                  ? "bg-primary-100 text-primary-800 dark:bg-primary-900/50 dark:text-primary-200"
                  : "bg-accent-100 text-accent-800 dark:bg-accent-900/50 dark:text-accent-200"
              }`}
            >
              {result.recommendation}
            </span>
            <RiskBadge risk={result.risk} />
            <span className="flex items-center gap-2 text-sm">
              {t("recommendation.trend")}:
              <strong>{result.trend}</strong>
              <TrendIndicator value={result.trendChangePct} />
            </span>
          </div>

          <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl bg-soil-50 p-4 dark:bg-soil-800/60">
              <dt className="text-xs text-soil-500 dark:text-soil-400">{t("recommendation.currentPrice")}</dt>
              <dd className="mt-1 font-bold">{formatINR(result.currentPrice)}{t("common.perQuintal")}</dd>
            </div>
            <div className="rounded-xl bg-soil-50 p-4 dark:bg-soil-800/60">
              <dt className="text-xs text-soil-500 dark:text-soil-400">{t("recommendation.projectedPrice")}</dt>
              <dd className="mt-1 font-bold">{formatINR(result.projectedPrice)}{t("common.perQuintal")}</dd>
            </div>
            <div className="rounded-xl bg-soil-50 p-4 dark:bg-soil-800/60">
              <dt className="text-xs text-soil-500 dark:text-soil-400">{t("recommendation.storageCostLabel")}</dt>
              <dd className="mt-1 font-bold">{formatINR(result.storageCost)}</dd>
            </div>
            <div className="rounded-xl bg-soil-50 p-4 dark:bg-soil-800/60">
              <dt className="text-xs text-soil-500 dark:text-soil-400">{t("recommendation.expectedReturn")}</dt>
              <dd
                className={`mt-1 font-bold ${
                  result.expectedAdditionalReturn >= 0
                    ? "text-primary-700 dark:text-primary-300"
                    : "text-red-600 dark:text-red-400"
                }`}
              >
                {formatINR(result.expectedAdditionalReturn)}{t("common.perQuintal")}
              </dd>
            </div>
          </dl>

          <div>
            <h2 className="text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
              {t("recommendation.reason")}
            </h2>
            <p className="mt-1.5 text-sm leading-relaxed text-soil-700 dark:text-soil-200">{result.reason}</p>
          </div>

          <p className="text-xs text-soil-500 dark:text-soil-400">⚖️ {result.disclaimer}</p>
        </div>
      )}

      {/* History */}
      <section aria-label={t("recommendation.history")}>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
          {t("recommendation.history")}
        </h2>
        {!history || history.length === 0 ? (
          <LoadingState rows={1} />
        ) : (
          <ul className="space-y-2">
            {history.map((item, index) => (
              <li
                key={`${item.cropId}-${index}`}
                className="card flex flex-wrap items-center justify-between gap-3 p-4"
              >
                <span className="flex items-center gap-3">
                  <span className="chip font-bold">{item.recommendation}</span>
                  <span className="text-sm font-medium">
                    {item.cropName} · {formatINR(item.currentPrice)}
                  </span>
                </span>
                <span className="flex items-center gap-3 text-xs text-soil-500 dark:text-soil-400">
                  <RiskBadge risk={item.risk} />
                  <TrendIndicator value={item.trendChangePct} />
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
