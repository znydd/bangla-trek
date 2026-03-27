import { Badge } from "@/components/ui/badge";

interface AmenitiesListProps {
  amenities: string[];
}

export function AmenitiesList({ amenities }: AmenitiesListProps) {
  if (amenities.length === 0) {
    return <p className="text-sm text-muted-foreground italic">No amenities listed.</p>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {amenities.map((amenity, index) => (
        <Badge key={index} variant="outline" className="bg-muted/30">
          {amenity}
        </Badge>
      ))}
    </div>
  );
}
