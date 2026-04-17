import { Button } from "@/components/ui/button";
import type { FacilityType } from "@/types/emergency";
import { Hospital, Shield, LayoutGrid } from "lucide-react";

interface FacilityTypeFilterProps {
  selected: FacilityType | "all";
  onChange: (type: FacilityType | "all") => void;
}

const TABS: { value: FacilityType | "all"; label: string; icon: React.ElementType }[] = [
  { value: "all", label: "All", icon: LayoutGrid },
  { value: "hospital", label: "Hospitals", icon: Hospital },
  { value: "police_station", label: "Police", icon: Shield },
  { value: "tourist_police", label: "Tourist Police", icon: Shield },
];

export function FacilityTypeFilter({
  selected,
  onChange,
}: FacilityTypeFilterProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      {TABS.map(({ value, label, icon: Icon }) => (
        <Button
          key={value}
          variant={selected === value ? "secondary" : "outline"}
          size="sm"
          onClick={() => onChange(value)}
          className="rounded-full px-4 h-8 gap-1.5"
        >
          <Icon size={14} />
          {label}
        </Button>
      ))}
    </div>
  );
}
