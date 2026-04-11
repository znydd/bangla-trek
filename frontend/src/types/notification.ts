export interface Notification {
  id: string;
  user_id: string;
  type: string;
  message: string;
  is_read: boolean;
  resource_id?: string;
  resource_type?: string;
  created_at: string;
}

export interface NotificationListResponse {
  items: Notification[];
  total_unread: number;
}
