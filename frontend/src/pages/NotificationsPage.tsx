import { useI18n } from "@/i18n/I18nProvider";
import { useNotifications } from "@/store/NotificationContext";
import { LoadingState, EmptyState } from "@/components/common/states";
import { timeAgo } from "@/utils/format";

const TYPE_ICONS: Record<string, string> = {
  ANALYSIS: "🌿",
  MARKET: "📈",
  RECOMMENDATION: "⚖️",
  WEATHER: "🌦️",
  SYSTEM: "🔔",
  MARKETPLACE: "🏪",
};

export default function NotificationsPage() {
  const { t } = useI18n();
  const { items, unreadCount, loading, markRead, markAllRead } = useNotifications();

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h1 className="font-display text-2xl font-extrabold">
          {t("notifications.title")}
          {unreadCount > 0 && (
            <span className="ml-2 align-middle text-sm font-semibold text-primary-700 dark:text-primary-300">
              {unreadCount} {t("notifications.unread")}
            </span>
          )}
        </h1>
        {unreadCount > 0 && (
          <button type="button" className="btn-secondary" onClick={() => void markAllRead()}>
            {t("notifications.markAllRead")}
          </button>
        )}
      </div>

      {loading && items.length === 0 ? (
        <LoadingState rows={3} />
      ) : items.length === 0 ? (
        <EmptyState description={t("notifications.empty")} />
      ) : (
        <ul className="space-y-2">
          {items.map((notification) => (
            <li key={notification.id}>
              <button
                type="button"
                onClick={() => void markRead(notification.id)}
                className={`card flex w-full items-start gap-4 p-4 text-left transition-colors hover:bg-soil-50 dark:hover:bg-soil-800/60 ${
                  notification.isRead ? "opacity-60" : ""
                }`}
                aria-label={`${notification.title}${notification.isRead ? "" : ` — ${t("notifications.unread")}`}`}
              >
                <span aria-hidden className="mt-0.5 text-2xl">
                  {TYPE_ICONS[notification.type] ?? "🔔"}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="flex flex-wrap items-center gap-2">
                    <span className="font-semibold">{notification.title}</span>
                    <span className="chip bg-soil-100 text-xs text-soil-600 dark:bg-soil-800 dark:text-soil-300">
                      {t(`notifications.type_${notification.type}`)}
                    </span>
                  </span>
                  <span className="mt-1 block text-sm text-soil-600 dark:text-soil-300">
                    {notification.message}
                  </span>
                  <span className="mt-1 block text-xs text-soil-500 dark:text-soil-400">
                    {timeAgo(notification.createdAt)}
                  </span>
                </span>
                {!notification.isRead && (
                  <span aria-hidden className="mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full bg-primary-500" />
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
