import { useCallback, useState } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useCropSelection } from "@/store/CropContext";
import { cropService } from "@/services/cropService";
import { fertilizerService } from "@/services/fertilizerService";
import { useToast } from "@/components/ui/Toast";
import { LoadingState, ErrorState, EducationalBadge } from "@/components/common/states";
import { ApiError } from "@/services/apiClient";
import type {
  FertilizerGuidance,
  MLFertilizerPredictionRequest,
  MLFertilizerPredictionResponse,
} from "@/types/api";

const GROWTH_STAGES = [
  "SOWING",
  "VEGETATIVE",
  "FLOWERING",
  "GRAIN_FILLING",
  "FRUITING",
  "HARVEST_READY",
] as const;

const SOIL_CONDITIONS = ["LOAMY", "SANDY", "CLAY", "SALINE", "BLACK"] as const;

const ML_SOILS = ["Black", "Clayey", "Loamy", "Red", "Sandy"] as const;
const ML_SEASONS = ["Kharif", "Rabi", "Zaid"] as const;

const ML_CROPS_BY_SEASON: Record<string, { id: string; name: string }[]> = {
  Kharif: [
    { id: "rice", name: "Rice / Paddy" },
    { id: "maize", name: "Maize / Makka" },
    { id: "cotton", name: "Cotton / Kapas" },
    { id: "jute", name: "Jute / Patson" },
    { id: "pigeonpeas", name: "Pigeonpeas / Arhar" },
    { id: "blackgram", name: "Black Gram / Urad" },
    { id: "mothbeans", name: "Moth Beans / Matki" },
    { id: "mungbean", name: "Mungbean / Moong" },
    { id: "kidneybeans", name: "Kidney Beans / Rajma" },
    { id: "brinjal", name: "Brinjal / Eggplant" },
    { id: "okra", name: "Okra / Bhindi" },
  ],
  Rabi: [
    { id: "wheat", name: "Wheat / Gehun" },
    { id: "mustard", name: "Mustard / Sarson" },
    { id: "chickpea", name: "Chickpea / Chana" },
    { id: "potato", name: "Potato / Aloo" },
    { id: "lentil", name: "Lentil / Masoor" },
    { id: "cauliflower", name: "Cauliflower / Gobhi" },
    { id: "cabbage", name: "Cabbage / Patta Gobhi" },
    { id: "carrot", name: "Carrot / Gajar" },
    { id: "onion", name: "Onion / Pyaaz" },
    { id: "peas", name: "Peas / Matar" },
    { id: "tomato", name: "Tomato / Tamatar" },
  ],
  Zaid: [
    { id: "watermelon", name: "Watermelon / Tarbooz" },
    { id: "cucumber", name: "Cucumber / Kheera" },
    { id: "muskmelon", name: "Muskmelon / Kharbooja" },
  ],
};

interface Preset {
  id: string;
  name: string;
  badge: string;
  values: MLFertilizerPredictionRequest;
}

const PRESETS: Preset[] = [
  {
    id: "rice-kharif",
    name: "Rice · Kharif High-N",
    badge: "Kharif • Clayey",
    values: {
      crop: "rice",
      season: "Kharif",
      soilType: "Clayey",
      nitrogen: 35,
      phosphorous: 18,
      potassium: 12,
      temperature: 26,
      humidity: 70,
      moisture: 35,
    },
  },
  {
    id: "cotton-kharif",
    name: "Cotton · Black Soil Balanced",
    badge: "Kharif • Black",
    values: {
      crop: "cotton",
      season: "Kharif",
      soilType: "Black",
      nitrogen: 42,
      phosphorous: 32,
      potassium: 40,
      temperature: 29,
      humidity: 65,
      moisture: 30,
    },
  },
  {
    id: "wheat-rabi",
    name: "Wheat · Rabi Starter Root",
    badge: "Rabi • Loamy",
    values: {
      crop: "wheat",
      season: "Rabi",
      soilType: "Loamy",
      nitrogen: 22,
      phosphorous: 65,
      potassium: 28,
      temperature: 18,
      humidity: 45,
      moisture: 40,
    },
  },
  {
    id: "watermelon-zaid",
    name: "Watermelon · Summer High-K",
    badge: "Zaid • Sandy",
    values: {
      crop: "watermelon",
      season: "Zaid",
      soilType: "Sandy",
      nitrogen: 18,
      phosphorous: 42,
      potassium: 52,
      temperature: 33,
      humidity: 50,
      moisture: 25,
    },
  },
];

export default function FertilizerPage() {
  const { t } = useI18n();
  const { showToast } = useToast();
  const { season: activeGlobalSeason, cropId, setCrop } = useCropSelection();

  // Mode Selection: "api" (Default) vs "ml"
  const [activeTab, setActiveTab] = useState<"api" | "ml">("api");

  // --- API-Based Recommendation State ---
  const [growthStage, setGrowthStage] = useState<string>("VEGETATIVE");
  const [soilCondition, setSoilCondition] = useState<string>("LOAMY");
  const [npk, setNpk] = useState("");
  const [guidance, setGuidance] = useState<FertilizerGuidance | null>(null);
  const [submittingApi, setSubmittingApi] = useState(false);

  const fetchCrops = useCallback(() => cropService.catalog(activeGlobalSeason), [activeGlobalSeason]);
  const { data: crops, loading: cropsLoading, error: cropsError, refetch } = useApiQuery(
    fetchCrops,
    [activeGlobalSeason]
  );

  const activeCropId = cropId ?? crops?.[0]?.id ?? "";

  const submitApi = async () => {
    if (!activeCropId || submittingApi) return;
    setSubmittingApi(true);
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
      setSubmittingApi(false);
    }
  };

  // --- ML-Based Prediction State ---
  const [mlSeason, setMlSeason] = useState<string>("Kharif");
  const [mlCrop, setMlCrop] = useState<string>("rice");
  const [mlSoilType, setMlSoilType] = useState<string>("Clayey");
  const [nitrogen, setNitrogen] = useState<number>(35);
  const [phosphorous, setPhosphorous] = useState<number>(18);
  const [potassium, setPotassium] = useState<number>(12);
  const [temperature, setTemperature] = useState<number>(26);
  const [humidity, setHumidity] = useState<number>(70);
  const [moisture, setMoisture] = useState<number>(35);

  const [mlPrediction, setMlPrediction] = useState<MLFertilizerPredictionResponse | null>(null);
  const [submittingMl, setSubmittingMl] = useState(false);

  const handleSeasonChange = (newSeason: string) => {
    setMlSeason(newSeason);
    const available = ML_CROPS_BY_SEASON[newSeason];
    if (available && available.length > 0) {
      setMlCrop(available[0].id);
    }
  };

  const applyPreset = (preset: Preset) => {
    setMlSeason(preset.values.season);
    setMlCrop(preset.values.crop);
    setMlSoilType(preset.values.soilType);
    setNitrogen(preset.values.nitrogen);
    setPhosphorous(preset.values.phosphorous);
    setPotassium(preset.values.potassium);
    setTemperature(preset.values.temperature);
    setHumidity(preset.values.humidity);
    setMoisture(preset.values.moisture);
    showToast(`Applied "${preset.name}" preset`, "info");
  };

  const submitMl = async () => {
    if (submittingMl) return;
    setSubmittingMl(true);
    try {
      const res = await fertilizerService.mlPredict({
        crop: mlCrop,
        season: mlSeason,
        soilType: mlSoilType,
        nitrogen: Number(nitrogen),
        phosphorous: Number(phosphorous),
        potassium: Number(potassium),
        temperature: Number(temperature),
        humidity: Number(humidity),
        moisture: Number(moisture),
      });
      setMlPrediction(res.data);
      showToast(`Predicted: ${res.data.prediction} (${res.data.confidencePct}% confidence)`, "success");
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : t("common.error"), "error");
    } finally {
      setSubmittingMl(false);
    }
  };

  if (cropsLoading) return <LoadingState />;
  if (cropsError) return <ErrorState message={cropsError.message} onRetry={() => void refetch()} />;

  return (
    <div className="space-y-6">
      {/* Header & Mode Switcher */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="font-display text-2xl font-extrabold text-soil-900 dark:text-soil-50">
            {t("fertilizer.title")}
          </h1>
          <p className="mt-1 text-sm text-soil-600 dark:text-soil-400">
            {activeTab === "api" ? t("fertilizer.tabApiDesc") : t("fertilizer.tabMlDesc")}
          </p>
        </div>

        {/* Partition Tabs */}
        <div className="inline-flex rounded-xl bg-soil-100 p-1.5 shadow-inner dark:bg-soil-800">
          <button
            type="button"
            onClick={() => setActiveTab("api")}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition-all ${
              activeTab === "api"
                ? "bg-white text-primary-700 shadow-sm dark:bg-soil-900 dark:text-primary-400"
                : "text-soil-600 hover:text-soil-900 dark:text-soil-400 dark:hover:text-soil-200"
            }`}
          >
            <span>🌿</span>
            <span>{t("fertilizer.tabApi")}</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("ml")}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition-all ${
              activeTab === "ml"
                ? "bg-white text-emerald-700 shadow-sm dark:bg-soil-900 dark:text-emerald-400"
                : "text-soil-600 hover:text-soil-900 dark:text-soil-400 dark:hover:text-soil-200"
            }`}
          >
            <span>🤖</span>
            <span>{t("fertilizer.tabMl")}</span>
          </button>
        </div>
      </div>

      {/* =========================================================================
          TAB 1: API-Based Recommendation (Preserved Rule/Knowledge-Based System)
          ========================================================================= */}
      {activeTab === "api" && (
        <div className="space-y-6">
          <div className="card space-y-4 p-6">
            <div className="flex items-center justify-between border-b border-soil-100 pb-3 dark:border-soil-800">
              <div>
                <h2 className="font-display text-base font-bold text-soil-900 dark:text-soil-100">
                  {t("fertilizer.tabApi")}
                </h2>
                <p className="text-xs text-soil-500 dark:text-soil-400">{t("fertilizer.tabApiDesc")}</p>
              </div>
              <EducationalBadge />
            </div>

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

            <button
              type="button"
              className="btn-primary flex items-center justify-center gap-2"
              onClick={() => void submitApi()}
              disabled={submittingApi || !activeCropId}
            >
              {submittingApi ? (
                <span>{t("common.loading")}</span>
              ) : (
                <span>{t("fertilizer.recommend")}</span>
              )}
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
              <p className="text-sm leading-relaxed text-soil-700 dark:text-soil-200">
                {guidance.guidance}
              </p>
              <p className="text-xs text-soil-500 dark:text-soil-400">{guidance.sourceNote}</p>
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          TAB 2: ML-Based Fertilizer Prediction (XGBoost Classifier)
          ========================================================================= */}
      {activeTab === "ml" && (
        <div className="space-y-6">
          {/* Quick Test Presets */}
          <div className="rounded-2xl border border-emerald-100 bg-emerald-50/60 p-4 dark:border-emerald-900/40 dark:bg-emerald-950/20">
            <p className="text-xs font-bold uppercase tracking-wider text-emerald-800 dark:text-emerald-300">
              ⚡ {t("fertilizer.mlPresets")}
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {PRESETS.map((preset) => (
                <button
                  key={preset.id}
                  type="button"
                  onClick={() => applyPreset(preset)}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-white px-3 py-1.5 text-xs font-medium text-emerald-800 shadow-sm transition hover:bg-emerald-100 dark:border-emerald-800 dark:bg-soil-900 dark:text-emerald-200 dark:hover:bg-emerald-950"
                >
                  <span>{preset.name}</span>
                  <span className="rounded bg-emerald-100 px-1.5 py-0.5 text-[10px] text-emerald-700 dark:bg-emerald-900/60 dark:text-emerald-300">
                    {preset.badge}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* ML Prediction Form */}
          <div className="card space-y-5 p-6">
            <div className="flex items-center justify-between border-b border-soil-100 pb-3 dark:border-soil-800">
              <div>
                <h2 className="font-display text-base font-bold text-soil-900 dark:text-soil-100">
                  {t("fertilizer.tabMl")}
                </h2>
                <p className="text-xs text-soil-500 dark:text-soil-400">
                  XGBoost 39-feature multi-class classification model
                </p>
              </div>
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300">
                XGBoost ML Engine
              </span>
            </div>

            {/* Categorical Dimensions */}
            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <label htmlFor="ml-season" className="label">
                  {t("fertilizer.season")}
                </label>
                <select
                  id="ml-season"
                  className="input cursor-pointer"
                  value={mlSeason}
                  onChange={(e) => handleSeasonChange(e.target.value)}
                >
                  {ML_SEASONS.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="ml-crop" className="label">
                  {t("fertilizer.crop")}
                </label>
                <select
                  id="ml-crop"
                  className="input cursor-pointer"
                  value={mlCrop}
                  onChange={(e) => setMlCrop(e.target.value)}
                >
                  {(ML_CROPS_BY_SEASON[mlSeason] ?? []).map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="ml-soil" className="label">
                  {t("fertilizer.soilType")}
                </label>
                <select
                  id="ml-soil"
                  className="input cursor-pointer"
                  value={mlSoilType}
                  onChange={(e) => setMlSoilType(e.target.value)}
                >
                  {ML_SOILS.map((soil) => (
                    <option key={soil} value={soil}>
                      {soil}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Soil Nutrients N-P-K */}
            <div className="rounded-xl border border-soil-200 bg-soil-50/50 p-4 dark:border-soil-800 dark:bg-soil-900/40">
              <p className="text-xs font-bold uppercase tracking-wider text-soil-600 dark:text-soil-300">
                🌱 Soil Nutrients (NPK)
              </p>
              <div className="mt-3 grid gap-4 sm:grid-cols-3">
                <div>
                  <div className="flex items-center justify-between">
                    <label htmlFor="ml-nitrogen" className="label">
                      {t("fertilizer.nitrogen")}
                    </label>
                    <span className="text-xs font-bold text-soil-700 dark:text-soil-300">{nitrogen}</span>
                  </div>
                  <input
                    id="ml-nitrogen"
                    type="number"
                    min="0"
                    max="250"
                    className="input mt-1"
                    value={nitrogen}
                    onChange={(e) => setNitrogen(Math.max(0, Number(e.target.value)))}
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between">
                    <label htmlFor="ml-phosphorous" className="label">
                      {t("fertilizer.phosphorous")}
                    </label>
                    <span className="text-xs font-bold text-soil-700 dark:text-soil-300">{phosphorous}</span>
                  </div>
                  <input
                    id="ml-phosphorous"
                    type="number"
                    min="0"
                    max="250"
                    className="input mt-1"
                    value={phosphorous}
                    onChange={(e) => setPhosphorous(Math.max(0, Number(e.target.value)))}
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between">
                    <label htmlFor="ml-potassium" className="label">
                      {t("fertilizer.potassium")}
                    </label>
                    <span className="text-xs font-bold text-soil-700 dark:text-soil-300">{potassium}</span>
                  </div>
                  <input
                    id="ml-potassium"
                    type="number"
                    min="0"
                    max="250"
                    className="input mt-1"
                    value={potassium}
                    onChange={(e) => setPotassium(Math.max(0, Number(e.target.value)))}
                  />
                </div>
              </div>
            </div>

            {/* Environmental & Soil Moisture */}
            <div className="rounded-xl border border-soil-200 bg-soil-50/50 p-4 dark:border-soil-800 dark:bg-soil-900/40">
              <p className="text-xs font-bold uppercase tracking-wider text-soil-600 dark:text-soil-300">
                🌤️ Environmental & Moisture
              </p>
              <div className="mt-3 grid gap-4 sm:grid-cols-3">
                <div>
                  <div className="flex items-center justify-between">
                    <label htmlFor="ml-temperature" className="label">
                      {t("fertilizer.temperature")}
                    </label>
                    <span className="text-xs font-bold text-soil-700 dark:text-soil-300">{temperature}°C</span>
                  </div>
                  <input
                    id="ml-temperature"
                    type="number"
                    min="-5"
                    max="55"
                    className="input mt-1"
                    value={temperature}
                    onChange={(e) => setTemperature(Number(e.target.value))}
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between">
                    <label htmlFor="ml-humidity" className="label">
                      {t("fertilizer.humidity")}
                    </label>
                    <span className="text-xs font-bold text-soil-700 dark:text-soil-300">{humidity}%</span>
                  </div>
                  <input
                    id="ml-humidity"
                    type="number"
                    min="0"
                    max="100"
                    className="input mt-1"
                    value={humidity}
                    onChange={(e) => setHumidity(Math.min(100, Math.max(0, Number(e.target.value))))}
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between">
                    <label htmlFor="ml-moisture" className="label">
                      {t("fertilizer.moisture")}
                    </label>
                    <span className="text-xs font-bold text-soil-700 dark:text-soil-300">{moisture}%</span>
                  </div>
                  <input
                    id="ml-moisture"
                    type="number"
                    min="0"
                    max="100"
                    className="input mt-1"
                    value={moisture}
                    onChange={(e) => setMoisture(Math.min(100, Math.max(0, Number(e.target.value))))}
                  />
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="button"
              className="btn-primary flex w-full items-center justify-center gap-2 bg-emerald-600 py-3 font-bold text-white hover:bg-emerald-700"
              onClick={() => void submitMl()}
              disabled={submittingMl}
            >
              {submittingMl ? (
                <>
                  <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  <span>{t("fertilizer.mlPredicting")}</span>
                </>
              ) : (
                <>
                  <span>🧪</span>
                  <span>{t("fertilizer.mlPredict")}</span>
                </>
              )}
            </button>
          </div>

          {/* ML Prediction Result Card */}
          {mlPrediction && (
            <div className="card space-y-5 border-2 border-emerald-500/30 p-6" aria-live="polite">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-soil-100 pb-3 dark:border-soil-800">
                <div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                    {t("fertilizer.mlPredictionTitle")}
                  </span>
                  <h3 className="font-display text-2xl font-extrabold text-soil-900 dark:text-soil-50">
                    {mlPrediction.prediction}
                  </h3>
                </div>
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-emerald-100 px-3 py-1 text-sm font-bold text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-200">
                    {mlPrediction.confidencePct}% {t("fertilizer.confidence")}
                  </span>
                  <EducationalBadge />
                </div>
              </div>

              {/* Based On Parameter Tag Summary */}
              {mlPrediction.inputSummary && (
                <div className="rounded-xl bg-soil-100/70 p-3.5 text-xs text-soil-700 dark:bg-soil-800/60 dark:text-soil-300">
                  <span className="font-bold text-soil-900 dark:text-soil-100">
                    {t("fertilizer.basedOn")}:{" "}
                  </span>
                  <span className="capitalize">{mlPrediction.inputSummary.crop}</span> •{" "}
                  <span>{mlPrediction.inputSummary.season}</span> •{" "}
                  <span>{mlPrediction.inputSummary.soilType} Soil</span> ·{" "}
                  <span className="font-semibold">N: {mlPrediction.inputSummary.nitrogen}</span> ·{" "}
                  <span className="font-semibold">P: {mlPrediction.inputSummary.phosphorous}</span> ·{" "}
                  <span className="font-semibold">K: {mlPrediction.inputSummary.potassium}</span> ·{" "}
                  <span>Temp: {mlPrediction.inputSummary.temperature}°C</span> ·{" "}
                  <span>Humidity: {mlPrediction.inputSummary.humidity}%</span> ·{" "}
                  <span>Moisture: {mlPrediction.inputSummary.moisture}%</span>
                </div>
              )}

              {/* Agronomic Profile */}
              {mlPrediction.profile && (
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-xl bg-emerald-50 p-4 dark:bg-emerald-950/30">
                    <dt className="text-xs font-semibold uppercase tracking-wide text-emerald-800 dark:text-emerald-300">
                      {t("fertilizer.npkRatio")}
                    </dt>
                    <dd className="mt-1 font-bold text-soil-900 dark:text-soil-100">
                      {mlPrediction.profile.npkRatio}
                    </dd>
                    <p className="mt-2 text-xs leading-relaxed text-soil-600 dark:text-soil-300">
                      {mlPrediction.profile.primaryFunction}
                    </p>
                  </div>

                  <div className="rounded-xl bg-soil-50 p-4 dark:bg-soil-800/50">
                    <dt className="text-xs font-semibold uppercase tracking-wide text-soil-600 dark:text-soil-400">
                      {t("fertilizer.applicationAdvice")}
                    </dt>
                    <dd className="mt-1 text-xs leading-relaxed text-soil-700 dark:text-soil-300">
                      {mlPrediction.profile.applicationAdvice}
                    </dd>
                  </div>
                </div>
              )}

              {/* Class Probability Distribution */}
              {mlPrediction.probabilities && mlPrediction.probabilities.length > 0 && (
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-soil-500 dark:text-soil-400">
                    {t("fertilizer.probabilities")}
                  </p>
                  <div className="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-4">
                    {mlPrediction.probabilities.map((item) => (
                      <div
                        key={item.fertilizer}
                        className={`rounded-lg p-2.5 text-xs transition-colors ${
                          item.fertilizer === mlPrediction.prediction
                            ? "border border-emerald-300 bg-emerald-100/70 font-bold text-emerald-900 dark:border-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-200"
                            : "bg-soil-100/50 text-soil-600 dark:bg-soil-800/40 dark:text-soil-400"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span>{item.fertilizer}</span>
                          <span>{(item.probability * 100).toFixed(1)}%</span>
                        </div>
                        <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-soil-200 dark:bg-soil-700">
                          <div
                            className={`h-full rounded-full ${
                              item.fertilizer === mlPrediction.prediction
                                ? "bg-emerald-600 dark:bg-emerald-400"
                                : "bg-soil-400 dark:bg-soil-500"
                            }`}
                            style={{ width: `${Math.max(4, item.probability * 100)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Educational Disclaimer */}
              <p className="text-xs text-soil-500 dark:text-soil-400">{mlPrediction.disclaimer}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
