import { Link } from "@tanstack/react-router";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Accommodation } from "@/types/accommodation";
import { MapPin, Wifi, Wind, Droplets, Zap, Building2, Home, Hotel } from "lucide-react";

interface AccommodationCardProps {
  accommodation: Accommodation;
  itineraryId?: string;
}

function getPriceLabel(priceRange: string) {
  switch (priceRange) {
    case "budget":
      return "$ Budget";
    case "mid_range":
      return "$$ Mid-range";
    case "premium":
      return "$$$ Premium";
    case "luxury":
      return "$$$$ Luxury";
    default:
      return priceRange;
  }
}

function getCategoryIcon(category: string) {
  switch (category) {
    case "hotel":
      return <Hotel size={14} />;
    case "guesthouse":
      return <Building2 size={14} />;
    case "homestay":
      return <Home size={14} />;
    default:
      return <Building2 size={14} />;
  }
}

function getCategoryLabel(category: string) {
  switch (category) {
    case "hotel":
      return "Hotel";
    case "guesthouse":
      return "Guesthouse";
    case "homestay":
      return "Homestay";
    default:
      return category;
  }
}

const AMENITY_ICONS: Record<string, React.ReactNode> = {
  wifi: <Wifi size={12} />,
  ac: <Wind size={12} />,
  "hot water": <Droplets size={12} />,
  generator: <Zap size={12} />,
};

export function AccommodationCard({ accommodation, itineraryId }: AccommodationCardProps) {
  const firstPhoto = accommodation.photos.length > 0 ? accommodation.photos[0].url : null;

  const linkTo = itineraryId
    ? `/planner/${itineraryId}/accommodations/${accommodation.id}`
    : `/community/${accommodation.id}`;

  return (
    <Link to={linkTo} className="block group">
      <Card className="overflow-hidden h-full transition-all hover:shadow-lg border-border/50 group-hover:border-primary/20">
        {/* Image */}
        <div className="aspect-[4/3] w-full overflow-hidden bg-muted relative">
          {firstPhoto ? (
            <img
              src={firstPhoto}
              alt={accommodation.name}
              className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center text-muted-foreground/30">
              {getCategoryIcon(accommodation.category)}
              <span className="ml-2 text-lg">{getCategoryLabel(accommodation.category)}</span>
            </div>
          )}
          {/* Price badge overlay */}
          <div className="absolute top-3 right-3">
            <Badge className="bg-background/90 text-foreground backdrop-blur-sm shadow-sm">
              {getPriceLabel(accommodation.price_range)}
            </Badge>
          </div>
          {/* Category badge overlay */}
          <div className="absolute top-3 left-3">
            <Badge variant="secondary" className="backdrop-blur-sm shadow-sm flex items-center gap-1">
              {getCategoryIcon(accommodation.category)}
              {getCategoryLabel(accommodation.category)}
            </Badge>
          </div>
        </div>

        <CardHeader className="p-4 pb-2">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-lg leading-tight group-hover:text-primary transition-colors line-clamp-1">
              {accommodation.name}
            </h3>
            {accommodation.tags.map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs shrink-0">
                {tag === "hidden_gem" ? "💎 Hidden Gem" : tag === "trending" ? "🔥 Trending" : tag}
              </Badge>
            ))}
          </div>
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <MapPin size={14} className="shrink-0" />
            <span className="line-clamp-1">{accommodation.location}</span>
          </div>
        </CardHeader>

        <CardContent className="p-4 pt-0 pb-2">
          {/* Amenities preview */}
          {accommodation.amenities.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {accommodation.amenities.slice(0, 4).map((amenity) => (
                <span
                  key={amenity}
                  className="inline-flex items-center gap-1 bg-secondary/50 px-2 py-0.5 rounded-full text-xs"
                >
                  {AMENITY_ICONS[amenity.toLowerCase()] || null}
                  {amenity}
                </span>
              ))}
              {accommodation.amenities.length > 4 && (
                <span className="text-xs text-muted-foreground px-1 py-0.5">
                  +{accommodation.amenities.length - 4} more
                </span>
              )}
            </div>
          )}
        </CardContent>

        <CardFooter className="p-4 pt-0 text-xs text-muted-foreground flex justify-between items-center">
          <span className="line-clamp-1">by {accommodation.author_name}</span>
          {accommodation.distance_km != null && (
            <Badge variant="outline" className="text-xs">
              📍 {accommodation.distance_km} km away
            </Badge>
          )}
        </CardFooter>
      </Card>
    </Link>
  );
}
