import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { authService } from "@/services/authService";
import { tokenStore, ApiError } from "@/services/apiClient";
import type { User } from "@/types/api";
import type { AuthState } from "./authTypes";

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [initializing, setInitializing] = useState(true);

  // Session persistence: if a token exists, resolve the user via /auth/me.
  useEffect(() => {
    let cancelled = false;
    const token = tokenStore.get();
    if (!token) {
      setInitializing(false);
      return;
    }
    authService
      .me()
      .then((result) => {
        if (!cancelled) setUser(result.data);
      })
      .catch(() => {
        tokenStore.clear();
      })
      .finally(() => {
        if (!cancelled) setInitializing(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const result = await authService.login(email, password);
    tokenStore.set(result.data.token);
    setUser(result.data.user);
  }, []);

  const register = useCallback(
    async (payload: Parameters<typeof authService.register>[0]) => {
      const result = await authService.register(payload);
      tokenStore.set(result.data.token);
      setUser(result.data.user);
    },
    [],
  );

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch (error) {
      if (!(error instanceof ApiError)) throw error;
    } finally {
      tokenStore.clear();
      setUser(null);
    }
  }, []);

  const updateUser = useCallback((next: User) => setUser(next), []);

  const value = useMemo(
    () => ({ user, initializing, login, register, logout, updateUser }),
    [user, initializing, login, register, logout, updateUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
