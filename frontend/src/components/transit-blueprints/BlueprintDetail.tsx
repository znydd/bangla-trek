import type { TransitBlueprint } from "@/types/transit-blueprint";
import { BlueprintStepTimeline } from "./BlueprintStepTimeline";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  ArrowRight,
  Clock,
  Banknote,
  Footprints,
  User,
  CalendarDays,
  FileText,
  StickyNote,
} from "lucide-react";

interface BlueprintDetailProps {
  blueprint: TransitBlueprint;
}

export function BlueprintDetail({ blueprint }: BlueprintDetailProps) {
  const durationText = blueprint.estimated_duration_mins
    ? blueprint.estimated_duration_mins >= 60
      ? `${Math.floor(blueprint.estimated_duration_mins / 60)}h ${blueprint.estimated_duration_mins % 60}m`
      : `${blueprint.estimated_duration_mins}m`
    : null;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 text-2xl font-bold tracking-tight mb-2">
          <span>{blueprint.origin}</span>
          <ArrowRight size={24} className="text-primary shrink-0" />
          <span>{blueprint.destination}</span>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
          {durationText && (
            <div className="flex items-center gap-1.5">
              <Clock size={14} />
              <span>{durationText}</span>
            </div>
          )}
          {blueprint.estimated_cost_bdt != null && (
            <div className="flex items-center gap-1.5">
              <Banknote size={14} />
              <span>৳{blueprint.estimated_cost_bdt.toLocaleString()}</span>
            </div>
          )}
          <div className="flex items-center gap-1.5">
            <Footprints size={14} />
            <span>
              {blueprint.steps.length} step
              {blueprint.steps.length !== 1 ? "s" : ""}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <User size={14} />
            <span>by {blueprint.author_name}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <CalendarDays size={14} />
            <span>{new Date(blueprint.created_at).toLocaleDateString()}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Step timeline (main area) */}
        <div className="lg:col-span-2">
          <Card className="border-border/50">
            <CardHeader className="p-5 pb-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <Footprints size={18} className="text-primary" />
                Step-by-Step Directions
              </h2>
            </CardHeader>
            <CardContent className="p-5 pt-0">
              <BlueprintStepTimeline steps={blueprint.steps} />
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Raw description */}
          <Card className="border-border/50">
            <CardHeader className="p-5 pb-3">
              <h3 className="text-sm font-semibold flex items-center gap-2">
                <FileText size={14} className="text-muted-foreground" />
                Original Description
              </h3>
            </CardHeader>
            <CardContent className="p-5 pt-0">
              <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">
                {blueprint.raw_description}
              </p>
            </CardContent>
          </Card>

          {/* Notes */}
          {blueprint.notes && (
            <Card className="border-border/50">
              <CardHeader className="p-5 pb-3">
                <h3 className="text-sm font-semibold flex items-center gap-2">
                  <StickyNote size={14} className="text-muted-foreground" />
                  Notes & Tips
                </h3>
              </CardHeader>
              <CardContent className="p-5 pt-0">
                <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">
                  {blueprint.notes}
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
