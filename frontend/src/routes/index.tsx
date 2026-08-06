import { useState, type SubmitEvent } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowRight,
  BadgeCheck,
  Compass,
  MapPin,
  Search,
  Users,
} from "lucide-react";

import bannerImage from "../../banner.png";
import { communityEntriesQueryOptions } from "@/services/community.service";
import { getPriceRangeLabel } from "@/components/community/EntryCard";
import type { CommunityEntry } from "@/types/community";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/")({
  component: HomePage,
});

function HomePage() {
  const [searchInput, setSearchInput] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");

  const listingsQuery = useQuery(
    communityEntriesQueryOptions({
      page: 1,
      per_page: 8,
      search: appliedSearch || undefined,
      sort_by: "newest",
    }),
  );

  const places = listingsQuery.data?.items ?? [];

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

        {listingsQuery.isLoading && (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 8 }).map((_, index) => (
              <div
                key={index}
                className="h-85 animate-pulse rounded-3xl bg-zinc-200"
              />
            ))}
          </div>
        )}

        {listingsQuery.isError && (
          <div className="rounded-3xl border border-red-200 bg-red-50 px-6 py-12 text-center text-red-700">
            Places could not be loaded. Make sure the backend is running.
          </div>
        )}

        {!listingsQuery.isLoading &&
          !listingsQuery.isError &&
          places.length === 0 && (
            <div className="rounded-3xl border border-dashed border-zinc-300 bg-white px-6 py-16 text-center">
              <Search className="mx-auto mb-4 text-zinc-400" size={32} />
              <h3 className="text-lg font-semibold text-zinc-950">
                No places found
              </h3>
              <p className="mt-1 text-sm text-zinc-500">
                Try another destination or remove the search.
              </p>

              {appliedSearch && (
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
              )}
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

function LandingPlaceCard({ entry }: { entry: CommunityEntry }) {
  const photo = entry.photos[0]?.url || bannerImage;

  // Temporary UI rule. Replace with a real backend field later.
  const isVerified =
    entry.author_name.trim().toLowerCase() === "bangla trek";

  return (
    <button
      type="button"
      className="group block h-92.5 w-full text-left"
    >
      <article className="relative h-full overflow-hidden rounded-[1.75rem] border border-black/10 bg-zinc-900 shadow-sm transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-2xl group-hover:shadow-black/15">
        <img
          src={photo}
          alt={entry.name}
          className="absolute inset-0 h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
        />

        <div className="absolute inset-0 bg-linear-to-t from-black via-black/25 to-transparent" />

        <div className="absolute left-4 top-4">
          {isVerified ? (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-400 px-3 py-1.5 text-xs font-bold text-zinc-950 shadow-lg">
              <BadgeCheck size={14} />
              Verified
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-white/25 bg-black/30 px-3 py-1.5 text-xs font-semibold text-white backdrop-blur-md">
              <Users size={14} />
              Community
            </span>
          )}
        </div>

        {entry.tags[0] && (
          <span className="absolute right-4 top-4 rounded-full border border-white/25 bg-white/15 px-3 py-1.5 text-xs font-medium capitalize text-white backdrop-blur-md">
            {entry.tags[0].replace("_", " ")}
          </span>
        )}

        <div className="absolute inset-x-0 bottom-0 p-5 text-white">
          <span className="text-xs font-semibold uppercase tracking-[0.16em] text-emerald-300">
            {entry.category}
          </span>

          <h3 className="mt-2 line-clamp-2 text-2xl font-bold leading-tight tracking-tight">
            {entry.name}
          </h3>

          <div className="mt-2 flex items-center gap-1.5 text-sm text-white/75">
            <MapPin size={15} className="shrink-0" />
            <span className="line-clamp-1">{entry.location}</span>
          </div>

          <div className="grid grid-rows-[0fr] opacity-0 transition-all duration-300 group-hover:mt-4 group-hover:grid-rows-[1fr] group-hover:opacity-100">
            <div className="overflow-hidden">
              <p className="line-clamp-2 text-sm leading-relaxed text-white/75">
                {entry.travel_tips ||
                  "Local information, expected costs and practical travel advice."}
              </p>
            </div>
          </div>

          <div className="mt-4 flex items-center justify-between border-t border-white/20 pt-4">
            <span className="text-sm font-semibold">
              {getPriceRangeLabel(entry.price_range)}
            </span>

            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-zinc-950 transition-transform duration-300 group-hover:translate-x-1">
              <ArrowRight size={16} />
            </span>
          </div>
        </div>
      </article>
    </button>
  );
}