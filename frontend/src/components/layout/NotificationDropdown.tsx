import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { 
  Bell, 
  CheckCheck, 
  Users, 
  Calendar, 
  AlertTriangle, 
  ExternalLink,
  MessageSquare
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { 
  notificationsQueryOptions, 
  markNotificationAsRead, 
  markAllNotificationsAsRead,
  Notification
} from "@/services/notification.service";
import { formatDistanceToNow } from "date-fns";

export default function NotificationDropdown() {
  const queryClient = useQueryClient();
  const { data: notifications = [] } = useQuery(notificationsQueryOptions());

  const unreadCount = notifications.filter((n: Notification) => !n.is_read).length;

  const markReadMutation = useMutation({
    mutationFn: markNotificationAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const markAllReadMutation = useMutation({
    mutationFn: markAllNotificationsAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const getIcon = (type: Notification["type"]) => {
    switch (type) {
      case "group_join":
        return <Users size={16} className="text-blue-500" />;
      case "travel_overlap":
        return <Calendar size={16} className="text-amber-500" />;
      case "reminder":
        return <AlertTriangle size={16} className="text-red-500" />;
      case "poll_result":
        return <MessageSquare size={16} className="text-emerald-500" />;
      default:
        return <Bell size={16} />;
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger render={
        <Button
          variant="ghost"
          size="icon"
          className="relative h-10 w-10 rounded-full hover:bg-muted"
        >
          <Bell size={20} className="text-muted-foreground" />
          {unreadCount > 0 && (
            <span className="absolute top-2 right-2 flex h-4 w-4 items-center justify-center rounded-full bg-red-600 text-[10px] font-bold text-white border-2 border-background">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </Button>
      } />
      <DropdownMenuContent align="end" className="w-80 sm:w-96 p-0 overflow-hidden mt-1 bg-card border shadow-xl">
        <div className="flex items-center justify-between p-4 border-b bg-muted/30">
          <h3 className="font-semibold text-sm">Notifications</h3>
          {unreadCount > 0 && (
            <button
              onClick={() => markAllReadMutation.mutate()}
              className="text-xs text-primary hover:underline flex items-center gap-1 font-medium bg-transparent border-0 cursor-pointer"
            >
              <CheckCheck size={14} />
              Mark all as read
            </button>
          )}
        </div>

        <div className="max-h-[400px] overflow-y-auto">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 px-8 text-center bg-background">
              <div className="p-3 rounded-full bg-muted mb-3">
                <Bell size={24} className="text-muted-foreground/50" />
              </div>
              <p className="text-sm font-medium">No notifications yet</p>
              <p className="text-xs text-muted-foreground mt-1">
                We'll let you know when something important happens!
              </p>
            </div>
          ) : (
            <div className="divide-y divide-border">
              {notifications.map((n: Notification) => (
                <div
                  key={n.id}
                  className={`p-4 transition-colors hover:bg-muted/50 flex gap-3 ${
                    !n.is_read ? "bg-primary/5 border-l-2 border-primary" : ""
                  }`}
                >
                  <div className={`mt-0.5 p-2 rounded-lg bg-background border flex-shrink-0`}>
                    {getIcon(n.type)}
                  </div>
                  <div className="flex-1 min-w-0 space-y-1">
                    <div className="flex items-start justify-between gap-2">
                        <p className={`text-sm leading-tight ${!n.is_read ? "font-semibold" : "font-medium"}`}>
                            {n.title}
                        </p>
                        <span className="text-[10px] text-muted-foreground whitespace-nowrap">
                            {formatDistanceToNow(new Date(n.created_at), { addSuffix: true })}
                        </span>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                      {n.content}
                    </p>
                    {n.link_url && (
                        <div className="pt-1">
                            <Button
                                variant="outline"
                                size="sm"
                                className="h-7 px-3 text-[10px] items-center gap-1 hover:bg-primary hover:text-primary-foreground transition-all"
                                onClick={() => markReadMutation.mutate(n.id)}
                                render={<Link to={n.link_url} />}
                            >
                                View Details
                                <ExternalLink size={10} />
                            </Button>
                        </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {notifications.length > 0 && (
          <div className="p-2 border-t text-center bg-muted/10">
            <p className="text-[10px] text-muted-foreground">Showing latest notifications</p>
          </div>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
