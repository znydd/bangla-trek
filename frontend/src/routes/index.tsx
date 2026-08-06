import { useState, type SubmitEvent } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import {
  BadgeCheck,
  Compass,
  MapPin,
  Search,
  Users,
} from "lucide-react";

import bannerImage from "../../banner.png";
import aiMascot from "@/data/ai_mascot.svg";
import { ADD_GLOBAL_AI_CONTEXT_EVENT } from "@/components/place/GlobalAiChat";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  resolvePlaceImage,
  syntheticPlaceCards,
} from "@/data/synthetic-place";
import type { PlaceCardData } from "@/types/place";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/")({
  component: HomePage,
});

function HomePage() {
  const [searchInput, setSearchInput] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");

  const normalizedSearch = appliedSearch.toLowerCase();
  const places = syntheticPlaceCards.filter((place) => {
    if (!normalizedSearch) return true;
    return [
      place.name,
      place.location.upazila,
      place.location.district,
      place.category,
      ...place.tags,
    ].some((value) => value.toLowerCase().includes(normalizedSearch));
  });

  const handleSearch = (event: SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    setAppliedSearch(searchInput.trim());
  };

  return (
    <div className="min-h-screen bg-[#f7f7f2] pb-24">
      <div className="mx-auto max-w-7xl px-4 pb-5 pt-5 sm:px-6 lg:px-8">
        <section
          className="relative flex h-85 overflow-hidden rounded-[2rem] border border-black/10 bg-cover bg-center shadow-xl shadow-black/10 sm:h-95 md:h-105"
          style={{
            backgroundImage: `
              url(${bannerImage})
            `,
          }}
        >
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_20%,rgba(0,0,0,0.18)_100%)]" />

          <div className="relative z-10 flex w-full flex-col items-center px-5 py-6 text-center sm:px-10 md:py-8">
            <div className="flex max-w-4xl flex-col items-center pt-3 md:pt-5">
              <h1 className="max-w-4xl text-4xl font-black leading-[0.95] tracking-[-0.045em] text-white drop-shadow-lg sm:text-5xl md:text-6xl">
                <span className=" bg-orange-500 ">See </span> <span className=" text-neutral-700">Bangladesh</span>
                <br />
                beyond the guidebook
              </h1>
            </div>

            <form
              onSubmit={handleSearch}
              className="mt-auto flex w-full max-w-3xl items-center gap-2 rounded-2xl border border-white/30 bg-white p-1.5 shadow-2xl shadow-black/25"
            >
              <div className="flex flex-1 items-center gap-3 px-3">
                <Search size={18} className="shrink-0 text-muted-foreground" />

                <Input
                  value={searchInput}
                  onChange={(event) => setSearchInput(event.target.value)}
                  placeholder="Search Sajek, Sylhet, hidden waterfalls..."
                  className="h-10 flex-1 border-0 bg-transparent px-0 shadow-none focus-visible:border-transparent focus-visible:ring-0"
                />
              </div>

              <Button
                type="submit"
                size="lg"
                className="h-10 rounded-xl bg-emerald-600 px-6 text-white hover:bg-emerald-700"
              >
                Search
              </Button>
            </form>
          </div>
        </section>
      </div>

      <section
        id="places"
        className="mx-auto max-w-7xl scroll-mt-6 px-4 sm:px-6 lg:px-8"
      >
        <div className="mb-6 flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.18em] text-emerald-700">
          <Compass size={16} />
          Explore Bangladesh
        </div>

        {places.length === 0 && (
          <div className="rounded-3xl border border-dashed border-zinc-300 bg-white px-6 py-16 text-center">
            <Search className="mx-auto mb-4 text-zinc-400" size={32} />
            <h3 className="text-lg font-semibold text-zinc-950">
              No synthetic places match that search
            </h3>
            <p className="mt-1 text-sm text-zinc-500">
              This UI preview currently contains one place. Clear the search to
              see it.
            </p>
            <button
              type="button"
              onClick={() => {
                setSearchInput("");
                setAppliedSearch("");
              }}
              className="mt-5 text-sm font-semibold text-emerald-700"
            >
              Clear search
            </button>
          </div>
        )}

        {places.length > 0 && (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {places.map((entry) => (
              <LandingPlaceCard key={entry.id} entry={entry} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function LandingPlaceCard({ entry }: { entry: PlaceCardData }) {
  const photo = resolvePlaceImage(entry.cover_image);
  const isVerified = entry.source.verified;

  return (
    <article className="group relative h-80 w-full overflow-hidden rounded-[1.75rem] border border-black/10 bg-zinc-900 text-left shadow-sm">
      <img
        src={photo}
        alt={entry.cover_image.alt}
        style={{ objectPosition: entry.cover_image.object_position }}
        className="absolute inset-0 h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
      />

      <div className="absolute inset-0 bg-linear-to-t from-black via-black/45 to-transparent" />

      <Link
        to="/places/$placeId"
        params={{ placeId: entry.slug }}
        aria-label={`View ${entry.name}`}
        className="absolute inset-0 z-10 rounded-[1.75rem] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-500"
      />

      <div className="pointer-events-none absolute left-4 top-4 z-20">
        {isVerified ? (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-400 px-3 py-1.5 text-xs font-bold text-zinc-950 shadow-lg">
            <BadgeCheck size={14} />
            Verified
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-white/25 bg-black/30 px-3 py-1.5 text-xs font-semibold text-white backdrop-blur-md">
            <Users size={14} />
            Community Discovery
          </span>
        )}
      </div>

      {entry.tags[0] && (
        <span className="pointer-events-none absolute right-4 top-4 z-20 rounded-full border border-white/25 bg-white/15 px-3 py-1.5 text-xs font-medium text-white backdrop-blur-md">
          {entry.tags[0]}
        </span>
      )}

      <div className="pointer-events-none absolute inset-x-0 bottom-0 z-20 p-5 pr-20 text-white drop-shadow-[0_1px_2px_rgba(0,0,0,0.9)]">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-emerald-200">
          {entry.category}
        </p>

        <h3 className="mt-2 text-2xl font-bold tracking-tight">{entry.name}</h3>

        <p className="mt-2 flex items-center gap-1.5 text-sm font-medium text-white/90">
          <MapPin size={15} />
          {entry.location.upazila}, {entry.location.district}
        </p>

        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs font-medium text-white/90">
          <span className="font-bold text-amber-300">
            ★ {entry.rating?.toFixed(1) ?? "New"}
          </span>
          <span>·</span>
          <span>{entry.review_count} reviews</span>
        </div>

      </div>

      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger
            render={
              <button
                type="button"
                aria-label={`Add ${entry.name} to AI Chat`}
                onClick={() =>
                  window.dispatchEvent(
                    new CustomEvent(ADD_GLOBAL_AI_CONTEXT_EVENT, {
                      detail: { placeName: entry.name },
                    }),
                  )
                }
                className="absolute bottom-3 right-3 z-30 flex size-16 items-center justify-center bg-transparent transition-transform hover:scale-110 focus-visible:rounded-full focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-400"
              />
            }
          >
            <img src={aiMascot} alt="" className="size-16 drop-shadow-lg" />
          </TooltipTrigger>
          <TooltipContent side="top">Add to AI Chat</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </article>
  );
}
