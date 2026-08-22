import { useCallback, useState } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useCropSelection } from "@/store/CropContext";
import { cropService } from "@/services/cropService";
import { fertilizerService } from "@/services/fertilizerService";
import { useToast } from "@/components/ui/Toast";
import { LoadingState, ErrorState, EducationalBadge } from "@/components/common/states";
import { ApiError } from "@/services/apiClient";
import type { FertilizerGuidance } from "@/types/api";

const GROWTH_STAGES = ["SOWING", "VEGETATIVE", "FLOWERING", "GRAIN_FILLING", "FRUITING", "HARVEST_READY"] as const;
const SOIL_CONDITIONS = ["LOAMY", "SANDY", "CLAY", "SALINE", "BLACK"] as const;

export default function FertilizerPage() {
  const { t } = useI18n();
  const { showToast } = useToast();
  const { season, cropId, setCrop } = useCropSelection();

  const [growthStage, setGrowthStage] = useState<string>("VEGETATIVE");
  const [soilCondition, setSoilCondition] = useState<string>("LOAMY");
  const [npk, setNpk] = useState("");
  const [guidance, setGuidance] = useState<FertilizerGuidance | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const fetchCrops = useCallback(() => cropService.catalog(season), [season]);
  const { data: crops, loading, error, refetch } = useApiQuery(fetchCrops, [season]);

  const activeCropId = cropId ?? crops?.[0]?.id ?? "";

  const submit = async () => {
    if (!activeCropId || submitting) return;
    setSubmitting(true);
    try {
      const result = await fertilizerService.guidance({
        cropId: activeCropId,
        growthStage,
        soilCondition,
        npk: npk.trim() || undefined,
      });
      setGuidance(result.data);
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : t("common.error"), "error");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error.message} onRetry={() => void refetch()} />;

  return (
    <div className="space-y-6">
      <h1 className="font-display text-2xl font-extrabold">{t("fertilizer.title")}</h1>

      <div className="card space-y-4 p-6">
        <div>
          <label htmlFor="fert-crop" className="label">
            {t("common.selectCrop")}
          </label>
          <select
            id="fert-crop"
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

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="fert-stage" className="label">
              {t("fertilizer.growthStage")}
            </label>
            <select
              id="fert-stage"
              className="input cursor-pointer"
              value={growthStage}
              onChange={(event) => setGrowthStage(event.target.value)}
            >
              {GROWTH_STAGES.map((stage) => (
                <option key={stage} value={stage}>
                  {stage.replace("_", " ")}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="fert-soil" className="label">
              {t("fertilizer.soilCondition")}
            </label>
            <select
              id="fert-soil"
              className="input cursor-pointer"
              value={soilCondition}
              onChange={(event) => setSoilCondition(event.target.value)}
            >
              {SOIL_CONDITIONS.map((soil) => (
                <option key={soil} value={soil}>
                  {soil}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label htmlFor="fert-npk" className="label">
            {t("fertilizer.npk")}
          </label>
          <input
            id="fert-npk"
            className="input"
            placeholder={t("fertilizer.npkPlaceholder")}
            value={npk}
            onChange={(event) => setNpk(event.target.value)}
          />
        </div>

        <button type="button" className="btn-primary" onClick={() => void submit()} disabled={submitting || !activeCropId}>
          {t("fertilizer.recommend")}
        </button>
      </div>

      {guidance && (
        <div className="card space-y-4 p-6" aria-live="polite">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="font-display text-lg font-bold">
              {guidance.crop} · {guidance.growthStage.replace("_", " ")}
            </h2>
            <EducationalBadge />
          </div>
          <dl className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl bg-primary-50 p-4 dark:bg-primary-900/30">
              <dt className="text-xs font-semibold uppercase tracking-wide text-primary-700 dark:text-primary-300">
                {t("fertilizer.category")}
              </dt>
              <dd className="mt-1 font-semibold">{guidance.recommendedCategory}</dd>
            </div>
            <div className="rounded-xl bg-soil-50 p-4 dark:bg-soil-800/60">
              <dt className="text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
                {t("fertilizer.timing")}
              </dt>
              <dd className="mt-1 text-sm">{guidance.applicationTiming}</dd>
            </div>
          </dl>
          {guidance.soilNote && (
            <p className="text-sm text-soil-600 dark:text-soil-300">🌱 {guidance.soilNote}</p>
          )}
          <p className="text-sm leading-relaxed text-soil-700 dark:text-soil-200">{guidance.guidance}</p>
          <p className="text-xs text-soil-500 dark:text-soil-400">{guidance.sourceNote}</p>
        </div>
      )}
    </div>
  );
}
