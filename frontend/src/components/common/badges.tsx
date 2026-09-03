import type { Risk, Severity } from "@/types/api";

const SEVERITY_STYLES: Record<Severity, string> = {
  LOW: "bg-primary-100 text-primary-800 dark:bg-primary-900/50 dark:text-primary-200",
  MODERATE: "bg-accent-100 text-accent-800 dark:bg-accent-900/50 dark:text-accent-200",
  HIGH: "bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-200",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  const normalized = (severity.toUpperCase() as Severity) in SEVERITY_STYLES
    ? (severity.toUpperCase() as Severity)
    : "LOW";
  return <span className={`chip ${SEVERITY_STYLES[normalized]}`}>{normalized}</span>;
}

const RISK_STYLES: Record<Risk, string> = {
  LOW: "bg-primary-100 text-primary-800 dark:bg-primary-900/50 dark:text-primary-200",
  MEDIUM: "bg-accent-100 text-accent-800 dark:bg-accent-900/50 dark:text-accent-200",
  HIGH: "bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-200",
};

export function RiskBadge({ risk }: { risk: Risk }) {
  const normalized = (risk.toUpperCase() as Risk) in RISK_STYLES ? (risk.toUpperCase() as Risk) : "LOW";
  return <span className={`chip ${RISK_STYLES[normalized]}`}>{normalized} RISK</span>;
}

export function GradeBadge({ grade }: { grade: string }) {
  const styles: Record<string, string> = {
    A: "bg-primary-100 text-primary-800 dark:bg-primary-900/50 dark:text-primary-200",
    B: "bg-accent-100 text-accent-800 dark:bg-accent-900/50 dark:text-accent-200",
    C: "bg-soil-200 text-soil-700 dark:bg-soil-700 dark:text-soil-200",
  };
  return <span className={`chip ${styles[grade] ?? styles.C}`}>Grade {grade}</span>;
}

export function SeasonBadge({ season }: { season: string }) {
  const norm = season.toUpperCase();
  const style =
    norm === "RABI"
      ? "bg-sky-100 text-sky-800 dark:bg-sky-900/50 dark:text-sky-200"
      : norm === "KHARIF"
        ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-200"
        : "bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-200";
  return (
    <span className={`chip ${style}`}>
      {season}
    </span>
  );
}

export function TrendIndicator({ value }: { value: number }) {
  const up = value > 0;
  const flat = Math.abs(value) < 0.05;
  return (
    <span
      className={`inline-flex items-center gap-1 text-sm font-semibold ${
        flat
          ? "text-soil-500 dark:text-soil-400"
          : up
            ? "text-primary-700 dark:text-primary-300"
            : "text-red-600 dark:text-red-400"
      }`}
    >
      <span aria-hidden>{flat ? "→" : up ? "▲" : "▼"}</span>
      {`${up ? "+" : ""}${value.toFixed(1)}%`}
      <span className="sr-only">{flat ? "no change" : up ? "up" : "down"}</span>
    </span>
  );
}
