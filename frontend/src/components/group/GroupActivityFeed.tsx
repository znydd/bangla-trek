import { useQuery } from "@tanstack/react-query";
import { groupActivityQueryOptions } from "@/services/group-collaboration.service";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { 
  UserPlus, 
  MessageSquare, 
  Vote as VoteIcon, 
  Link as LinkIcon, 
  Trophy,
  Loader2,
  CalendarDays
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import type { GroupActivity } from "@/types/group-collaboration";

interface GroupActivityFeedProps {
  tripId: string;
}

const ACTIVITY_ICONS: Record<string, any> = {
  join: { icon: UserPlus, color: "text-blue-500", bg: "bg-blue-100 dark:bg-blue-900/30" },
  trip_created: { icon: Trophy, color: "text-amber-500", bg: "bg-amber-100 dark:bg-amber-900/30" },
  poll_created: { icon: MessageSquare, color: "text-purple-500", bg: "bg-purple-100 dark:bg-purple-900/30" },
  voted: { icon: VoteIcon, color: "text-green-500", bg: "bg-green-100 dark:bg-green-900/30" },
  itinerary_linked: { icon: LinkIcon, color: "text-orange-500", bg: "bg-orange-100 dark:bg-orange-900/30" },
};

export default function GroupActivityFeed({ tripId }: GroupActivityFeedProps) {
  const { data: feed = [], isLoading } = useQuery(groupActivityQueryOptions(tripId));

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (feed.length === 0) {
    return (
      <div className="text-center py-12 space-y-3">
        <div className="mx-auto w-12 h-12 rounded-full bg-muted flex items-center justify-center">
          <CalendarDays className="h-6 w-6 text-muted-foreground" />
        </div>
        <div>
          <h3 className="font-medium">No activity yet</h3>
          <p className="text-sm text-muted-foreground max-w-xs mx-auto">
            Everything important that happens in this trip will appear here.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border before:to-transparent">
      {feed.map((activity) => (
        <ActivityItem key={activity.id} activity={activity} />
      ))}
    </div>
  );
}

function ActivityItem({ activity }: { activity: GroupActivity }) {
  const config = ACTIVITY_ICONS[activity.activity_type] || { icon: MessageSquare, color: "text-muted-foreground", bg: "bg-muted" };
  const Icon = config.icon;

  return (
    <div className="relative flex items-start gap-4">
      {/* Icon node */}
      <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-4 border-background ${config.bg} z-10`}>
        <Icon size={16} className={config.color} />
      </div>

      <Card className="flex-1 p-4 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <Avatar className="h-6 w-6">
              <AvatarImage src={activity.user_picture_url} />
              <AvatarFallback>{activity.user_name?.charAt(0)}</AvatarFallback>
            </Avatar>
            <span className="text-sm font-semibold">{activity.user_name}</span>
          </div>
          <time className="text-[10px] text-muted-foreground whitespace-nowrap">
            {formatDistanceToNow(new Date(activity.created_at), { addSuffix: true })}
          </time>
        </div>
        
        <p className="mt-2 text-sm text-foreground/90 font-medium">
          {activity.description}
        </p>
        
        {activity.metadata_json && (
          <div className="mt-2 text-xs text-muted-foreground italic px-2 py-1 bg-muted/30 rounded border-l-2 border-primary/20">
            {JSON.stringify(activity.metadata_json, null, 2)}
          </div>
        )}
      </Card>
    </div>
  );
}
