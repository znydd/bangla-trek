import api from "@/lib/api";
import { queryOptions } from "@tanstack/react-query";

export interface Notification {
  id: string;
  type: "group_join" | "travel_overlap" | "reminder" | "poll_result";
  title: string;
  content: string;
  link_url?: string;
  is_read: boolean;
  created_at: string;
}

export const notificationsQueryOptions = () =>
  queryOptions({
    queryKey: ["notifications"],
    queryFn: async () => {
      const response = await api.get<Notification[]>("/notifications/");
      return response.data;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

export const markNotificationAsRead = async (id: string) => {
  await api.patch(`/notifications/${id}/read`);
};

export const markAllNotificationsAsRead = async () => {
  await api.post("/notifications/mark-all-read");
};
