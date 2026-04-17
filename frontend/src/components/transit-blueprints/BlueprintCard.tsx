import { Link } from "@tanstack/react-router";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import type { TransitBlueprintListItem } from "@/types/transit-blueprint";
import {
  ArrowRight,
  Clock,
  Banknote,
  Footprints,
  User,
} from "lucide-react";

interface BlueprintCardProps {
  blueprint: TransitBlueprintListItem;
}

export function BlueprintCard({ blueprint }: BlueprintCardProps) {
  const durationText = blueprint.estimated_duration_mins
    ? blueprint.estimated_duration_mins >= 60
      ? `${Math.floor(blueprint.estimated_duration_mins / 60)}h ${blueprint.estimated_duration_mins % 60}m`
      : `${blueprint.estimated_duration_mins}m`
    : null;

  return (
    <Link
      to="/transit-blueprints/$blueprintId"
      params={{ blueprintId: blueprint.id }}
      className="block group"
    >
      <Card className="overflow-hidden h-full transition-all hover:shadow-md border-border/50 group-hover:border-primary/20">
        <CardHeader className="p-4 pb-3">
          <div className="flex items-center gap-2 text-sm font-medium">
            <span className="truncate text-foreground">{blueprint.origin}</span>
            <ArrowRight size={14} className="shrink-0 text-primary" />
            <span className="truncate text-foreground">
              {blueprint.destination}
            </span>
          </div>
        </CardHeader>

        <CardContent className="p-4 pt-0 pb-3 space-y-3">
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            {durationText && (
              <div className="flex items-center gap-1">
                <Clock size={12} />
                <span>{durationText}</span>
              </div>
            )}
            {blueprint.estimated_cost_bdt != null && (
              <div className="flex items-center gap-1">
                <Banknote size={12} />
                <span>৳{blueprint.estimated_cost_bdt.toLocaleString()}</span>
              </div>
            )}
            <div className="flex items-center gap-1">
              <Footprints size={12} />
              <span>
                {blueprint.step_count} step{blueprint.step_count !== 1 ? "s" : ""}
              </span>
            </div>
          </div>
        </CardContent>

        <CardFooter className="p-4 pt-0 text-xs text-muted-foreground flex justify-between items-center">
          <div className="flex items-center gap-1.5">
            <User size={12} />
            <span className="line-clamp-1">by {blueprint.author_name}</span>
          </div>
          <span>{new Date(blueprint.created_at).toLocaleDateString()}</span>
        </CardFooter>
      </Card>
    </Link>
  );
}
