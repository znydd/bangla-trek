import { Badge } from "@/components/ui/badge";
import type { GroupTripMember } from "@/types/group-trip";
import { User as UserIcon, Crown } from "lucide-react";

interface MemberListProps {
  members: GroupTripMember[];
}

export function MemberList({ members }: MemberListProps) {
  // Sort owner first
  const sorted = [...members].sort((a, b) =>
    a.role === "owner" ? -1 : b.role === "owner" ? 1 : 0
  );

  return (
    <div className="space-y-2">
      {sorted.map((member) => (
        <div
          key={member.user_id}
          className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted/50 transition-colors"
        >
          <div className="h-8 w-8 rounded-full overflow-hidden border bg-muted shrink-0">
            {member.picture_url ? (
              <img
                src={member.picture_url}
                alt={member.name}
                className="h-full w-full object-cover"
              />
            ) : (
              <div className="h-full w-full flex items-center justify-center bg-primary/10 text-primary">
                <UserIcon size={14} />
              </div>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{member.name}</p>
            <p className="text-xs text-muted-foreground">
              Joined {new Date(member.joined_at).toLocaleDateString()}
            </p>
          </div>
          {member.role === "owner" && (
            <Badge variant="secondary" className="shrink-0">
              <Crown size={10} className="mr-1" />
              Owner
            </Badge>
          )}
        </div>
      ))}
    </div>
  );
}
