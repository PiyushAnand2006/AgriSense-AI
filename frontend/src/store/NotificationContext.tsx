import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { notificationService } from "@/services/notificationService";
import { useAuth } from "@/auth/AuthProvider";
import type { NotificationItem } from "@/types/api";

interface NotificationState {
  items: NotificationItem[];
  unreadCount: number;
  loading: boolean;
  refresh: () => Promise<void>;
  markRead: (id: string) => Promise<void>;
  markAllRead: () => Promise<void>;
}

const POLL_INTERVAL_MS = 60_000;

const NotificationContext = createContext<NotificationState | null>(null);

export function NotificationProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const result = await notificationService.list();
      setItems(result.data.items);
      setUnreadCount(result.data.unreadCount);
    } catch {
      // Notifications are non-critical; keep last state.
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (!user) {
      setItems([]);
      setUnreadCount(0);
      return;
    }
    void refresh();
    const timer = setInterval(() => void refresh(), POLL_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [user, refresh]);

  /** Optimistic mark-read with revert on failure. */
  const markRead = useCallback(async (id: string) => {
    const previousItems = items;
    const previousCount = unreadCount;
    const target = items.find((n) => n.id === id);
    if (!target || target.isRead) return;
    setItems((current) => current.map((n) => (n.id === id ? { ...n, isRead: true } : n)));
    setUnreadCount((count) => Math.max(0, count - 1));
    try {
      await notificationService.markRead(id);
    } catch {
      setItems(previousItems);
      setUnreadCount(previousCount);
    }
  }, [items, unreadCount]);

  const markAllRead = useCallback(async () => {
    const previousItems = items;
    const previousCount = unreadCount;
    setItems((current) => current.map((n) => ({ ...n, isRead: true })));
    setUnreadCount(0);
    try {
      await notificationService.markAllRead();
    } catch {
      setItems(previousItems);
      setUnreadCount(previousCount);
    }
  }, [items, unreadCount]);

  const value = useMemo(
    () => ({ items, unreadCount, loading, refresh, markRead, markAllRead }),
    [items, unreadCount, loading, refresh, markRead, markAllRead],
  );

  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>;
}

export function useNotifications(): NotificationState {
  const context = useContext(NotificationContext);
  if (!context) throw new Error("useNotifications must be used within NotificationProvider");
  return context;
}
