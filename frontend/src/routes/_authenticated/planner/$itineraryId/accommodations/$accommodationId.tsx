import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { accommodationQueryOptions } from "@/services/accommodation.service";
import { itineraryQueryOptions } from "@/services/itinerary.service";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { LocationMap } from "@/components/community/LocationMap";
import {
  ArrowLeft,
  MapPin,
  Wallet,
  Loader2,
  User as UserIcon,
  Calendar,
  Hotel,
  Building2,
  Home,
  Wifi,
  Wind,
  Droplets,
  Zap,
  CheckCircle2,
} from "lucide-react";

export const Route = createFileRoute(
  "/_authenticated/planner/$itineraryId/accommodations/$accommodationId",
)({
  component: AccommodationDetailPage,
});

function getCategoryIcon(category: string) {
  switch (category) {
    case "hotel":
      return <Hotel size={20} className="text-blue-500" />;
    case "guesthouse":
      return <Building2 size={20} className="text-emerald-500" />;
    case "homestay":
      return <Home size={20} className="text-amber-500" />;
    default:
      return <Building2 size={20} />;
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

const AMENITY_ICONS: Record<string, React.ReactNode> = {
  wifi: <Wifi size={16} />,
  ac: <Wind size={16} />,
  "hot water": <Droplets size={16} />,
  generator: <Zap size={16} />,
};

function AccommodationDetailPage() {
  const { itineraryId, accommodationId } = Route.useParams();

  const { data: accommodation, isLoading } = useQuery(
    accommodationQueryOptions(accommodationId),
  );
  const { data: itinerary } = useQuery(itineraryQueryOptions(itineraryId));

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!accommodation) {
    return (
      <div className="container mx-auto py-8 px-4 text-center">
        <p className="text-muted-foreground">Accommodation not found.</p>
        <Button
          variant="outline"
          className="mt-4"
          render={
            <Link
              to="/planner/$itineraryId/accommodations"
              params={{ itineraryId }}
            />
          }
        >
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Accommodations
        </Button>
      </div>
    );
  }

  // Build list of itinerary locations for distance context
  const attractionLocations = itinerary
    ? [...new Set(itinerary.activities.map((a) => a.location))]
    : [];

  return (
    <div className="container mx-auto py-8 px-4 max-w-5xl space-y-8">
      {/* Back button */}
      <Button
        variant="ghost"
        size="sm"
        render={
          <Link
            to="/planner/$itineraryId/accommodations"
            params={{ itineraryId }}
          />
        }
        className="-ml-2 text-muted-foreground"
      >
        <ArrowLeft size={16} className="mr-1" />
        Back to accommodations
      </Button>

      {/* Header */}
      <div className="space-y-3">
        <div className="flex flex-wrap gap-2">
          {accommodation.tags.map((tag) => (
            <Badge key={tag} variant="outline" className="px-3 py-1 text-sm">
              {tag === "hidden_gem"
                ? "💎 Hidden Gem"
                : tag === "trending"
                  ? "🔥 Trending"
                  : tag}
            </Badge>
          ))}
          <Badge
            variant="secondary"
            className="px-3 py-1 text-sm flex items-center gap-1.5"
          >
            {getCategoryIcon(accommodation.category)}
            {getCategoryLabel(accommodation.category)}
          </Badge>
        </div>
        <h1 className="text-4xl font-bold tracking-tight">
          {accommodation.name}
        </h1>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <MapPin size={18} className="text-primary" />
            <span>{accommodation.location}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Wallet size={18} />
            <span>{getPriceLabel(accommodation.price_range)}</span>
          </div>
        </div>
      </div>

      {/* Content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-10">
          {/* Photos */}
          <section>
            <h2 className="text-2xl font-semibold mb-4">Photos</h2>
            {accommodation.photos.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {accommodation.photos.map((photo, idx) => (
                  <div
                    key={photo.id}
                    className={`overflow-hidden rounded-xl ${
                      idx === 0 ? "col-span-2 row-span-2" : ""
                    }`}
                  >
                    <img
                      src={photo.url}
                      alt={photo.caption || accommodation.name}
                      className="h-full w-full object-cover hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                ))}
              </div>
            ) : (
              <div className="aspect-[2/1] flex items-center justify-center bg-muted rounded-xl text-muted-foreground/30">
                {getCategoryIcon(accommodation.category)}
                <span className="ml-2">No photos available</span>
              </div>
            )}
          </section>

          {/* Travel Tips */}
          <section className="bg-muted/30 p-6 rounded-2xl border border-border/50">
            <h2 className="text-2xl font-semibold mb-4">Travel Tips</h2>
            <div className="prose prose-sm dark:prose-invert max-w-none">
              {accommodation.travel_tips ? (
                <p className="whitespace-pre-wrap text-foreground/80 leading-relaxed">
                  {accommodation.travel_tips}
                </p>
              ) : (
                <p className="text-muted-foreground italic">
                  No tips provided for this accommodation yet.
                </p>
              )}
            </div>
          </section>

          {/* Nearby Trip Attractions */}
          {attractionLocations.length > 0 && (
            <section className="bg-primary/5 p-6 rounded-2xl border border-primary/10">
              <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <MapPin size={18} className="text-primary" />
                Your Trip Attractions Nearby
              </h2>
              <p className="text-sm text-muted-foreground mb-3">
                Places from your itinerary to{" "}
                <span className="font-medium text-foreground">
                  {itinerary?.destination}
                </span>
                :
              </p>
              <div className="flex flex-wrap gap-2">
                {attractionLocations.slice(0, 10).map((loc) => (
                  <Badge key={loc} variant="outline" className="text-xs">
                    📍 {loc}
                  </Badge>
                ))}
                {attractionLocations.length > 10 && (
                  <Badge variant="secondary" className="text-xs">
                    +{attractionLocations.length - 10} more
                  </Badge>
                )}
              </div>
            </section>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-8">
          {/* Info card */}
          <section className="bg-card rounded-2xl border p-6 shadow-sm">
            <h3 className="font-semibold text-lg mb-4">Information</h3>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="bg-primary/10 p-2 rounded-lg text-primary">
                  <UserIcon size={20} />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">
                    Contributed by
                  </p>
                  <p className="font-medium">{accommodation.author_name}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="bg-primary/10 p-2 rounded-lg text-primary">
                  <Calendar size={20} />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">
                    Posted on
                  </p>
                  <p className="font-medium">
                    {new Date(accommodation.created_at).toLocaleDateString(
                      undefined,
                      { dateStyle: "long" },
                    )}
                  </p>
                </div>
              </div>
            </div>

            <Separator className="my-6" />

            {/* Amenities */}
            <h3 className="font-semibold text-lg mb-4">Amenities</h3>
            {accommodation.amenities.length > 0 ? (
              <div className="space-y-2">
                {accommodation.amenities.map((amenity) => (
                  <div
                    key={amenity}
                    className="flex items-center gap-2 text-sm"
                  >
                    <CheckCircle2
                      size={16}
                      className="text-green-500 shrink-0"
                    />
                    <span className="flex items-center gap-1.5">
                      {AMENITY_ICONS[amenity.toLowerCase()] || null}
                      {amenity}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground italic">
                No amenities listed.
              </p>
            )}
          </section>

          {/* Map */}
          <section>
            <h3 className="font-semibold text-lg mb-3">Location</h3>
            <LocationMap
              latitude={accommodation.latitude}
              longitude={accommodation.longitude}
              locationQuery={accommodation.location}
              name={accommodation.name}
            />
          </section>
        </div>
      </div>
    </div>
  );
}
