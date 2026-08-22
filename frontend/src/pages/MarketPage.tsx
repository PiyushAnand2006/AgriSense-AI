import { useCallback, useEffect, useState } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useDebounce } from "@/hooks/useDebounce";
import { marketService } from "@/services/marketService";
import { LoadingState, ErrorState, EmptyState, OfflineBanner } from "@/components/common/states";
import { SearchBar, SortSelect, Select } from "@/components/ui/controls";
import { TrendIndicator } from "@/components/common/badges";
import { formatINR, formatDate } from "@/utils/format";
import type { MarketTrend, PriceHistory } from "@/types/api";

export default function MarketPage() {
  const { t } = useI18n();
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 350);
  const [sort, setSort] = useState("name");
  const [stateFilter, setStateFilter] = useState("");
  const [page, setPage] = useState(1);

  const [detailCropId, setDetailCropId] = useState<string | null>(null);
  const [trend, setTrend] = useState<MarketTrend | null>(null);
  const [history, setHistory] = useState<PriceHistory | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => setPage(1), [debouncedSearch, sort, stateFilter]);

  const fetchBoard = useCallback(
    () =>
      marketService.priceBoard({
        search: debouncedSearch || undefined,
        sort,
        state: stateFilter || undefined,
        page,
        limit: 12,
      }),
    [debouncedSearch, sort, stateFilter, page],
  );
  const {
    data: prices,
    loading,
    error,
    stale,
    fetchedAt,
    refetch,
  } = useApiQuery(fetchBoard, [debouncedSearch, sort, stateFilter, page]);

  const fetchMarkets = useCallback(() => marketService.markets(), []);
  const { data: markets } = useApiQuery(fetchMarkets, []);
  const states = [...new Set((markets ?? []).map((market) => market.state))].sort();

  const openDetail = async (cropId: string, marketId: string) => {
    setDetailCropId(cropId);
    setDetailLoading(true);
    setTrend(null);
    setHistory(null);
    try {
      const [trendResult, historyResult] = await Promise.all([
        marketService.trend(cropId, marketId, 30),
        marketService.priceHistory(cropId, marketId, 90),
      ]);
      setTrend(trendResult.data);
      setHistory(historyResult.data);
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h1 className="font-display text-2xl font-extrabold">{t("market.title")}</h1>
        {prices?.[0] && (
          <p className="text-xs text-soil-500 dark:text-soil-400">
            {t("market.source")}: {prices[0].source} · {t("market.lastSynced")}: {formatDate(prices[0].lastUpdated)}
          </p>
        )}
      </div>

      {stale && <OfflineBanner fetchedAt={fetchedAt} />}

      {/* Filters */}
      <div className="card flex flex-wrap items-end gap-3 p-4">
        <SearchBar value={search} onChange={setSearch} placeholder={t("common.search")} label={t("common.search")} />
        <SortSelect
          value={sort}
          onChange={setSort}
          label={t("common.sort")}
          options={[
            { value: "name", label: t("common.sort") + ": A-Z" },
            { value: "price_desc", label: "₹ ↓" },
            { value: "price_asc", label: "₹ ↑" },
            { value: "change_desc", label: "% ↓" },
          ]}
        />
        <div className="min-w-40">
          <Select
            id="state-filter"
            value={stateFilter}
            onChange={(value) => setStateFilter(value)}
            label="State"
            options={[{ value: "", label: t("common.all") }, ...states.map((s) => ({ value: s, label: s }))]}
          />
        </div>
      </div>

      {/* Price board */}
      {loading ? (
        <LoadingState rows={3} />
      ) : error ? (
        <ErrorState message={error.message} onRetry={() => void refetch()} />
      ) : !prices || prices.length === 0 ? (
        <EmptyState description={t("marketplace.empty")} />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] border-separate border-spacing-y-2 text-sm">
            <caption className="sr-only">{t("market.priceBoard")}</caption>
            <thead>
              <tr className="text-left text-xs uppercase tracking-wide text-soil-500 dark:text-soil-400">
                <th scope="col" className="px-4 py-2">{t("common.selectCrop")}</th>
                <th scope="col" className="px-4 py-2">{t("common.selectMarket")}</th>
                <th scope="col" className="px-4 py-2 text-right">{t("market.currentPrice")}</th>
                <th scope="col" className="px-4 py-2 text-right">{t("market.range")}</th>
                <th scope="col" className="px-4 py-2 text-right">{t("market.trend7")}</th>
                <th scope="col" className="px-4 py-2 text-right">{t("market.trend30")}</th>
                <th scope="col" className="px-4 py-2" aria-hidden />
              </tr>
            </thead>
            <tbody>
              {prices.map((price) => (
                <tr key={`${price.cropId}-${price.marketId}`} className="card [&>td]:first:rounded-l-xl [&>td]:last:rounded-r-xl">
                  <td className="bg-white px-4 py-3 font-semibold dark:bg-soil-900">{price.cropName}</td>
                  <td className="bg-white px-4 py-3 text-soil-600 dark:bg-soil-900 dark:text-soil-300">
                    {price.marketName}
                  </td>
                  <td className="bg-white px-4 py-3 text-right font-bold dark:bg-soil-900">
                    {formatINR(price.modalPrice)}
                    <span className="ml-1 text-xs font-normal text-soil-500">{t("common.perQuintal")}</span>
                  </td>
                  <td className="bg-white px-4 py-3 text-right text-xs text-soil-500 dark:bg-soil-900 dark:text-soil-400">
                    {formatINR(price.minPrice)} – {formatINR(price.maxPrice)}
                  </td>
                  <td className="bg-white px-4 py-3 text-right dark:bg-soil-900">
                    <TrendIndicator value={price.trend7d} />
                  </td>
                  <td className="bg-white px-4 py-3 text-right dark:bg-soil-900">
                    <TrendIndicator value={price.trend30d} />
                  </td>
                  <td className="bg-white px-4 py-3 text-right dark:bg-soil-900">
                    <button
                      type="button"
                      className="btn-secondary !py-1.5 !text-xs"
                      onClick={() => void openDetail(price.cropId, price.marketId)}
                    >
                      {t("market.trends")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {prices && prices.length === 12 && (
        <nav aria-label="Pagination" className="flex justify-center">
          <button type="button" className="btn-secondary" onClick={() => setPage((p) => p + 1)}>
            {t("common.next")} →
          </button>
        </nav>
      )}

      {/* Trend + history detail */}
      {detailCropId && (
        <section className="card p-6" aria-label={t("market.trends")}>
          <div className="mb-4 flex items-start justify-between gap-3">
            <h2 className="font-display text-lg font-bold">
              {t("market.trends")} · {trend?.cropName ?? detailCropId} @ {trend?.marketName}
            </h2>
            <button type="button" className="btn-secondary !py-1.5 !text-xs" onClick={() => setDetailCropId(null)}>
              {t("common.close")}
            </button>
          </div>

          {detailLoading ? (
            <LoadingState rows={1} />
          ) : trend ? (
            <div className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-4">
                <div>
                  <p className="text-xs text-soil-500 dark:text-soil-400">{t("market.currentPrice")}</p>
                  <p className="text-lg font-bold">{formatINR(trend.currentPrice)}</p>
                </div>
                <div>
                  <p className="text-xs text-soil-500 dark:text-soil-400">{t("market.direction")} ({trend.days}d)</p>
                  <p className={`text-lg font-bold ${trend.direction === "UP" ? "text-primary-700 dark:text-primary-300" : trend.direction === "DOWN" ? "text-red-600 dark:text-red-400" : ""}`}>
                    {trend.direction} <TrendIndicator value={trend.changePct} />
                  </p>
                </div>
                <div>
                  <p className="text-xs text-soil-500 dark:text-soil-400">{t("market.trend7")}</p>
                  <TrendIndicator value={trend.trend7d} />
                </div>
                <div>
                  <p className="text-xs text-soil-500 dark:text-soil-400">{t("market.trend30")}</p>
                  <TrendIndicator value={trend.trend30d} />
                </div>
              </div>

              {/* 90-day modal price chart */}
              {history && history.history.length > 0 && (
                <div>
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
                    {t("market.history")} (90d)
                  </p>
                  <div className="flex h-40 items-end gap-0.5" role="img" aria-label={t("market.history")}>
                    {history.history.map((point) => {
                      const values = history.history.map((p) => p.modalPrice);
                      const min = Math.min(...values);
                      const max = Math.max(...values);
                      const height = max === min ? 50 : 6 + ((point.modalPrice - min) / (max - min)) * 94;
                      return (
                        <span
                          key={point.date}
                          title={`${formatDate(point.date)}: ${formatINR(point.modalPrice)} (${t("market.range")} ${formatINR(point.minPrice)}–${formatINR(point.maxPrice)})`}
                          className="flex-1 rounded-t bg-primary-400/70 hover:bg-primary-600 dark:bg-primary-500/60 dark:hover:bg-primary-400"
                          style={{ height: `${height}%` }}
                        />
                      );
                    })}
                  </div>
                </div>
              )}
              <p className="text-xs text-soil-500 dark:text-soil-400">ℹ️ {trend.note}</p>
            </div>
          ) : (
            <ErrorState />
          )}
        </section>
      )}
    </div>
  );
}
