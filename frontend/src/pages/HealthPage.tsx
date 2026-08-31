import { useCallback, useMemo, useState } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { useApiQuery } from "@/hooks/useApiQuery";
import { useCropSelection } from "@/store/CropContext";
import { cropService } from "@/services/cropService";
import { healthService } from "@/services/healthService";
import { useToast } from "@/components/ui/Toast";
import { LoadingState, ErrorState, EmptyState, EducationalBadge } from "@/components/common/states";
import { SeverityBadge } from "@/components/common/badges";
import { Modal } from "@/components/ui/primitives";
import { ApiError } from "@/services/apiClient";
import type { DiseaseInfo, HealthRecordInput, PestInfo, Severity } from "@/types/api";
import { resolveImageUrl, timeAgo } from "@/utils/format";

type Tab = "diseases" | "pests" | "records";

export default function HealthPage() {
  const { t } = useI18n();
  const { showToast } = useToast();
  const { season, cropId, setCrop } = useCropSelection();

  const [tab, setTab] = useState<Tab>("diseases");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [logOpen, setLogOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [form, setForm] = useState<HealthRecordInput>({
    recordType: "DISEASE",
    name: "",
    severity: "LOW",
    notes: "",
    imageUrl: "",
  });
  const [uploading, setUploading] = useState(false);

  const fetchSeasonCrops = useCallback(() => cropService.catalog(season), [season]);
  const { data: crops } = useApiQuery(fetchSeasonCrops, [season]);

  const selectedCrop = useMemo(
    () => crops?.find((crop) => crop.id === cropId) ?? crops?.[0] ?? null,
    [crops, cropId],
  );
  const activeCropId = selectedCrop?.id ?? "";

  const fetchDiseases = useCallback(
    () => (activeCropId ? cropService.diseases(activeCropId) : Promise.resolve({ data: [] as DiseaseInfo[], stale: false, fetchedAt: 0 })),
    [activeCropId],
  );
  const { data: diseases, loading: diseasesLoading, error: diseasesError, refetch: refetchDiseases } =
    useApiQuery(fetchDiseases, [activeCropId]);

  const fetchPests = useCallback(
    () => (activeCropId ? cropService.pests(activeCropId) : Promise.resolve({ data: [] as PestInfo[], stale: false, fetchedAt: 0 })),
    [activeCropId],
  );
  const { data: pests, loading: pestsLoading, error: pestsError, refetch: refetchPests } =
    useApiQuery(fetchPests, [activeCropId]);

  const fetchRecords = useCallback(
    () => (activeCropId ? healthService.records(activeCropId) : Promise.resolve({ data: [], stale: false, fetchedAt: 0 })),
    [activeCropId],
  );
  const { data: records, loading: recordsLoading, error: recordsError, refetch: refetchRecords, setData: setRecords } =
    useApiQuery(fetchRecords, [activeCropId]);

  const upload = async (file: File) => {
    const localBlob = URL.createObjectURL(file);
    setPreviewUrl(localBlob);
    setUploading(true);
    try {
      const result = await healthService.uploadImage(file);
      setForm((f) => ({ ...f, imageUrl: result.data.url }));
      showToast(t("health.uploadPhoto"), "success");
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : t("common.error"), "error");
    } finally {
      setUploading(false);
    }
  };

  const handleCloseLog = useCallback(() => {
    setLogOpen(false);
    setPreviewUrl("");
  }, []);

  const submitRecord = async () => {
    if (!form.name.trim() || submitting) return;
    setSubmitting(true);
    try {
      const result = await healthService.logRecord(activeCropId, form);
      setRecords((current) => [result.data, ...(current ?? [])]);
      showToast(t("health.logRecord"), "success");
      handleCloseLog();
      setForm({ recordType: "DISEASE", name: "", severity: "LOW", notes: "", imageUrl: "" });
      setTab("records");
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : t("common.error"), "error");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteRecord = async (recordId: string) => {
    if (!activeCropId) return;
    setDeletingId(recordId);
    try {
      await healthService.deleteRecord(activeCropId, recordId);
      setRecords((current) => (current ?? []).filter((r) => r.id !== recordId));
      showToast(t("health.recordDeleted"), "success");
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : t("common.error"), "error");
    } finally {
      setDeletingId(null);
    }
  };

  const tabs: { id: Tab; label: string }[] = [
    { id: "diseases", label: t("health.browseTab") },
    { id: "pests", label: t("health.pestsTab") },
    { id: "records", label: t("health.recordsTab") },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h1 className="font-display text-2xl font-extrabold">{t("health.title")}</h1>
        <button
          type="button"
          className="btn-primary"
          onClick={() => {
            setForm({ recordType: "DISEASE", name: "", severity: "LOW", notes: "", imageUrl: "" });
            setPreviewUrl("");
            setLogOpen(true);
          }}
          disabled={!activeCropId}
        >
          + {t("health.logRecord")}
        </button>
      </div>

      {/* Crop picker */}
      <div className="card flex flex-wrap items-center gap-2 p-4">
        <label htmlFor="health-crop" className="text-sm font-semibold text-soil-700 dark:text-soil-200">
          {t("common.selectCrop")}:
        </label>
        <select
          id="health-crop"
          className="input max-w-xs cursor-pointer"
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

      {/* Tabs */}
      <div role="tablist" aria-label={t("health.title")} className="flex gap-1 rounded-xl bg-soil-100 p-1 dark:bg-soil-800">
        {tabs.map((item) => (
          <button
            key={item.id}
            role="tab"
            aria-selected={tab === item.id}
            type="button"
            className={`flex-1 rounded-lg px-3 py-2 text-sm font-bold transition-colors ${
              tab === item.id
                ? "bg-white text-primary-700 shadow-sm dark:bg-soil-950 dark:text-primary-300"
                : "text-soil-500 hover:text-soil-800 dark:text-soil-400 dark:hover:text-soil-200"
            }`}
            onClick={() => setTab(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>

      {tab === "diseases" &&
        (diseasesLoading ? (
          <LoadingState />
        ) : diseasesError ? (
          <ErrorState message={diseasesError.message} onRetry={() => void refetchDiseases()} />
        ) : !diseases || diseases.length === 0 ? (
          <EmptyState description={t("common.empty")} />
        ) : (
          <ul className="space-y-3" role="tabpanel">
            {diseases.map((disease) => (
              <InfoCard
                key={disease.id}
                id={disease.id}
                name={disease.name}
                expanded={expanded === disease.id}
                onToggle={() => setExpanded(expanded === disease.id ? null : disease.id)}
                symptoms={disease.knowledge.symptoms}
                recommendedAction={disease.knowledge.recommendedAction}
                treatment={disease.knowledge.treatment}
                organic={disease.knowledge.organicAlternatives}
                prevention={disease.knowledge.prevention}
                onLog={() => {
                  setForm((f) => ({ ...f, recordType: "DISEASE", name: disease.name }));
                  setPreviewUrl("");
                  setLogOpen(true);
                }}
              />
            ))}
          </ul>
        ))}

      {tab === "pests" &&
        (pestsLoading ? (
          <LoadingState />
        ) : pestsError ? (
          <ErrorState message={pestsError.message} onRetry={() => void refetchPests()} />
        ) : !pests || pests.length === 0 ? (
          <EmptyState description={t("common.empty")} />
        ) : (
          <ul className="space-y-3" role="tabpanel">
            {pests.map((pest) => (
              <InfoCard
                key={pest.id}
                id={pest.id}
                name={pest.name}
                expanded={expanded === pest.id}
                onToggle={() => setExpanded(expanded === pest.id ? null : pest.id)}
                symptoms={pest.knowledge.symptoms}
                recommendedAction={pest.knowledge.recommendedAction}
                treatment={pest.knowledge.treatment}
                organic={pest.knowledge.organicAlternatives}
                prevention={pest.knowledge.prevention}
                onLog={() => {
                  setForm((f) => ({ ...f, recordType: "PEST", name: pest.name }));
                  setPreviewUrl("");
                  setLogOpen(true);
                }}
              />
            ))}
          </ul>
        ))}

      {tab === "records" &&
        (recordsLoading ? (
          <LoadingState />
        ) : recordsError ? (
          <ErrorState message={recordsError.message} onRetry={() => void refetchRecords()} />
        ) : !records || records.length === 0 ? (
          <EmptyState description={t("health.noRecords")} />
        ) : (
          <ul className="space-y-3" role="tabpanel">
            {records.map((record) => (
              <li key={record.id} className="card flex flex-wrap items-center gap-4 p-5">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="font-display font-bold">{record.name}</p>
                    <SeverityBadge severity={record.severity} />
                    <span className="chip bg-soil-100 text-soil-700 dark:bg-soil-800 dark:text-soil-200">
                      {record.recordType}
                    </span>
                  </div>
                  {record.notes && (
                    <p className="mt-1 text-sm text-soil-600 dark:text-soil-300">{record.notes}</p>
                  )}
                  <p className="mt-1 text-xs text-soil-500 dark:text-soil-400">
                    {record.cropName} · {timeAgo(record.createdAt)}
                  </p>
                </div>
                {record.imageUrl && (
                  <img
                    src={resolveImageUrl(record.imageUrl)}
                    alt={record.name}
                    className="h-16 w-16 rounded-lg border border-soil-200 object-cover dark:border-soil-700 bg-soil-100 dark:bg-soil-800"
                    loading="lazy"
                    onError={(e) => {
                      (e.currentTarget as HTMLElement).style.display = "none";
                    }}
                  />
                )}
                <button
                  type="button"
                  onClick={() => void handleDeleteRecord(record.id)}
                  disabled={deletingId === record.id}
                  className="rounded-lg p-2 text-soil-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/40 dark:hover:text-red-400 transition-colors"
                  title={t("common.delete")}
                  aria-label={t("common.delete")}
                >
                  {deletingId === record.id ? (
                    <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-red-500 border-t-transparent" />
                  ) : (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6" />
                    </svg>
                  )}
                </button>
              </li>
            ))}
          </ul>
        ))}

      <Modal
        open={logOpen}
        onClose={handleCloseLog}
        title={t("health.logRecordTitle")}
        footer={
          <>
            <button type="button" className="btn-secondary" onClick={handleCloseLog}>
              {t("common.cancel")}
            </button>
            <button type="button" className="btn-primary" onClick={() => void submitRecord()} disabled={submitting}>
              {t("common.save")}
            </button>
          </>
        }
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="record-type" className="label">
                {t("health.recordType")}
              </label>
              <select
                id="record-type"
                className="input cursor-pointer"
                value={form.recordType}
                onChange={(event) =>
                  setForm((f) => ({ ...f, recordType: event.target.value as HealthRecordInput["recordType"] }))
                }
              >
                <option value="DISEASE">{t("health.browseTab")}</option>
                <option value="PEST">{t("health.pestsTab")}</option>
              </select>
            </div>
            <div>
              <label htmlFor="record-severity" className="label">
                {t("health.recordSeverity")}
              </label>
              <select
                id="record-severity"
                className="input cursor-pointer"
                value={form.severity}
                onChange={(event) => setForm((f) => ({ ...f, severity: event.target.value as Severity }))}
              >
                {(["LOW", "MODERATE", "HIGH"] as const).map((severity) => (
                  <option key={severity} value={severity}>
                    {severity}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label htmlFor="record-name" className="label">
              {t("health.recordName")}
            </label>
            <input
              id="record-name"
              className="input"
              value={form.name}
              onChange={(event) => setForm((f) => ({ ...f, name: event.target.value }))}
            />
          </div>
          <div>
            <label htmlFor="record-notes" className="label">
              {t("health.recordNotes")}
            </label>
            <textarea
              id="record-notes"
              className="input min-h-20"
              value={form.notes}
              onChange={(event) => setForm((f) => ({ ...f, notes: event.target.value }))}
            />
          </div>
          <div>
            <label htmlFor="record-photo" className="label">
              {t("health.uploadPhoto")} <span className="font-normal text-soil-500">({t("health.uploadHint")})</span>
            </label>
            <input
              id="record-photo"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="input"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) void upload(file);
              }}
            />
            {uploading && <p className="mt-1 text-xs text-soil-500">{t("common.loading")}</p>}
            {(previewUrl || form.imageUrl) && (
              <div className="mt-2 flex items-center gap-3">
                <img
                  src={previewUrl || resolveImageUrl(form.imageUrl)}
                  alt="Preview"
                  className="h-20 w-20 rounded-lg border border-soil-200 object-cover dark:border-soil-700 bg-soil-50 dark:bg-soil-800"
                />
                <button
                  type="button"
                  className="text-xs font-semibold text-red-600 hover:underline dark:text-red-400"
                  onClick={() => {
                    setPreviewUrl("");
                    setForm((f) => ({ ...f, imageUrl: "" }));
                  }}
                >
                  {t("health.removePhoto")}
                </button>
              </div>
            )}
          </div>
        </div>
      </Modal>
    </div>
  );
}

function InfoCard({
  id,
  name,
  expanded,
  onToggle,
  symptoms,
  recommendedAction,
  treatment,
  organic,
  prevention,
  onLog,
}: {
  id: string;
  name: string;
  expanded: boolean;
  onToggle: () => void;
  symptoms: string[];
  recommendedAction: string;
  treatment: string;
  organic: string;
  prevention: string[];
  onLog: () => void;
}) {
  const { t } = useI18n();
  return (
    <li className="card p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <button type="button" className="flex min-w-0 flex-1 items-center gap-3 text-left" onClick={onToggle} aria-expanded={expanded}>
          <span className="font-display text-lg font-bold">{name}</span>
          <span aria-hidden className="text-soil-400">{expanded ? "▲" : "▼"}</span>
        </button>
        <EducationalBadge />
        <button type="button" className="btn-secondary !py-1.5 !text-xs" onClick={onLog}>
          {t("health.logRecord")}
        </button>
      </div>

      {expanded && (
        <div className="mt-4 space-y-4 border-t border-soil-200 pt-4 dark:border-soil-800">
          <section>
            <h3 className="text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
              {t("health.symptoms")}
            </h3>
            <ul className="mt-1.5 list-inside list-disc text-sm text-soil-700 dark:text-soil-200">
              {symptoms.map((symptom) => (
                <li key={symptom}>{symptom}</li>
              ))}
            </ul>
          </section>
          <section>
            <h3 className="text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
              {t("health.recommendedAction")}
            </h3>
            <p className="mt-1 text-sm text-soil-700 dark:text-soil-200">{recommendedAction}</p>
          </section>
          <section className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-xl bg-soil-50 p-3 dark:bg-soil-800/60">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
                {t("health.treatment")}
              </h3>
              <p className="mt-1 text-sm text-soil-700 dark:text-soil-200">{treatment}</p>
            </div>
            <div className="rounded-xl bg-soil-50 p-3 dark:bg-soil-800/60">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
                {t("health.organicAlternatives")}
              </h3>
              <p className="mt-1 text-sm text-soil-700 dark:text-soil-200">{organic}</p>
            </div>
          </section>
          <section>
            <h3 className="text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
              {t("health.prevention")}
            </h3>
            <ul className="mt-1.5 flex flex-wrap gap-2">
              {prevention.map((item) => (
                <li key={item} className="chip bg-primary-50 text-primary-800 dark:bg-primary-900/40 dark:text-primary-200">
                  {item}
                </li>
              ))}
            </ul>
          </section>
          <p className="text-xs text-soil-500 dark:text-soil-400" id={`note-${id}`}>
            {t("health.sourceNote")}
          </p>
        </div>
      )}
    </li>
  );
}
