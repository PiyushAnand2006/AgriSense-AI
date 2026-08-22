import { useCallback, useEffect, useState } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useDebounce } from "@/hooks/useDebounce";
import { useAuth } from "@/auth/AuthProvider";
import { marketplaceService } from "@/services/marketplaceService";
import { cropService } from "@/services/cropService";
import { useToast } from "@/components/ui/Toast";
import {
  LoadingState,
  ErrorState,
  EmptyState,
} from "@/components/common/states";
import { SearchBar, SortSelect, Pagination } from "@/components/ui/controls";
import { Modal } from "@/components/ui/primitives";
import { GradeBadge } from "@/components/common/badges";
import { ApiError } from "@/services/apiClient";
import { formatINR, timeAgo } from "@/utils/format";
import type { ListingInput } from "@/types/api";

export default function MarketplacePage() {
  const { t } = useI18n();
  const { user } = useAuth();
  const { showToast } = useToast();

  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 350);
  const [cropFilter, setCropFilter] = useState("");
  const [gradeFilter, setGradeFilter] = useState("");
  const [sort, setSort] = useState("newest");
  const [page, setPage] = useState(1);

  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<ListingInput>({
    cropId: "",
    quantity: 10,
    unit: "quintal",
    askingPrice: 2000,
    qualityGrade: "A",
    location: "",
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => setPage(1), [debouncedSearch, cropFilter, gradeFilter, sort]);

  const fetchListings = useCallback(
    () =>
      marketplaceService.list({
        search: debouncedSearch || undefined,
        cropId: cropFilter || undefined,
        grade: gradeFilter || undefined,
        sort,
        page,
        pageSize: 12,
      }),
    [debouncedSearch, cropFilter, gradeFilter, sort, page],
  );
  const {
    data: listingPage,
    loading,
    error,
    refetch,
    setData,
  } = useApiQuery(fetchListings, [debouncedSearch, cropFilter, gradeFilter, sort, page]);

  const fetchCrops = useCallback(() => cropService.catalog(), []);
  const { data: crops } = useApiQuery(fetchCrops, []);

  const openCreate = () => {
    setForm({
      cropId: crops?.[0]?.id ?? "",
      quantity: 10,
      unit: "quintal",
      askingPrice: 2000,
      qualityGrade: "A",
      location: "",
    });
    setModalOpen(true);
  };

  const submit = async () => {
    if (!form.cropId || submitting) return;
    setSubmitting(true);
    try {
      // Optimistic: append locally, reconcile with server response.
      const result = await marketplaceService.create(form);
      setData((current) =>
        current
          ? { ...current, items: [result.data, ...current.items], total: current.total + 1 }
          : current,
      );
      showToast(t("marketplace.listingCreated"), "success");
      setModalOpen(false);
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : t("common.error"), "error");
    } finally {
      setSubmitting(false);
    }
  };

  const markSold = async (id: string) => {
    const previous = listingPage ?? null;
    setData((current) =>
      current
        ? { ...current, items: current.items.filter((item) => item.id !== id) }
        : current,
    );
    try {
      await marketplaceService.update(id, { status: "SOLD" });
      showToast(t("marketplace.sold"), "success");
    } catch {
      setData(() => previous);
      showToast(t("common.error"), "error");
    }
  };

  const listings = listingPage?.items ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h1 className="font-display text-2xl font-extrabold">{t("marketplace.title")}</h1>
        <button type="button" className="btn-primary" onClick={openCreate}>
          + {t("marketplace.createListing")}
        </button>
      </div>

      {/* Filters */}
      <div className="card flex flex-wrap items-end gap-3 p-4">
        <SearchBar value={search} onChange={setSearch} placeholder={t("common.search")} label={t("common.search")} />
        <div className="min-w-36">
          <label htmlFor="mp-crop" className="label">
            {t("common.selectCrop")}
          </label>
          <select
            id="mp-crop"
            className="input cursor-pointer"
            value={cropFilter}
            onChange={(event) => setCropFilter(event.target.value)}
          >
            <option value="">{t("common.all")}</option>
            {(crops ?? []).map((crop) => (
              <option key={crop.id} value={crop.id}>
                {crop.name}
              </option>
            ))}
          </select>
        </div>
        <div className="min-w-28">
          <label htmlFor="mp-grade" className="label">
            {t("marketplace.grade")}
          </label>
          <select
            id="mp-grade"
            className="input cursor-pointer"
            value={gradeFilter}
            onChange={(event) => setGradeFilter(event.target.value)}
          >
            <option value="">{t("common.all")}</option>
            {["A", "B", "C"].map((grade) => (
              <option key={grade} value={grade}>
                {grade}
              </option>
            ))}
          </select>
        </div>
        <SortSelect
          value={sort}
          onChange={setSort}
          label={t("common.sort")}
          options={[
            { value: "newest", label: t("common.sort") + ": ⏱" },
            { value: "price_asc", label: "₹ ↑" },
            { value: "price_desc", label: "₹ ↓" },
            { value: "quantity_desc", label: "kg ↓" },
          ]}
        />
      </div>

      {loading ? (
        <LoadingState rows={3} />
      ) : error ? (
        <ErrorState message={error.message} onRetry={() => void refetch()} />
      ) : listings.length === 0 ? (
        <EmptyState description={t("marketplace.empty")} />
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {listings.map((listing) => (
            <li key={listing.id} className="card flex flex-col p-5">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="font-display text-lg font-bold">{listing.cropName}</p>
                  <p className="text-xs text-soil-500 dark:text-soil-400">
                    {listing.farmerName} · {timeAgo(listing.createdAt)}
                  </p>
                </div>
                {listing.qualityGrade && <GradeBadge grade={listing.qualityGrade} />}
              </div>
              <dl className="mt-3 space-y-1.5 text-sm">
                <div className="flex justify-between">
                  <dt className="text-soil-500 dark:text-soil-400">{t("marketplace.quantity")}</dt>
                  <dd className="font-medium">
                    {listing.quantity} {listing.unit}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-soil-500 dark:text-soil-400">{t("marketplace.askingPrice")}</dt>
                  <dd className="font-bold text-primary-700 dark:text-primary-300">
                    {formatINR(listing.askingPrice)}
                    <span className="text-xs font-normal text-soil-500">/{listing.unit}</span>
                  </dd>
                </div>
                {listing.location && (
                  <div className="flex justify-between">
                    <dt className="text-soil-500 dark:text-soil-400">{t("marketplace.location")}</dt>
                    <dd className="font-medium">{listing.location}</dd>
                  </div>
                )}
              </dl>
              <div className="mt-4 flex items-center gap-2">
                {listing.farmerId === user?.id ? (
                  <button
                    type="button"
                    className="btn-secondary !py-1.5 !text-xs"
                    onClick={() => void markSold(listing.id)}
                  >
                    {t("marketplace.sold")}
                  </button>
                ) : (
                  <a
                    href={`mailto:farmer-${listing.farmerId.slice(0, 6)}@example.com?subject=${encodeURIComponent(
                      `${listing.cropName} listing`,
                    )}`}
                    className="btn-secondary !py-1.5 !text-xs"
                  >
                    {t("marketplace.contact")}
                  </a>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      {listingPage && (
        <Pagination
          page={listingPage.page}
          pageSize={listingPage.pageSize}
          total={listingPage.total}
          onPageChange={setPage}
        />
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={t("marketplace.createListing")}
        footer={
          <>
            <button type="button" className="btn-secondary" onClick={() => setModalOpen(false)}>
              {t("common.cancel")}
            </button>
            <button type="button" className="btn-primary" onClick={() => void submit()} disabled={submitting}>
              {t("common.save")}
            </button>
          </>
        }
      >
        <div className="space-y-4">
          <div>
            <label htmlFor="listing-crop" className="label">
              {t("common.selectCrop")}
            </label>
            <select
              id="listing-crop"
              className="input cursor-pointer"
              value={form.cropId}
              onChange={(event) => setForm((f) => ({ ...f, cropId: event.target.value }))}
            >
              {(crops ?? []).map((crop) => (
                <option key={crop.id} value={crop.id}>
                  {crop.name}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="listing-quantity" className="label">
                {t("marketplace.quantity")}
              </label>
              <input
                id="listing-quantity"
                type="number"
                min="0.5"
                step="0.5"
                className="input"
                value={form.quantity}
                onChange={(event) => setForm((f) => ({ ...f, quantity: Number(event.target.value) }))}
              />
            </div>
            <div>
              <label htmlFor="listing-price" className="label">
                {t("marketplace.askingPrice")} (₹)
              </label>
              <input
                id="listing-price"
                type="number"
                min="1"
                className="input"
                value={form.askingPrice}
                onChange={(event) => setForm((f) => ({ ...f, askingPrice: Number(event.target.value) }))}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="listing-grade" className="label">
                {t("marketplace.grade")}
              </label>
              <select
                id="listing-grade"
                className="input cursor-pointer"
                value={form.qualityGrade}
                onChange={(event) => setForm((f) => ({ ...f, qualityGrade: event.target.value }))}
              >
                {["A", "B", "C"].map((grade) => (
                  <option key={grade} value={grade}>
                    {grade}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="listing-location" className="label">
                {t("marketplace.location")}
              </label>
              <input
                id="listing-location"
                className="input"
                value={form.location}
                onChange={(event) => setForm((f) => ({ ...f, location: event.target.value }))}
              />
            </div>
          </div>
        </div>
      </Modal>
    </div>
  );
}
