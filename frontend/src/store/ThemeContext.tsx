import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type ThemeMode = "light" | "dark" | "system";
export type AccentColor = "green" | "amber";

const STORAGE_KEY = "agrisense.theme";
const ACCENT_KEY = "agrisense.accent";

interface ThemeContextValue {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
  isDark: boolean;
  accent: AccentColor;
  setAccent: (accent: AccentColor) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

function systemPrefersDark(): boolean {
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function applyTheme(mode: ThemeMode, accent: AccentColor) {
  const dark = mode === "dark" || (mode === "system" && systemPrefersDark());
  document.documentElement.classList.toggle("dark", dark);
  // Custom accent property — components read var(--accent) via Tailwind arbitrary values.
  document.documentElement.style.setProperty(
    "--accent",
    accent === "amber" ? "#f5930b" : "#247b4c",
  );
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<ThemeMode>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === "light" || stored === "dark" || stored === "system" ? stored : "system";
  });
  const [accent, setAccentState] = useState<AccentColor>(() => {
    return localStorage.getItem(ACCENT_KEY) === "amber" ? "amber" : "green";
  });
  const [systemDark, setSystemDark] = useState(systemPrefersDark);

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const listener = (event: MediaQueryListEvent) => setSystemDark(event.matches);
    media.addEventListener("change", listener);
    return () => media.removeEventListener("change", listener);
  }, []);

  const isDark = mode === "dark" || (mode === "system" && systemDark);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, mode);
    localStorage.setItem(ACCENT_KEY, accent);
    applyTheme(mode, accent);
  }, [mode, accent]);

  const value = useMemo(
    () => ({
      mode,
      setMode: setModeState,
      isDark,
      accent,
      setAccent: setAccentState,
    }),
    [mode, isDark, accent],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) throw new Error("useTheme must be used within ThemeProvider");
  return context;
}
