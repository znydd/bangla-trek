import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { EmergencyFacility, FacilityType } from "@/types/emergency";
import { Hospital, Shield, Phone, MapPin, Navigation } from "lucide-react";

const TYPE_CONFIG: Record<
  FacilityType,
  { icon: React.ElementType; label: string; color: string; bg: string }
> = {
  hospital: {
    icon: Hospital,
    label: "Hospital",
    color: "text-red-600",
    bg: "bg-red-50 border-red-200",
  },
  police_station: {
    icon: Shield,
    label: "Police Station",
    color: "text-blue-600",
    bg: "bg-blue-50 border-blue-200",
  },
  tourist_police: {
    icon: Shield,
    label: "Tourist Police",
    color: "text-emerald-600",
    bg: "bg-emerald-50 border-emerald-200",
  },
};

interface FacilityCardProps {
  facility: EmergencyFacility;
}

export function getFacilityConfig(type: FacilityType) {
  return TYPE_CONFIG[type] || TYPE_CONFIG.hospital;
}

export function FacilityCard({ facility }: FacilityCardProps) {
  const config = getFacilityConfig(facility.facility_type);
  const Icon = config.icon;

  const handleCall = () => {
    if (facility.phone_number) {
      window.open(`tel:${facility.phone_number}`, "_self");
    }
  };

  const handleDirections = () => {
    window.open(
      `https://www.google.com/maps/dir/?api=1&destination=${facility.latitude},${facility.longitude}`,
      "_blank",
    );
  };

  return (
    <Card className={`border ${config.bg} transition-all hover:shadow-md`}>
      <CardContent className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start gap-3">
            <div
              className={`p-2 rounded-lg ${config.color} bg-white/80 border shrink-0`}
            >
              <Icon size={18} />
            </div>
            <div>
              <h3 className="font-semibold text-sm leading-tight">
                {facility.name}
              </h3>
              <Badge variant="outline" className="mt-1 text-xs font-normal">
                {config.label}
              </Badge>
            </div>
          </div>
          {facility.distance_km != null && (
            <span className="text-xs font-medium text-muted-foreground whitespace-nowrap">
              {facility.distance_km < 1
                ? `${Math.round(facility.distance_km * 1000)}m`
                : `${facility.distance_km.toFixed(1)} km`}
            </span>
          )}
        </div>

        <div className="flex items-start gap-1.5 text-xs text-muted-foreground">
          <MapPin size={12} className="shrink-0 mt-0.5" />
          <span>{facility.address}</span>
        </div>

        {facility.notes && (
          <p className="text-xs text-muted-foreground/80 leading-relaxed">
            {facility.notes}
          </p>
        )}

        <div className="flex items-center gap-2 pt-1">
          {facility.phone_number && (
            <Button
              size="sm"
              variant="outline"
              onClick={handleCall}
              className="text-xs gap-1.5 h-8"
            >
              <Phone size={12} />
              {facility.phone_number}
            </Button>
          )}
          <Button
            size="sm"
            variant="outline"
            onClick={handleDirections}
            className="text-xs gap-1.5 h-8"
          >
            <Navigation size={12} />
            Directions
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
