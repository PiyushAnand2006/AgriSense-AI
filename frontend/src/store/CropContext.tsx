import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { cropService } from "@/services/cropService";
import type { Crop, Season } from "@/types/api";

interface CropSelection {
  season: Season;
  cropId: string | null;
  setSeason: (season: Season) => void;
  setCrop: (cropId: string | null) => void;
}

const SEASON_KEY = "agrisense.season";
const CROP_KEY = "agrisense.crop";

const CropContext = createContext<CropSelection | null>(null);

export function CropProvider({ children }: { children: ReactNode }) {
  const [season, setSeasonState] = useState<Season>(() => {
    const stored = localStorage.getItem(SEASON_KEY);
    return stored === "KHARIF" ? "KHARIF" : stored === "ZAID" ? "ZAID" : "RABI";
  });
  const [cropId, setCropId] = useState<string | null>(() => localStorage.getItem(CROP_KEY));

  useEffect(() => {
    localStorage.setItem(SEASON_KEY, season);
  }, [season]);

  useEffect(() => {
    if (cropId) localStorage.setItem(CROP_KEY, cropId);
    else localStorage.removeItem(CROP_KEY);
  }, [cropId]);

  const setSeason = useCallback((next: Season) => {
    setSeasonState(next);
    setCropId(null); // switching season resets crop selection
  }, []);

  const setCrop = useCallback((next: string | null) => setCropId(next), []);

  const value = useMemo(
    () => ({ season, cropId, setSeason, setCrop }),
    [season, cropId, setSeason, setCrop],
  );
  return <CropContext.Provider value={value}>{children}</CropContext.Provider>;
}

export function useCropSelection(): CropSelection {
  const context = useContext(CropContext);
  if (!context) throw new Error("useCropSelection must be used within CropProvider");
  return context;
}

/** Convenience hook for components needing the full catalog. */
export function useCropCatalog(season?: Season) {
  const [crops, setCrops] = useState<Crop[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let cancelled = false;
    cropService
      .catalog(season)
      .then((result) => {
        if (!cancelled) setCrops(result.data);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [season]);
  return { crops, loading };
}
