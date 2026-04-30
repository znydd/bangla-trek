import type { TransitBlueprintStep, ParsedStepPreview, TransitMode } from "@/types/transit-blueprint";
import {
  Bus,
  Car,
  Bike,
  Footprints,
  Train,
  Ship,
  Truck,
  CircleDot,
  Clock,
  Banknote,
} from "lucide-react";

const MODE_CONFIG: Record<
  TransitMode,
  { icon: React.ElementType; label: string; color: string }
> = {
  bus: { icon: Bus, label: "Bus", color: "text-blue-500" },
  cng: { icon: Truck, label: "CNG", color: "text-green-500" },
  walking: { icon: Footprints, label: "Walking", color: "text-amber-500" },
  rickshaw: { icon: CircleDot, label: "Rickshaw", color: "text-purple-500" },
  train: { icon: Train, label: "Train", color: "text-red-500" },
  launch: { icon: Ship, label: "Launch", color: "text-cyan-500" },
  boat: { icon: Ship, label: "Boat", color: "text-cyan-600" },
  ferry: { icon: Ship, label: "Ferry", color: "text-teal-500" },
  auto: { icon: Car, label: "Auto", color: "text-orange-500" },
  bike: { icon: Bike, label: "Bike", color: "text-lime-500" },
  car: { icon: Car, label: "Car", color: "text-slate-500" },
  mixed: { icon: CircleDot, label: "Mixed", color: "text-indigo-500" },
  other: { icon: CircleDot, label: "Other", color: "text-gray-500" },
};

export function getModeIcon(mode: TransitMode) {
  return MODE_CONFIG[mode] || MODE_CONFIG.other;
}

interface BlueprintStepTimelineProps {
  steps: (TransitBlueprintStep | ParsedStepPreview)[];
}

export function BlueprintStepTimeline({ steps }: BlueprintStepTimelineProps) {
  if (steps.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No steps parsed yet.
      </div>
    );
  }

  return (
    <div className="relative space-y-0">
      {steps.map((step, index) => {
        const config = getModeIcon(step.mode as TransitMode);
        const Icon = config.icon;
        const isLast = index === steps.length - 1;

        const durationText =
          step.estimated_duration_mins != null
            ? step.estimated_duration_mins >= 60
              ? `${Math.floor(step.estimated_duration_mins / 60)}h ${step.estimated_duration_mins % 60}m`
              : `${step.estimated_duration_mins}m`
            : null;

        return (
          <div key={step.step_number} className="relative flex gap-4">
            {/* Timeline line + icon */}
            <div className="flex flex-col items-center">
              <div
                className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full border-2 bg-background ${config.color} border-current`}
              >
                <Icon size={16} />
              </div>
              {!isLast && (
                <div className="w-0.5 flex-1 bg-border min-h-[24px]" />
              )}
            </div>

            {/* Step content */}
            <div className={`pb-6 flex-1 ${isLast ? "pb-0" : ""}`}>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Step {step.step_number}
                </span>
                <span
                  className={`text-xs font-medium px-2 py-0.5 rounded-full bg-secondary/50 ${config.color}`}
                >
                  {config.label}
                </span>
              </div>

              <p className="text-sm leading-relaxed">{step.instruction}</p>

              {(durationText || step.estimated_cost_bdt != null) && (
                <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                  {durationText && (
                    <div className="flex items-center gap-1">
                      <Clock size={11} />
                      <span>{durationText}</span>
                    </div>
                  )}
                  {step.estimated_cost_bdt != null && (
                    <div className="flex items-center gap-1">
                      <Banknote size={11} />
                      <span>৳{step.estimated_cost_bdt.toLocaleString()}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
