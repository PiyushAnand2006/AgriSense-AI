import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "@/services/apiClient";

interface UseApiQueryResult<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  stale: boolean;
  fetchedAt: number;
  refetch: () => Promise<void>;
  setData: (updater: T | ((previous: T | null) => T | null)) => void;
}

/**
 * Minimal data-fetching hook with loading / error / stale (offline cache)
 * states and manual refetch. `fetcher` should be a service call returning
 * ApiResult<T>. Pass a stable reference (useCallback) to avoid loops.
 */
export function useApiQuery<T>(
  fetcher: () => Promise<{ data: T; stale: boolean; fetchedAt: number }>,
  deps: unknown[] = [],
): UseApiQueryResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [stale, setStale] = useState(false);
  const [fetchedAt, setFetchedAt] = useState(0);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  const run = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetcher();
      if (!mounted.current) return;
      setData(result.data);
      setStale(result.stale);
      setFetchedAt(result.fetchedAt);
    } catch (err) {
      if (!mounted.current) return;
      setError(err instanceof ApiError ? err : new ApiError(0, "Unexpected error"));
    } finally {
      if (mounted.current) setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    void run();
  }, [run]);

  const updateData = useCallback((updater: T | ((previous: T | null) => T | null)) => {
    setData((previous) =>
      typeof updater === "function" ? (updater as (p: T | null) => T | null)(previous) : updater,
    );
  }, []);

  return { data, loading, error, stale, fetchedAt, refetch: run, setData: updateData };
}
