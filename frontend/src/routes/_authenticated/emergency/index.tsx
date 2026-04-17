import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  emergencyFacilitiesQueryOptions,
  emergencyPhrasesQueryOptions,
} from "@/services/emergency.service";
import { EmergencyContactsBar } from "@/components/emergency/EmergencyContactsBar";
import { FacilityCard } from "@/components/emergency/FacilityCard";
import { FacilityTypeFilter } from "@/components/emergency/FacilityTypeFilter";
import { PhraseSection } from "@/components/emergency/PhraseSection";
import { CustomTranslator } from "@/components/emergency/CustomTranslator";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import type { FacilityType } from "@/types/emergency";
import { Search, MapPin, Loader2 } from "lucide-react";

export const Route = createFileRoute("/_authenticated/emergency/")({
  component: EmergencyHubPage,
});

function EmergencyHubPage() {
  const [facilityType, setFacilityType] = useState<FacilityType | "all">("all");
  const [search, setSearch] = useState("");
  const [userLocation, setUserLocation] = useState<{
    lat: number;
    lng: number;
  } | null>(null);
  const [locating, setLocating] = useState(false);

  const { data: facilitiesData, isLoading: facilitiesLoading } = useQuery(
    emergencyFacilitiesQueryOptions({
      facility_type: facilityType === "all" ? undefined : facilityType,
      search: search || undefined,
      lat: userLocation?.lat,
      lng: userLocation?.lng,
    }),
  );

  const { data: phrasesData, isLoading: phrasesLoading } = useQuery(
    emergencyPhrasesQueryOptions(),
  );

  const handleLocateMe = () => {
    if (!navigator.geolocation) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
        setLocating(false);
      },
      () => {
        setLocating(false);
      },
    );
  };

  return (
    <div className="container mx-auto py-8 px-4 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Emergency Hub</h1>
        <p className="text-muted-foreground mt-1">
          Quick access to emergency contacts, nearby facilities, and
          translation help.
        </p>
      </div>

      {/* Emergency Numbers */}
      <EmergencyContactsBar />

      {/* Facilities Section */}
      <section className="space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <h2 className="text-xl font-semibold">Emergency Facilities</h2>
          <Button
            variant="outline"
            size="sm"
            onClick={handleLocateMe}
            disabled={locating}
            className="gap-2 w-fit"
          >
            {locating ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <MapPin size={14} />
            )}
            {userLocation ? "Location set ✓" : "Use My Location"}
          </Button>
        </div>

        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
          <FacilityTypeFilter
            selected={facilityType}
            onChange={setFacilityType}
          />
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search facilities..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {facilitiesLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-[160px] rounded-xl" />
            ))}
          </div>
        ) : facilitiesData && facilitiesData.items.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {facilitiesData.items.map((facility) => (
              <FacilityCard key={facility.id} facility={facility} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-muted-foreground">
            No facilities found. Try adjusting your filters.
          </div>
        )}
      </section>

      {/* AI Translator */}
      <section>
        <CustomTranslator />
      </section>

      {/* Phrases Section */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Emergency Phrases</h2>
        <p className="text-sm text-muted-foreground">
          Pre-translated emergency phrases in English, Bengali, and romanized
          form. Tap the copy button to copy the Bengali text.
        </p>
        {phrasesLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-[200px] rounded-xl" />
            ))}
          </div>
        ) : phrasesData ? (
          <PhraseSection categories={phrasesData} />
        ) : null}
      </section>
    </div>
  );
}
