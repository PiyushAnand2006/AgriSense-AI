/**
 * Central API client.
 *
 * - Injects the Bearer token on every request
 * - Normalizes errors into ApiError
 * - Caches successful GET responses in localStorage so the UI can show
 *   last-known data when the network is unavailable (stale flag)
 *
 * UI components never call fetch directly — always through services.
 */
import { API_BASE_URL } from "@/config/api";

const TOKEN_KEY = "agrisense.token";
const CACHE_PREFIX = "agrisense.cache:";
const CACHE_TIMESTAMP_PREFIX = "agrisense.cacheAt:";

export class ApiError extends Error {
  status: number;
  detail?: string;

  constructor(status: number, message: string, detail?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export interface ApiResult<T> {
  data: T;
  stale: boolean;
  fetchedAt: number;
}

export const tokenStore = {
  get(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },
  set(token: string) {
    localStorage.setItem(TOKEN_KEY, token);
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY);
  },
};

export function clearApiCache(): void {
  const keysToRemove: string[] = [];
  for (let i = 0; i < localStorage.length; i += 1) {
    const key = localStorage.key(i);
    if (key && (key.startsWith(CACHE_PREFIX) || key.startsWith(CACHE_TIMESTAMP_PREFIX))) {
      keysToRemove.push(key);
    }
  }
  keysToRemove.forEach((key) => localStorage.removeItem(key));
}

function cacheKey(url: string): string {
  return CACHE_PREFIX + url;
}

function readCache<T>(url: string): T | null {
  try {
    const raw = localStorage.getItem(cacheKey(url));
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

function writeCache<T>(url: string, data: T): void {
  try {
    localStorage.setItem(cacheKey(url), JSON.stringify(data));
    localStorage.setItem(CACHE_TIMESTAMP_PREFIX + url, String(Date.now()));
  } catch {
    // localStorage full/unavailable — cache is best-effort only.
  }
}

export function cacheTimestamp(url: string): number {
  return Number(localStorage.getItem(CACHE_TIMESTAMP_PREFIX + url) ?? 0);
}

async function request<T>(
  method: "GET" | "POST" | "PATCH" | "DELETE",
  path: string,
  options?: { body?: unknown; formData?: FormData; cache?: boolean },
): Promise<ApiResult<T>> {
  const url = `${API_BASE_URL}${path}`;
  const useCache = options?.cache ?? method === "GET";
  const token = tokenStore.get();

  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options?.body !== undefined) headers["Content-Type"] = "application/json";

  try {
    const response = await fetch(url, {
      method,
      headers,
      body: options?.formData ?? (options?.body !== undefined ? JSON.stringify(options.body) : undefined),
    });

    if (response.status === 204) {
      return { data: undefined as T, stale: false, fetchedAt: Date.now() };
    }

    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      if (response.status === 401) {
        tokenStore.clear();
      }
      const detail =
        payload && typeof payload === "object" && "detail" in payload
          ? String((payload as { detail: unknown }).detail)
          : undefined;
      throw new ApiError(response.status, detail ?? `Request failed (${response.status})`, detail);
    }

    if (useCache) writeCache(path, payload);
    return { data: payload as T, stale: false, fetchedAt: Date.now() };
  } catch (error) {
    if (error instanceof ApiError) throw error;
    // Network failure — fall back to cache for GET-style reads.
    if (useCache) {
      const cached = readCache<T>(path);
      if (cached !== null) {
        return { data: cached, stale: true, fetchedAt: cacheTimestamp(path) };
      }
    }
    throw new ApiError(0, "Network unavailable. Check your connection and try again.");
  }
}

export const apiClient = {
  get: <T>(path: string, params?: Record<string, string | number | boolean | undefined>) => {
    let query = "";
    if (params) {
      const search = new URLSearchParams();
      for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null && value !== "") search.set(key, String(value));
      }
      const qs = search.toString();
      if (qs) query = `?${qs}`;
    }
    return request<T>("GET", `${path}${query}`);
  },
  post: <T>(path: string, body?: unknown) => request<T>("POST", path, { body, cache: false }),
  postForm: <T>(path: string, formData: FormData) =>
    request<T>("POST", path, { formData, cache: false }),
  patch: <T>(path: string, body?: unknown) => request<T>("PATCH", path, { body, cache: false }),
  delete: <T>(path: string) => request<T>("DELETE", path, { cache: false }),
};
