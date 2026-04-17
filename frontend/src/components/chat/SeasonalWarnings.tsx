import { useQuery } from "@tanstack/react-query";
import { seasonalIntelQueryOptions } from "@/services/chat.service";
import { Card } from "@/components/ui/card";
import {
  CloudRain,
  Sun,
  AlertTriangle,
  Info,
  ShieldAlert,
  Calendar,
  Loader2,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";
import type { SeasonalWarning } from "@/types/chat";

interface SeasonalWarningsProps {
  destination: string;
  travelMonth?: number;
}

const SEVERITY_CONFIG: Record<
  string,
  { icon: typeof Info; className: string; badgeClass: string }
> = {
  info: {
    icon: Info,
    className: "border-blue-200 bg-blue-50/50 dark:border-blue-900 dark:bg-blue-950/30",
    badgeClass: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
  },
  warning: {
    icon: AlertTriangle,
    className: "border-amber-200 bg-amber-50/50 dark:border-amber-900 dark:bg-amber-950/30",
    badgeClass: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
  },
  danger: {
    icon: ShieldAlert,
    className: "border-red-200 bg-red-50/50 dark:border-red-900 dark:bg-red-950/30",
    badgeClass: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300",
  },
};

export default function SeasonalWarnings({
  destination,
  travelMonth,
}: SeasonalWarningsProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const { data, isLoading, error } = useQuery(
    seasonalIntelQueryOptions(destination, travelMonth)
  );

  if (isLoading) {
    return (
      <Card className="p-4">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading seasonal intelligence for {destination}...
        </div>
      </Card>
    );
  }

  if (error || !data) return null;

  const hasWarnings = data.warnings.length > 0;
  const dangerCount = data.warnings.filter((w) => w.severity === "danger").length;
  const warningCount = data.warnings.filter((w) => w.severity === "warning").length;

  return (
    <Card className="overflow-hidden">
      {/* Collapsed header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-muted/50 
                   transition-colors cursor-pointer text-left"
      >
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-amber-100 dark:bg-amber-900/30">
            <CloudRain size={16} className="text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <h3 className="font-semibold text-sm">Seasonal Intelligence</h3>
            <p className="text-xs text-muted-foreground">
              {destination} —{" "}
              {dangerCount > 0
                ? `${dangerCount} alert${dangerCount > 1 ? "s" : ""}`
                : warningCount > 0
                  ? `${warningCount} warning${warningCount > 1 ? "s" : ""}`
                  : "All clear"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {dangerCount > 0 && (
            <Badge className="bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300 text-xs">
              {dangerCount} Alert{dangerCount > 1 ? "s" : ""}
            </Badge>
          )}
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </button>

      {/* Expanded content */}
      {isExpanded && (
        <div className="px-4 pb-4 space-y-3 border-t pt-3">
          {/* Season summary */}
          {data.current_season_summary && (
            <p className="text-sm text-muted-foreground leading-relaxed">
              {data.current_season_summary}
            </p>
          )}

          {/* Best months */}
          {data.best_months.length > 0 && (
            <div className="flex items-start gap-2">
              <Calendar size={14} className="text-green-600 mt-0.5 shrink-0" />
              <div>
                <p className="text-xs font-medium text-green-700 dark:text-green-400">
                  Best months to visit
                </p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {data.best_months.map((month) => (
                    <Badge
                      key={month}
                      variant="outline"
                      className="text-xs bg-green-50 dark:bg-green-950/30"
                    >
                      {month}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Warnings */}
          {hasWarnings && (
            <div className="space-y-2">
              {data.warnings.map((warning: SeasonalWarning, idx: number) => {
                const config =
                  SEVERITY_CONFIG[warning.severity] || SEVERITY_CONFIG.info;
                const Icon = config.icon;

                return (
                  <div
                    key={idx}
                    className={`rounded-lg border p-3 ${config.className}`}
                  >
                    <div className="flex items-start gap-2">
                      <Icon size={14} className="mt-0.5 shrink-0" />
                      <div className="space-y-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-medium">
                            {warning.title}
                          </span>
                          <span
                            className={`inline-flex items-center rounded-full px-1.5 py-0.5 text-[10px] font-medium ${config.badgeClass}`}
                          >
                            {warning.severity}
                          </span>
                        </div>
                        <p className="text-xs leading-relaxed opacity-80">
                          {warning.description}
                        </p>
                        {warning.recommended_months &&
                          warning.recommended_months.length > 0 && (
                            <div className="flex items-center gap-1 flex-wrap pt-0.5">
                              <Sun size={10} className="shrink-0" />
                              <span className="text-[10px]">
                                Recommended:{" "}
                                {warning.recommended_months.join(", ")}
                              </span>
                            </div>
                          )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
