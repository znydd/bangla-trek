import { queryOptions } from "@tanstack/react-query";
import api from "@/lib/api";
import type { NotificationListResponse } from "@/types/notification";

const BASE = "/api/v1/notifications";

export const unreadNotificationsQueryOptions = () =>
  queryOptions<NotificationListResponse>({
    queryKey: ["notifications", "unread"],
    queryFn: async () => {
      const res = await api.get<NotificationListResponse>(BASE);
      return res.data;
    },
    refetchInterval: 5000, // Short polling
  });

export const markNotificationRead = async (notificationId: string) => {
  const res = await api.put(`${BASE}/${notificationId}/read`);
  return res.data;
};

export const markAllNotificationsRead = async () => {
  const res = await api.put(`${BASE}/read-all`);
  return res.data;
};
