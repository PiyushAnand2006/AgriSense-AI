import { useState, useCallback, useEffect } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { useApiQuery } from "@/hooks/useApiQuery";
import { cropRecommendationService } from "@/services/cropRecommendationService";
import { weatherService } from "@/services/weatherService";
import { useToast } from "@/components/ui/Toast";
import { LoadingState } from "@/components/common/states";
import { ApiError } from "@/services/apiClient";
import type {
  CropRecommendationInput,
  CropRecommendationResult,
  PresetItem,
} from "@/types/api";

const DEFAULT_INPUTS: CropRecommendationInput = {
  nitrogen: 90,
  phosphorus: 42,
  potassium: 43,
  temperature: 24.5,
  humidity: 82.0,
  ph: 6.5,
  rainfall: 202.9,
};

export default function CropRecommendationPage() {
  const { t } = useI18n();
  const { showToast } = useToast();

  const [form, setForm] = useState<CropRecommendationInput>(DEFAULT_INPUTS);
  const [result, setResult] = useState<CropRecommendationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetchingWeather, setFetchingWeather] = useState(false);

  // Fetch presets & model info
  const fetchPresets = useCallback(() => cropRecommendationService.presets(), []);
  const { data: presets } = useApiQuery(fetchPresets, []);

  const fetchModelInfo = useCallback(() => cropRecommendationService.modelInfo(), []);
  const { data: modelInfo } = useApiQuery(fetchModelInfo, []);

  // Run initial prediction on load
  useEffect(() => {
    let mounted = true;
    async function initialPredict() {
      try {
        const res = await cropRecommendationService.predict(DEFAULT_INPUTS);
        if (mounted) setResult(res.data);
      } catch {
        // quiet fallback
      }
    }
    void initialPredict();
    return () => {
      mounted = false;
    };
  }, []);

  const handleInputChange = (field: keyof CropRecommendationInput, val: number) => {
    setForm((prev) => ({ ...prev, [field]: val }));
  };

  const applyPreset = (preset: PresetItem) => {
    setForm(preset.values);
    showToast(`${preset.title} loaded`, "info");
  };

  const autofillLiveWeather = async () => {
    setFetchingWeather(true);
    try {
      const res = await weatherService.current();
      if (res.data?.today) {
        const today = res.data.today;
        setForm((prev) => ({
          ...prev,
          temperature: today.temperatureC,
          humidity: today.humidityPct,
          rainfall: today.rainProbability > 0 ? Math.round(today.rainProbability * 2.2) : prev.rainfall,
        }));
        showToast(
          `Weather synced: ${today.temperatureC}°C, ${today.humidityPct}% humidity`,
          "success"
        );
      }
    } catch {
      showToast("Could not fetch live weather. Using default values.", "error");
    } finally {
      setFetchingWeather(false);
    }
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const response = await cropRecommendationService.predict(form);
      setResult(response.data);
      showToast(
        `Top Recommended Crop: ${response.data.cropLabel} (${response.data.confidence}%)`,
        "success"
      );
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : t("common.error"), "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Title and Model Badge */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-extrabold text-soil-950 dark:text-white">
            {t("cropRec.title")}
          </h1>
          <p className="mt-1 text-sm text-soil-600 dark:text-soil-300">
            {t("cropRec.subtitle")}
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-primary-300 bg-primary-50 px-3.5 py-1.5 text-xs font-semibold text-primary-800 dark:border-primary-700 dark:bg-primary-900/40 dark:text-primary-200">
          <span className="flex h-2 w-2 rounded-full bg-primary-500 animate-pulse" />
          <span>Random Forest Tuned · 99.3% Accuracy</span>
        </div>
      </div>

      {/* Preset Chips and Live Weather Auto-fill bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-soil-200 bg-white p-4 shadow-sm dark:border-soil-800 dark:bg-soil-900">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-soil-500 dark:text-soil-400">
            {t("cropRec.presets")}:
          </span>
          {(presets ?? []).map((preset) => (
            <button
              key={preset.id}
              type="button"
              onClick={() => applyPreset(preset)}
              className="rounded-lg border border-soil-200 bg-soil-50 px-2.5 py-1 text-xs font-medium text-soil-700 transition hover:border-primary-500 hover:bg-primary-50 hover:text-primary-700 dark:border-soil-700 dark:bg-soil-800 dark:text-soil-200 dark:hover:border-primary-400 dark:hover:bg-primary-950"
            >
              {preset.title}
            </button>
          ))}
        </div>
        <button
          type="button"
          onClick={() => void autofillLiveWeather()}
          disabled={fetchingWeather}
          className="btn-secondary !py-1.5 !text-xs"
        >
          {fetchingWeather ? "Syncing…" : "🌤️ " + t("cropRec.useLiveWeather")}
        </button>
      </div>

      {/* Main Grid: Input Form + Result View */}
      <div className="grid gap-6 lg:grid-cols-12">
        {/* Left Column: Soil & Climate Input Form */}
        <form
          onSubmit={(e) => void handleSubmit(e)}
          className="card space-y-5 p-6 lg:col-span-6"
        >
          <div className="flex items-center justify-between border-b border-soil-100 pb-3 dark:border-soil-800">
            <h2 className="font-display text-base font-bold text-soil-950 dark:text-white">
              {t("cropRec.soilAndClimate")}
            </h2>
            <button
              type="button"
              onClick={() => setForm(DEFAULT_INPUTS)}
              className="text-xs font-medium text-soil-500 hover:text-soil-800 dark:hover:text-soil-200"
            >
              {t("cropRec.resetValues")}
            </button>
          </div>

          {/* Soil Nutrients Section */}
          <div className="space-y-4">
            <p className="text-xs font-bold uppercase tracking-wider text-primary-700 dark:text-primary-400">
              🧪 {t("cropRec.soilNutrients")} (NPK in kg/ha)
            </p>

            {/* Nitrogen */}
            <div>
              <div className="flex justify-between text-xs">
                <label htmlFor="input-n" className="font-semibold text-soil-700 dark:text-soil-200">
                  {t("cropRec.nitrogen")} (N)
                </label>
                <span className="font-mono font-bold text-primary-600 dark:text-primary-400">
                  {form.nitrogen} kg/ha
                </span>
              </div>
              <input
                id="input-n"
                type="range"
                min="0"
                max="160"
                step="1"
                value={form.nitrogen}
                onChange={(e) => handleInputChange("nitrogen", Number(e.target.value))}
                className="w-full accent-primary-600"
              />
              <div className="flex justify-between text-[10px] text-soil-400">
                <span>0 (Low)</span>
                <span>80 (Optimal)</span>
                <span>160 (High)</span>
              </div>
            </div>

            {/* Phosphorus */}
            <div>
              <div className="flex justify-between text-xs">
                <label htmlFor="input-p" className="font-semibold text-soil-700 dark:text-soil-200">
                  {t("cropRec.phosphorus")} (P)
                </label>
                <span className="font-mono font-bold text-primary-600 dark:text-primary-400">
                  {form.phosphorus} kg/ha
                </span>
              </div>
              <input
                id="input-p"
                type="range"
                min="5"
                max="150"
                step="1"
                value={form.phosphorus}
                onChange={(e) => handleInputChange("phosphorus", Number(e.target.value))}
                className="w-full accent-primary-600"
              />
              <div className="flex justify-between text-[10px] text-soil-400">
                <span>5</span>
                <span>75</span>
                <span>150</span>
              </div>
            </div>

            {/* Potassium */}
            <div>
              <div className="flex justify-between text-xs">
                <label htmlFor="input-k" className="font-semibold text-soil-700 dark:text-soil-200">
                  {t("cropRec.potassium")} (K)
                </label>
                <span className="font-mono font-bold text-primary-600 dark:text-primary-400">
                  {form.potassium} kg/ha
                </span>
              </div>
              <input
                id="input-k"
                type="range"
                min="5"
                max="210"
                step="1"
                value={form.potassium}
                onChange={(e) => handleInputChange("potassium", Number(e.target.value))}
                className="w-full accent-primary-600"
              />
              <div className="flex justify-between text-[10px] text-soil-400">
                <span>5</span>
                <span>100</span>
                <span>210</span>
              </div>
            </div>

            {/* Soil pH */}
            <div>
              <div className="flex justify-between text-xs">
                <label htmlFor="input-ph" className="font-semibold text-soil-700 dark:text-soil-200">
                  {t("cropRec.phValue")} (pH: 0 - 14)
                </label>
                <span className="font-mono font-bold text-primary-600 dark:text-primary-400">
                  {form.ph.toFixed(1)} {form.ph < 6.0 ? "(Acidic)" : form.ph > 7.5 ? "(Alkaline)" : "(Neutral)"}
                </span>
              </div>
              <input
                id="input-ph"
                type="range"
                min="3.5"
                max="9.5"
                step="0.1"
                value={form.ph}
                onChange={(e) => handleInputChange("ph", Number(e.target.value))}
                className="w-full accent-primary-600"
              />
              <div className="flex justify-between text-[10px] text-soil-400">
                <span>3.5 (Acidic)</span>
                <span>6.5 - 7.5 (Optimal)</span>
                <span>9.5 (Alkaline)</span>
              </div>
            </div>
          </div>

          {/* Climate & Weather Section */}
          <div className="space-y-4 border-t border-soil-100 pt-4 dark:border-soil-800">
            <p className="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400">
              ⛅ {t("cropRec.climateParameters")}
            </p>

            <div className="grid grid-cols-2 gap-3">
              {/* Temperature */}
              <div>
                <label htmlFor="input-temp" className="label text-xs">
                  {t("cropRec.temperature")} (°C)
                </label>
                <input
                  id="input-temp"
                  type="number"
                  step="0.1"
                  min="0"
                  max="55"
                  value={form.temperature}
                  onChange={(e) => handleInputChange("temperature", Number(e.target.value))}
                  className="input !py-1.5 text-sm"
                />
              </div>

              {/* Humidity */}
              <div>
                <label htmlFor="input-humidity" className="label text-xs">
                  {t("cropRec.humidity")} (%)
                </label>
                <input
                  id="input-humidity"
                  type="number"
                  step="0.5"
                  min="0"
                  max="100"
                  value={form.humidity}
                  onChange={(e) => handleInputChange("humidity", Number(e.target.value))}
                  className="input !py-1.5 text-sm"
                />
              </div>
            </div>

            {/* Rainfall */}
            <div>
              <div className="flex justify-between text-xs">
                <label htmlFor="input-rainfall" className="font-semibold text-soil-700 dark:text-soil-200">
                  {t("cropRec.rainfall")} (mm)
                </label>
                <span className="font-mono font-bold text-amber-600 dark:text-amber-400">
                  {form.rainfall} mm
                </span>
              </div>
              <input
                id="input-rainfall"
                type="range"
                min="20"
                max="300"
                step="1"
                value={form.rainfall}
                onChange={(e) => handleInputChange("rainfall", Number(e.target.value))}
                className="w-full accent-amber-600"
              />
              <div className="flex justify-between text-[10px] text-soil-400">
                <span>20 mm (Arid)</span>
                <span>150 mm (Moderate)</span>
                <span>300 mm (Heavy)</span>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full !py-3 text-base font-bold shadow-md transition"
          >
            {loading ? "Analyzing Soil & Climate…" : "🌾 " + t("cropRec.predictButton")}
          </button>
        </form>

        {/* Right Column: Prediction Results & Agronomic Guidance */}
        <div className="space-y-6 lg:col-span-6">
          {loading && <LoadingState rows={3} />}

          {!loading && result && (
            <div className="space-y-5" aria-live="polite">
              {/* Primary Champion Recommendation Card */}
              <div className="relative overflow-hidden rounded-2xl border-2 border-primary-500/30 bg-gradient-to-br from-primary-50/80 via-white to-soil-50/50 p-6 shadow-lg dark:from-primary-950/40 dark:via-soil-900 dark:to-soil-950">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-primary-600 px-3 py-1 text-xs font-bold uppercase tracking-wider text-white">
                      🌟 {t("cropRec.primaryRecommendation")}
                    </span>
                    <h3 className="mt-2 font-display text-3xl font-black capitalize text-soil-950 dark:text-white">
                      {result.agronomicGuide.icon} {result.cropLabel}
                    </h3>
                    <p className="mt-0.5 text-xs text-soil-500 dark:text-soil-400">
                      Scientific prediction: <strong>{result.recommendedCrop}</strong>
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="inline-flex flex-col items-end rounded-2xl bg-white/90 px-4 py-2 shadow-sm dark:bg-soil-800/90">
                      <span className="text-[11px] font-semibold text-soil-500 dark:text-soil-400">
                        {t("cropRec.confidence")}
                      </span>
                      <span className="font-display text-2xl font-extrabold text-primary-600 dark:text-primary-400">
                        {result.confidence}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Confidence Bar */}
                <div className="mt-4">
                  <div className="h-2.5 w-full overflow-hidden rounded-full bg-soil-200 dark:bg-soil-800">
                    <div
                      className="h-full rounded-full bg-primary-600 transition-all duration-700 ease-out"
                      style={{ width: `${Math.min(result.confidence, 100)}%` }}
                    />
                  </div>
                </div>

                {/* Agronomic Badges */}
                <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
                  <div className="rounded-xl bg-white/80 p-3 shadow-sm dark:bg-soil-800/80">
                    <p className="text-[10px] font-semibold uppercase text-soil-500 dark:text-soil-400">
                      {t("crops.season")}
                    </p>
                    <p className="mt-1 text-xs font-bold text-soil-900 dark:text-soil-100">
                      {result.agronomicGuide.season}
                    </p>
                  </div>
                  <div className="rounded-xl bg-white/80 p-3 shadow-sm dark:bg-soil-800/80">
                    <p className="text-[10px] font-semibold uppercase text-soil-500 dark:text-soil-400">
                      {t("crops.duration")}
                    </p>
                    <p className="mt-1 text-xs font-bold text-soil-900 dark:text-soil-100">
                      {result.agronomicGuide.growthDurationDays}
                    </p>
                  </div>
                  <div className="rounded-xl bg-white/80 p-3 shadow-sm dark:bg-soil-800/80">
                    <p className="text-[10px] font-semibold uppercase text-soil-500 dark:text-soil-400">
                      {t("cropRec.waterNeeds")}
                    </p>
                    <p className="mt-1 text-xs font-bold text-soil-900 dark:text-soil-100">
                      {result.agronomicGuide.waterRequirement.split("(")[0]}
                    </p>
                  </div>
                  <div className="rounded-xl bg-white/80 p-3 shadow-sm dark:bg-soil-800/80">
                    <p className="text-[10px] font-semibold uppercase text-soil-500 dark:text-soil-400">
                      {t("cropRec.soilType")}
                    </p>
                    <p className="mt-1 truncate text-xs font-bold text-soil-900 dark:text-soil-100">
                      {result.agronomicGuide.soilType.split(",")[0]}
                    </p>
                  </div>
                </div>

                {/* Cultivation Guidance Accordion/Box */}
                <div className="mt-5 space-y-3 rounded-xl border border-soil-200/80 bg-white/90 p-4 text-xs dark:border-soil-800 dark:bg-soil-900/90">
                  <div>
                    <h4 className="font-bold text-primary-700 dark:text-primary-300">
                      💡 {t("cropRec.fertilizerGuidance")}
                    </h4>
                    <p className="mt-1 leading-relaxed text-soil-700 dark:text-soil-300">
                      {result.agronomicGuide.fertilizerTip}
                    </p>
                  </div>
                  <div className="border-t border-soil-100 pt-2 dark:border-soil-800">
                    <h4 className="font-bold text-soil-800 dark:text-soil-200">
                      📋 {t("cropRec.agronomicAdvisory")}
                    </h4>
                    <p className="mt-1 leading-relaxed text-soil-600 dark:text-soil-400">
                      {result.agronomicGuide.advisoryNote}
                    </p>
                  </div>
                </div>
              </div>

              {/* Alternative Viable Crops */}
              {result.alternatives && result.alternatives.length > 0 && (
                <div className="card p-5">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-soil-500 dark:text-soil-400">
                    🔄 {t("cropRec.alternativeCrops")}
                  </h3>
                  <p className="mt-1 text-xs text-soil-500 dark:text-soil-400">
                    {t("cropRec.alternativesDescription")}
                  </p>
                  <div className="mt-3 grid gap-3 sm:grid-cols-3">
                    {result.alternatives.map((alt) => (
                      <div
                        key={alt.crop}
                        className="rounded-xl border border-soil-200 bg-soil-50 p-3 text-center dark:border-soil-800 dark:bg-soil-800/60"
                      >
                        <p className="text-sm font-bold capitalize text-soil-950 dark:text-white">
                          {alt.cropLabel}
                        </p>
                        <div className="mt-2 flex items-center justify-center gap-1.5">
                          <div className="h-2 w-16 overflow-hidden rounded-full bg-soil-200 dark:bg-soil-700">
                            <div
                              className="h-full bg-primary-500"
                              style={{ width: `${Math.min(alt.probability * 3, 100)}%` }}
                            />
                          </div>
                          <span className="font-mono text-xs font-bold text-primary-600 dark:text-primary-400">
                            {alt.probability}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Model Transparency info card */}
              <div className="rounded-xl border border-soil-200 bg-soil-50/70 p-4 text-xs text-soil-500 dark:border-soil-800 dark:bg-soil-900/50 dark:text-soil-400">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-soil-700 dark:text-soil-300">
                    ⚙️ {modelInfo?.modelName ?? "Random Forest Tuned"}
                  </span>
                  <span>Accuracy: {modelInfo?.testAccuracy ?? 99.32}%</span>
                </div>
                <p className="mt-1">
                  Trained on 2,200 agricultural trial records covering 22 crop classes under multi-variable soil chemistry and climate observations.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
