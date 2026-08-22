import { useCallback, useState } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useCropSelection } from "@/store/CropContext";
import { cropService } from "@/services/cropService";
import { seasonService } from "@/services/seasonService";
import { useToast } from "@/components/ui/Toast";
import { LoadingState, ErrorState, EmptyState } from "@/components/common/states";
import { Modal } from "@/components/ui/primitives";
import { SearchBar } from "@/components/ui/controls";
import { SeasonBadge } from "@/components/common/badges";
import { ApiError } from "@/services/apiClient";
import type { FarmerCrop, FarmerCropInput } from "@/types/api";
import { formatDate } from "@/utils/format";

export default function CropsPage() {
  const { t } = useI18n();
  const { showToast } = useToast();
  const { season, cropId, setCrop } = useCropSelection();
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<FarmerCrop | null>(null);
  const [form, setForm] = useState<FarmerCropInput>({ cropId: "", farmSize: undefined, location: "" });
  const [submitting, setSubmitting] = useState(false);

  const fetchSeasonCrops = useCallback(
    () => seasonService.cropsBySeasonValue(season), [season],
  );
  const {
    data: seasonData,
    loading: catalogLoading,
    error: catalogError,
    refetch: refetchCatalog,
  } = useApiQuery(fetchSeasonCrops, [season]);

  const fetchMine = useCallback(() => cropService.myCrops(), []);
  const { data: mine, loading: mineLoading, error: mineError, refetch, setData } = useApiQuery(fetchMine, []);

  const crops = seasonData?.crops ?? [];
  const filtered = search
    ? crops.filter(
        (crop) =>
          crop.name.toLowerCase().includes(search.toLowerCase()) ||
          crop.id.includes(search.toLowerCase()),
      )
    : crops;

  const openCreate = () => {
    setEditing(null);
    setForm({ cropId: filtered[0]?.id ?? "", farmSize: undefined, location: "" });
    setModalOpen(true);
  };

  const openEdit = (planting: FarmerCrop) => {
    setEditing(planting);
    setForm({
      cropId: planting.cropId,
      plantingDate: planting.plantingDate ?? undefined,
      expectedHarvestDate: planting.expectedHarvestDate ?? undefined,
      farmSize: planting.farmSize ?? undefined,
      location: planting.location ?? "",
    });
    setModalOpen(true);
  };

  const submit = async () => {
    if (!form.cropId || submitting) return;
    setSubmitting(true);
    try {
      if (editing) {
        const result = await cropService.updatePlanting(editing.id, form);
        setData((current) =>
          (current ?? []).map((p) => (p.id === editing.id ? result.data : p)),
        );
        showToast(t("crops.editCrop"), "success");
      } else {
        const result = await cropService.createPlanting(form);
        setData((current) => [result.data, ...(current ?? [])]);
        showToast(t("crops.addCrop"), "success");
      }
      setModalOpen(false);
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : t("common.error"), "error");
    } finally {
      setSubmitting(false);
    }
  };

  const remove = async (planting: FarmerCrop) => {
    if (!window.confirm(t("crops.deleteConfirm"))) return;
    const previous = mine ?? [];
    // Optimistic delete with revert on failure.
    setData((current) => (current ?? []).filter((p) => p.id !== planting.id));
    try {
      await cropService.deletePlanting(planting.id);
      showToast(t("common.delete"), "success");
    } catch {
      setData(previous);
      showToast(t("common.error"), "error");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="font-display text-2xl font-extrabold">{t("crops.title")}</h1>
        <button type="button" className="btn-primary" onClick={openCreate}>
          + {t("crops.addCrop")}
        </button>
      </div>

      {/* My plantings */}
      <section aria-label={t("crops.title")}>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
          {t("crops.title")}
        </h2>
        {mineLoading ? (
          <LoadingState rows={2} />
        ) : mineError ? (
          <ErrorState message={mineError.message} onRetry={() => void refetch()} />
        ) : !mine || mine.length === 0 ? (
          <EmptyState description={t("crops.empty")} />
        ) : (
          <ul className="grid gap-4 sm:grid-cols-2">
            {mine.map((planting) => (
              <li
                key={planting.id}
                className={`card p-5 ${cropId === planting.cropId ? "ring-2 ring-primary-500" : ""}`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-display text-lg font-bold">{planting.crop?.name ?? planting.cropId}</p>
                    <SeasonBadge season={planting.season} />
                  </div>
                  <span className="chip bg-soil-100 text-soil-700 dark:bg-soil-800 dark:text-soil-200">
                    {planting.status}
                  </span>
                </div>
                <dl className="mt-3 grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <dt className="text-xs text-soil-500 dark:text-soil-400">{t("crops.plantingDate")}</dt>
                    <dd className="font-medium">{formatDate(planting.plantingDate)}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-soil-500 dark:text-soil-400">{t("crops.harvestDate")}</dt>
                    <dd className="font-medium">{formatDate(planting.expectedHarvestDate)}</dd>
                  </div>
                  {planting.farmSize != null && (
                    <div>
                      <dt className="text-xs text-soil-500 dark:text-soil-400">{t("crops.farmSize")}</dt>
                      <dd className="font-medium">{planting.farmSize}</dd>
                    </div>
                  )}
                  {planting.location && (
                    <div>
                      <dt className="text-xs text-soil-500 dark:text-soil-400">{t("crops.location")}</dt>
                      <dd className="font-medium">{planting.location}</dd>
                    </div>
                  )}
                </dl>
                <div className="mt-4 flex flex-wrap gap-2">
                  <button type="button" className="btn-secondary !py-1.5 !text-xs" onClick={() => setCrop(planting.cropId)}>
                    {t("common.selectCrop")}
                  </button>
                  <button type="button" className="btn-secondary !py-1.5 !text-xs" onClick={() => openEdit(planting)}>
                    {t("common.edit")}
                  </button>
                  <button
                    type="button"
                    className="btn-secondary !py-1.5 !text-xs !text-red-600 dark:!text-red-400"
                    onClick={() => void remove(planting)}
                  >
                    {t("common.delete")}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Season catalog */}
      <section aria-label={t("crops.catalogTitle")}>
        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
            {t("crops.catalogTitle")} · {seasonData?.season.name}
          </h2>
          <SearchBar value={search} onChange={setSearch} label={t("common.search")} />
        </div>
        {catalogLoading ? (
          <LoadingState rows={2} />
        ) : catalogError ? (
          <ErrorState message={catalogError.message} onRetry={() => void refetchCatalog()} />
        ) : (
          <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {filtered.map((crop) => (
              <li
                key={crop.id}
                className={`card cursor-pointer p-5 transition-shadow hover:shadow-card-hover ${
                  cropId === crop.id ? "ring-2 ring-primary-500" : ""
                }`}
                onClick={() => setCrop(crop.id)}
              >
                <p className="font-display text-lg font-bold">{crop.name}</p>
                <p className="text-xs italic text-soil-500 dark:text-soil-400">{crop.scientificName}</p>
                <p className="mt-2 line-clamp-2 text-sm text-soil-600 dark:text-soil-300">{crop.description}</p>
                <div className="mt-3 space-y-1 text-xs text-soil-500 dark:text-soil-400">
                  {crop.growingPeriodDays && (
                    <p>{t("crops.growingPeriod")}: ~{crop.growingPeriodDays} {t("crops.days")}</p>
                  )}
                  {crop.sowingWindow && (
                    <p>{t("crops.sowingWindow")}: {crop.sowingWindow} · {t("crops.harvestWindow")}: {crop.harvestWindow}</p>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? t("crops.editCrop") : t("crops.addCrop")}
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
            <label htmlFor="crop-select" className="label">
              {t("common.selectCrop")}
            </label>
            <select
              id="crop-select"
              className="input cursor-pointer"
              value={form.cropId}
              disabled={!!editing}
              onChange={(event) => setForm((f) => ({ ...f, cropId: event.target.value }))}
            >
              {crops.map((crop) => (
                <option key={crop.id} value={crop.id}>
                  {crop.name}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="planting-date" className="label">
                {t("crops.plantingDate")}
              </label>
              <input
                id="planting-date"
                type="date"
                className="input"
                value={form.plantingDate ?? ""}
                onChange={(event) => setForm((f) => ({ ...f, plantingDate: event.target.value || undefined }))}
              />
            </div>
            <div>
              <label htmlFor="harvest-date" className="label">
                {t("crops.harvestDate")}
              </label>
              <input
                id="harvest-date"
                type="date"
                className="input"
                value={form.expectedHarvestDate ?? ""}
                onChange={(event) =>
                  setForm((f) => ({ ...f, expectedHarvestDate: event.target.value || undefined }))
                }
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="farm-size" className="label">
                {t("crops.farmSize")}
              </label>
              <input
                id="farm-size"
                type="number"
                min="0"
                step="0.5"
                className="input"
                value={form.farmSize ?? ""}
                onChange={(event) =>
                  setForm((f) => ({ ...f, farmSize: event.target.value ? Number(event.target.value) : undefined }))
                }
              />
            </div>
            <div>
              <label htmlFor="location" className="label">
                {t("crops.location")}
              </label>
              <input
                id="location"
                className="input"
                value={form.location ?? ""}
                onChange={(event) => setForm((f) => ({ ...f, location: event.target.value }))}
              />
            </div>
          </div>
        </div>
      </Modal>
    </div>
  );
}
