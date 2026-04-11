import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { unreadNotificationsQueryOptions, markNotificationRead, markAllNotificationsRead } from "@/services/notification.service";
import { Bell, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";

export function NotificationsPopover() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery(unreadNotificationsQueryOptions());
  const notifications = data?.items || [];
  const unreadCount = data?.total_unread || 0;
  
  const [open, setOpen] = useState(false);

  const markReadMutation = useMutation({
    mutationFn: (id: string) => markNotificationRead(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications", "unread"] }),
  });

  const markAllReadMutation = useMutation({
    mutationFn: () => markAllNotificationsRead(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications", "unread"] }),
  });

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative group">
          <Bell className="h-5 w-5 group-hover:text-primary transition-colors" />
          {unreadCount > 0 && (
            <Badge variant="destructive" className="absolute -top-1 -right-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full p-0 text-[10px]">
              {unreadCount}
            </Badge>
          )}
          <span className="sr-only">Toggle notifications</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0 mr-4" align="end">
        <div className="flex items-center justify-between px-4 py-3 border-b">
          <span className="text-sm font-semibold">Notifications</span>
          {unreadCount > 0 && (
            <Button variant="ghost" size="sm" className="h-auto p-0 text-xs text-muted-foreground hover:text-primary" onClick={() => markAllReadMutation.mutate()}>
              <Check className="h-3 w-3 mr-1" /> Mark all read
            </Button>
          )}
        </div>
        <div className="max-h-80 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-center text-xs text-muted-foreground">Loading...</div>
          ) : notifications.length === 0 ? (
            <div className="p-8 text-center text-sm text-muted-foreground">You have no unread notifications.</div>
          ) : (
            <div className="flex flex-col">
              {notifications.map((n) => (
                <div key={n.id} className="p-4 border-b last:border-0 hover:bg-muted/50 transition-colors cursor-pointer group" onClick={() => markReadMutation.mutate(n.id)}>
                  <div className="flex items-start gap-3">
                    <div className="h-2 w-2 mt-1.5 rounded-full bg-blue-500 shrink-0" />
                    <div className="flex-1 space-y-1">
                      <p className="text-sm leading-tight text-foreground/90">{n.message}</p>
                      <p className="text-[10px] text-muted-foreground">{new Date(n.created_at).toLocaleTimeString()}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
