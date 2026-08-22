import { apiClient } from "./apiClient";
import type { NotificationList } from "@/types/api";

export const notificationService = {
  list(unreadOnly = false) {
    return apiClient.get<NotificationList>("/notifications", { unreadOnly });
  },
  markRead(id: string) {
    return apiClient.patch<{ id: string; isRead: boolean }>(`/notifications/${id}/read`);
  },
  markAllRead() {
    return apiClient.patch<{ updated: number }>("/notifications/read-all");
  },
};
