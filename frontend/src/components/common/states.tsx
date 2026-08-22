import type { ReactNode } from "react";
import emptyState from "@/assets/empty-state.svg";
import errorState from "@/assets/error-state.svg";
import { useI18n } from "@/i18n/I18nProvider";
import { useOnlineStatus } from "@/hooks/useOnlineStatus";

export function LoadingState({ rows = 3, message }: { rows?: number; message?: string }) {
  const { t } = useI18n();
  return (
    <div role="status" aria-live="polite" className="space-y-4">
      <span className="sr-only">{message ?? t("common.loading")}</span>
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="card h-28 animate-pulse bg-soil-100/60 dark:bg-soil-800/60" />
      ))}
    </div>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  const { t } = useI18n();
  return (
    <div role="alert" className="card flex flex-col items-center gap-4 p-10 text-center">
      <img src={errorState} alt="" className="h-32" loading="lazy" />
      <div>
        <h3 className="font-display text-lg font-bold">{t("common.error")}</h3>
        {message && <p className="mt-1 text-sm text-soil-600 dark:text-soil-300">{message}</p>}
      </div>
      {onRetry && (
        <button type="button" className="btn-primary" onClick={onRetry}>
          {t("common.retry")}
        </button>
      )}
    </div>
  );
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title?: string;
  description?: string;
  action?: ReactNode;
}) {
  const { t } = useI18n();
  return (
    <div className="card flex flex-col items-center gap-4 p-10 text-center">
      <img src={emptyState} alt="" className="h-32" loading="lazy" />
      <div>
        <h3 className="font-display text-lg font-bold">{title ?? t("common.empty")}</h3>
        {description && (
          <p className="mt-1 max-w-md text-sm text-soil-600 dark:text-soil-300">{description}</p>
        )}
      </div>
      {action}
    </div>
  );
}

/** Offline banner shown when data comes from cache or browser is offline. */
export function OfflineBanner({ fetchedAt }: { fetchedAt?: number }) {
  const { t } = useI18n();
  const online = useOnlineStatus();
  if (online && !fetchedAt) return null;
  const time = fetchedAt ? new Date(fetchedAt).toLocaleString() : null;
  return (
    <div
      role="status"
      className="flex items-center gap-3 rounded-xl border border-accent-300 bg-accent-50 px-4 py-3 text-sm font-medium text-accent-800 dark:border-accent-700 dark:bg-accent-900/30 dark:text-accent-200"
    >
      <span aria-hidden className="text-base">
        ⚡
      </span>
      <span>
        {!online && <strong className="mr-1">{t("common.offline")} — </strong>}
        {t("common.offlineBanner")}
        {time && <span className="ml-1 font-normal opacity-80">({time})</span>}
      </span>
    </div>
  );
}

/** Label for educational information — required on all guidance content. */
export function EducationalBadge({ className = "" }: { className?: string }) {
  const { t } = useI18n();
  return (
    <span
      className={`chip border border-accent-300 bg-accent-50 text-accent-800 dark:border-accent-700 dark:bg-accent-900/40 dark:text-accent-200 ${className}`}
    >
      {t("common.educationalInfo")}
    </span>
  );
}

export function StaleDataNotice({ fetchedAt }: { fetchedAt: number }) {
  const { t } = useI18n();
  return (
    <p className="text-xs text-soil-500 dark:text-soil-400">
      {t("common.lastUpdated")}: {new Date(fetchedAt).toLocaleTimeString()}
    </p>
  );
}
