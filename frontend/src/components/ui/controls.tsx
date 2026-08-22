import type { ChangeEvent, ReactNode } from "react";
import { useI18n } from "@/i18n/I18nProvider";

/** Debounced search input (caller passes the debounced onChange). */
export function SearchBar({
  value,
  onChange,
  placeholder,
  label,
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  label: string;
}) {
  return (
    <div className="relative w-full sm:max-w-xs">
      <label htmlFor="search-bar" className="sr-only">
        {label}
      </label>
      <svg
        aria-hidden
        className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-soil-400"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
      >
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-3.5-3.5" />
      </svg>
      <input
        id="search-bar"
        type="search"
        className="input pl-10"
        placeholder={placeholder ?? label}
        value={value}
        onChange={(event: ChangeEvent<HTMLInputElement>) => onChange(event.target.value)}
      />
    </div>
  );
}

export interface SortOption {
  value: string;
  label: string;
}

export function SortSelect({
  value,
  options,
  onChange,
  label,
}: {
  value: string;
  options: SortOption[];
  onChange: (value: string) => void;
  label: string;
}) {
  return (
    <div>
      <label htmlFor="sort-select" className="sr-only">
        {label}
      </label>
      <select
        id="sort-select"
        className="input min-w-[9.5rem] cursor-pointer"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

export function FilterPanel({ children, title }: { children: ReactNode; title: string }) {
  return (
    <div className="card p-4">
      <h3 className="mb-3 text-sm font-semibold text-soil-700 dark:text-soil-200">{title}</h3>
      <div className="flex flex-wrap gap-3">{children}</div>
    </div>
  );
}

export function Pagination({
  page,
  pageSize,
  total,
  onPageChange,
}: {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
}) {
  const { t } = useI18n();
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  if (totalPages <= 1) return null;

  return (
    <nav aria-label="Pagination" className="flex items-center justify-between gap-4">
      <button
        type="button"
        className="btn-secondary"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
      >
        ← {t("common.previous")}
      </button>
      <span className="text-sm text-soil-600 dark:text-soil-300">
        {page} / {totalPages}
      </span>
      <button
        type="button"
        className="btn-secondary"
        disabled={page >= totalPages}
        onClick={() => onPageChange(page + 1)}
      >
        {t("common.next")} →
      </button>
    </nav>
  );
}

export interface SelectOption {
  value: string;
  label: string;
}

export function Select({
  id,
  value,
  options,
  onChange,
  label,
  hint,
}: {
  id: string;
  value: string;
  options: SelectOption[];
  onChange: (value: string) => void;
  label: string;
  hint?: string;
}) {
  return (
    <div>
      <label htmlFor={id} className="label">
        {label}
      </label>
      <select
        id={id}
        className="input cursor-pointer"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {hint && <p className="mt-1 text-xs text-soil-500 dark:text-soil-400">{hint}</p>}
    </div>
  );
}
