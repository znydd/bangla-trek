import { useState, useMemo, type ReactNode } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { fetchPlaceBySlug } from "@/services/place.service";
import {
  submitPlaceReview,
  placeReviewsQueryOptions,
} from "@/services/review.service";


import {
  ArrowLeft,
  BadgeCheck,
  Banknote,
  CalendarDays,
  CheckCircle2,
  Compass,
  CreditCard,
  Leaf,
  MapPin,
  MessageSquareText,
  Navigation,
  ShieldCheck,
  Signal,
  Sparkles,
  Star,
  ThumbsUp,
  Users,
  Wifi,
} from "lucide-react";
import { toast } from "sonner";
import { ADD_GLOBAL_AI_CONTEXT_EVENT } from "@/components/place/GlobalAiChat";
import { ReviewSubmissionDialog } from "@/components/place/ReviewSubmissionDialog";
import { LocationMap } from "@/components/place/LocationMap";
import { VideoEmbedPlayer } from "@/components/place/VideoEmbedPlayer";
import {
  EChartsPieChart,
  type ChartConfig,
} from "@/components/evilcharts/charts/echarts-pie-chart";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { LoginModal } from "@/components/ui/login-modal";
import { useAuth } from "@/hooks/useAuth";
import { resolvePlaceImage } from "@/data/synthetic-place";
import type {
  PlaceDetail,
  PlaceReview,
  ReviewDraft,
} from "@/types/place";

export const Route = createFileRoute("/places/$placeId")({
  component: PlaceDetailPage,
});

const ratingChartConfig = {
  rating: {
    label: "Overall rating",
    colors: {
      light: ["#fbbf24", "#f97316"],
      dark: ["#fbbf24", "#fb923c"],
    },
  },
  remaining: {
    label: "Remaining",
    colors: {
      light: ["#e4e4e7"],
      dark: ["#3f3f46"],
    },
  },
} satisfies ChartConfig;

const pieColors = [
  { light: "#047857", dark: "#34d399" },
  { light: "#0d9488", dark: "#2dd4bf" },
  { light: "#65a30d", dark: "#a3e635" },
  { light: "#d97706", dark: "#fbbf24" },
] as const;

function mapApiPlaceToDetail(api: any): PlaceDetail | null {
  if (!api) return null;

  if (api.cover_image && api.location && api.quick_facts) {
    return api as PlaceDetail;
  }

  const primaryPhoto = resolvePlaceImage(
    (api.media || []).find((m: any) => m.media_type === "photo")?.url,
    api.slug || api.name,
  );

  const budgetEst =
    api.budget_min_bdt && api.budget_max_bdt
      ? `৳${api.budget_min_bdt.toLocaleString()}–৳${api.budget_max_bdt.toLocaleString()} BDT`
      : "Budget details provided by travelers";

  return {
    id: String(api.id),
    slug: api.slug || "",
    name: api.name || "Destination",
    category: api.category || "Nature & Adventure",
    tags: api.tags || [],
    source: {
      type: api.source_type === "community" ? "community" : "admin",
      label: api.source_type === "community" ? "Community Discovery" : "Verified Guide",
      verified: api.source_type !== "community",
      contributor_name: "Bangla Trek Team",
    },
    summary: api.summary || "",
    description: api.description || api.summary || "",
    rating: api.average_rating || 0,
    review_count: api.review_count || 0,
    location: {
      village: api.village || undefined,
      upazila: api.upazila || "District Hub",
      district: api.district || "Bangladesh",
      division: api.division || "Division",
      nearest_hub: api.nearest_hub || "Town Center",
      latitude: api.latitude || 23.685,
      longitude: api.longitude || 90.3563,
    },
    cover_image: {
      id: "cover",
      url: primaryPhoto,
      alt: api.name || "Cover Image",
      object_position: "center",
    },
    gallery: (api.media || []).map((m: any, i: number) => ({
      id: m.id || `gal-${i}`,
      url: m.url,
      alt: m.caption || api.name,
    })),
    quick_facts: {
      best_season: api.best_season || "October to March",
      suggested_duration: api.suggested_duration || "2 Days / 1 Night",
      guide_requirement: api.guide_requirement || "Local guide optional",
      budget_estimate: budgetEst,
      cost_level: "moderate",
      access_difficulty: "Moderate",
      ideal_for: ["Adventure Travelers", "Group Tours", "Nature Enthusiasts"],
    },
    highlights: api.highlights || [],
    know_before_you_go: api.know_before_you_go || [],
    metrics: {
      report_count: api.review_count || 1,
      last_updated_at: api.updated_at || new Date().toISOString(),
      crowd_level: "Moderate",
      road_condition: "Paved",
      payment_methods: ["Cash", "bKash"],
      electricity: "Available",
      drinking_water: "Boiled / Filtered Water",
      signal_reports: [
        {
          carrier: "GP",
          network: "4G",
          reliability: "Stable",
          report_count: 5,
          last_reported_at: new Date().toISOString(),
        },
      ],
    },
    reviews: [],
    created_at: api.created_at || new Date().toISOString(),
    updated_at: api.updated_at || new Date().toISOString(),
  };
}

function PlaceDetailPage() {
  const { placeId } = Route.useParams();

  const { data: apiPlace, isLoading } = useQuery({
    queryKey: ["places", placeId],
    queryFn: () => fetchPlaceBySlug(placeId),
    retry: false,
  });

  const place = mapApiPlaceToDetail(apiPlace);

  if (isLoading) {
    return (
      <div className="mx-auto flex min-h-[60vh] max-w-xl flex-col items-center justify-center px-4 text-center">
        <Compass className="mb-4 size-10 animate-spin text-emerald-600" />
        <h1 className="text-xl font-semibold">Loading place guide...</h1>
      </div>
    );
  }

  if (!place) {
    return (
      <div className="mx-auto flex min-h-[60vh] max-w-xl flex-col items-center justify-center px-4 text-center">
        <MapPin className="mb-4 size-10 text-muted-foreground" />
        <h1 className="text-2xl font-bold">Place not found</h1>
        <p className="mt-2 text-muted-foreground">
          Could not locate place details.
        </p>
        <Button className="mt-6 font-semibold" render={<Link to="/" />}>
          Return to Explore
        </Button>
      </div>
    );
  }

  return <PlaceGuide place={place} />;
}


function PlaceGuide({ place }: { place: PlaceDetail }) {
  const { isAuthenticated } = useAuth();
  const [reviewOpen, setReviewOpen] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);

  const openReviewOrLogin = () => {
    if (!isAuthenticated) { setLoginOpen(true); return; }
    setReviewOpen(true);
  };

  const { data: apiReviews, refetch: refetchReviews } = useQuery(
    placeReviewsQueryOptions(place.id)
  );

  const reviews: PlaceReview[] = useMemo(() => {
    if (Array.isArray(apiReviews) && apiReviews.length > 0) {
      return apiReviews.map((r: any) => ({
        id: r.id,
        author_name: r.user_name || "Community Traveler",
        author_initials: (r.user_name || "CT").slice(0, 2).toUpperCase(),
        rating: r.rating,
        visited_at: r.visited_on,
        submitted_at: r.created_at || r.visited_on,
        travel_style: r.travel_style || "comfort",
        group_type: r.group_type || "Friends",
        group_size: r.group_size || 2,
        starting_location: r.starting_location || "Dhaka",
        actual_cost: r.actual_cost_bdt ? `৳${r.actual_cost_bdt}` : "Not specified",
        title: r.title || `Trip to ${place.name}`,
        observations: {
          crowd_level: r.crowd_level || "Moderate",
          access_difficulty: r.access_difficulty || "Moderate",
          road_condition: r.road_condition || "Paved",
          payment_methods: r.payment_methods || ["Cash"],
          carrier: r.mobile_carrier || "GP",
          network: r.strongest_network || "4G",
          network_reliability: r.network_reliability || "Stable",
          safety: r.safety || "Very safe",
          cleanliness: r.cleanliness || "Clean",
        },
        helpful_count: r.helpful_count || 0,
        travel_guide: r.travel_guide || "",
        photos: (r.media || []).filter((m: any) => m.media_type === "photo").map((m: any) => ({
          id: m.id,
          url: m.url,
          caption: m.caption,
        })),
        video_embeds: (r.media || []).filter((m: any) => m.media_type === "video_embed").map((m: any) => ({
          id: m.id,
          url: m.url,
          platform: m.platform || "youtube",
          caption: m.caption,
        })),
      }));
    }
    return place.reviews || [];
  }, [apiReviews, place]);

  const averageRating =
    reviews.length > 0
      ? reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length
      : place.rating || 0;

  const handleReviewSubmit = async (draft: ReviewDraft) => {
    try {
      if (place.id && !place.id.startsWith("synthetic")) {
        await submitPlaceReview(place.id, {
          visited_on: draft.visited_at,
          rating: draft.rating,
          travel_style: draft.travel_style,
          group_type: draft.group_type,
          group_size: draft.group_size,
          starting_location: draft.starting_location,
          actual_cost_bdt: parseFloat(draft.actual_cost) || null,
          travel_guide: draft.travel_guide,
          crowd_level: draft.crowd_level,
          access_difficulty: draft.access_difficulty,
          road_condition: draft.road_condition,
          payment_methods: draft.payment_methods,
          carrier: draft.carrier,
          network_type: draft.network,
          network_reliability: draft.network_reliability,
          safety_feeling: draft.safety,
          cleanliness: draft.cleanliness,
        });
        await refetchReviews();
        toast.success("Review submitted successfully!");
      }
    } catch {
      toast.info("Saved review preview locally.");
    }

    toast.success("Review submitted.");
    window.setTimeout(() => {
      document
        .getElementById("travel-guides")
        ?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);
  };

  const coverImage = resolvePlaceImage(place.cover_image);

  return (
    <div className="bg-[#f7f7f2] pb-28">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <Button
          variant="ghost"
          size="lg"
          className="mb-4 -ml-2"
          render={<Link to="/" hash="places" />}
        >
          <ArrowLeft className=" size-6" />
          Back to Explore
        </Button>

        <section className="relative min-h-[420px] overflow-hidden rounded-[2rem] bg-zinc-950 text-white shadow-2xl shadow-black/15">
          <img
            src={coverImage}
            alt={place.cover_image.alt}
            style={{ objectPosition: place.cover_image.object_position }}
            className="absolute inset-0 h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-linear-to-t from-black via-black/20 to-black/10" />

          <div className="relative flex min-h-[420px] flex-col justify-between p-6 sm:p-9 lg:p-12">
            <div className="flex flex-wrap gap-2">
              <Badge className="h-7 bg-emerald-400 px-3 text-zinc-950">
                <BadgeCheck />
                {place.source.label}
              </Badge>
              {place.tags.map((tag) => (
                <Badge
                  key={tag}
                  className="h-7 border-white/20 bg-black/25 px-3 text-white backdrop-blur"
                >
                  {tag}
                </Badge>
              ))}
            </div>

            <div className="grid items-end gap-8 lg:grid-cols-[1fr_auto]">
              <div className="max-w-4xl">
                <p className="mb-3 flex items-center gap-2 text-sm font-medium text-white/70">
                  <MapPin size={16} />
                  {place.location.upazila}, {place.location.district}
                </p>
                <h1 className="text-5xl font-black tracking-[-0.045em] sm:text-6xl lg:text-7xl">
                  {place.name}
                </h1>
                <p className="mt-5 max-w-2xl text-base leading-relaxed text-white/80 sm:text-lg">
                  {place.summary}
                </p>
                <div className="mt-6 flex flex-wrap items-center gap-4 text-sm">
                  <span className="flex items-center gap-1.5 font-semibold">
                    <Star className="size-4 fill-amber-400 text-amber-400" />
                    {averageRating.toFixed(1)}
                  </span>
                  <span className="text-white/60">
                    {reviews.length} community reviews
                  </span>
                  <span className="text-white/30">•</span>
                  <span className="text-white/70">
                    Updated {formatDate(place.updated_at)}
                  </span>
                </div>
              </div>

              <div className="flex flex-col gap-2 sm:flex-row lg:flex-col">
                <Button
                  size="lg"
                  className="h-12 bg-white px-6 text-zinc-950 hover:bg-white/90"
                  onClick={() => openReviewOrLogin()}
                >
                  <MessageSquareText />
                  Leave a review
                </Button>
                <Button
                  size="lg"
                  className="h-12 border border-white/30 bg-black/25 px-6 text-white backdrop-blur hover:bg-black/40"
                  onClick={() =>
                    window.dispatchEvent(
                      new CustomEvent(ADD_GLOBAL_AI_CONTEXT_EVENT, {
                        detail: { placeName: place.name },
                      }),
                    )
                  }
                >
                  <Sparkles />
                  Use in AI chat
                </Button>
              </div>
            </div>
          </div>
        </section>

        <section id="community-snapshot" className="mt-10 scroll-mt-24">
          <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
            <SectionHeading
              eyebrow="Community snapshot"
              title="What travelers reported"
            />
          </div>

          <div className="mt-7 grid items-start gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
            <div className="grid overflow-hidden rounded-3xl border bg-white lg:grid-cols-[220px_1fr]">
              <RatingChart
                rating={averageRating}
                responseCount={reviews.length}
              />

              <div className="grid content-center gap-x-8 gap-y-5 border-t p-5 sm:grid-cols-2 lg:border-l lg:border-t-0">
                <SnapshotFact
                  icon={<Banknote />}
                  label="Reported cost range"
                  value={reportedCostRange(reviews)}
                />
                <SnapshotFact
                  icon={<Compass />}
                  label="Common travel style"
                  value={titleCase(mostCommon(reviews.map((review) => review.travel_style)))}
                />
                <SnapshotFact
                  icon={<Users />}
                  label="Average group size"
                  value={`${Math.round(
                    reviews.reduce((sum, review) => sum + review.group_size, 0) /
                    Math.max(reviews.length, 1),
                  )} travelers`}
                />
                <SnapshotFact
                  icon={<Compass />}
                  label="Typical access"
                  value={mostCommon(
                    reviews.map((review) => review.observations.access_difficulty),
                  )}
                />
                <SnapshotFact
                  icon={<CreditCard />}
                  label="Most reported payment"
                  value={mostCommon(
                    reviews.flatMap((review) => review.observations.payment_methods),
                  )}
                />
                <SnapshotFact
                  icon={<CalendarDays />}
                  label="Best time to travel"
                  value={place.quick_facts.best_season}
                />
              </div>
            </div>

            <div className="rounded-3xl border bg-white p-3">
              <div>
                <LocationMap
                  latitude={place.location.latitude}
                  longitude={place.location.longitude}
                  locationQuery={`${place.name}, ${place.location.district}`}
                  name={place.name}
                  height={220}
                  compact
                />
              </div>
              <div className="mt-2 flex items-end justify-between gap-3 px-1 pb-1">
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold">
                    {place.location.upazila}, {place.location.district}
                  </p>
                  <p className="mt-0.5 truncate text-[11px] text-muted-foreground">
                    Nearest hub: {place.location.nearest_hub}
                  </p>
                </div>
                <p className="shrink-0 text-right text-[10px] leading-4 text-muted-foreground">
                  {place.location.latitude}
                  <br />
                  {place.location.longitude}
                </p>
              </div>
            </div>
          </div>

          <div className="mt-8">
            <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-end">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald-700">
                  Review distributions
                </p>
              </div>
              <p className="max-w-lg text-sm leading-6 text-muted-foreground">
                Select a pie segment or legend item to focus on one answer.
              </p>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <MetricPieBlock
                icon={<Users />}
                label="Crowd level"
                values={reviews.map(
                  (review) => review.observations.crowd_level,
                )}
              />
              <MetricPieBlock
                icon={<Compass />}
                label="Access difficulty"
                values={reviews.map(
                  (review) => review.observations.access_difficulty,
                )}
              />
              <MetricPieBlock
                icon={<Navigation />}
                label="Road and access"
                values={reviews.map(
                  (review) => review.observations.road_condition,
                )}
              />
              <MetricPieBlock
                icon={<ShieldCheck />}
                label="Safety"
                values={reviews.map((review) => review.observations.safety)}
              />
              <MetricPieBlock
                icon={<Leaf />}
                label="Cleanliness"
                values={reviews.map(
                  (review) => review.observations.cleanliness,
                )}
              />
              <MetricPieBlock
                icon={<Signal />}
                label="Strongest signal"
                values={reviews.map((review) => review.observations.network)}
              />
              <MetricPieBlock
                icon={<Wifi />}
                label="Signal reliability"
                values={reviews.map(
                  (review) => review.observations.network_reliability,
                )}
              />
              <MetricPieBlock
                icon={<CreditCard />}
                label="Payments that worked"
                values={reviews.flatMap(
                  (review) => review.observations.payment_methods,
                )}
                responseCount={reviews.length}
              />
            </div>
          </div>
        </section>

        <section id="travel-guides" className="mt-16 scroll-mt-24">
          <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
            <SectionHeading
              eyebrow="Traveler-written guides"
              title="How people actually made the trip"
              description="Complete first-hand accounts of transport, fares, timing, accommodation and practical advice."
            />
            <Button onClick={() => openReviewOrLogin()}>
              <MessageSquareText />
              Leave a review
            </Button>
          </div>

          <div className="mt-7 space-y-5">
            {reviews.map((review) => (
              <TravelGuideCard key={review.id} review={review} />
            ))}
          </div>
        </section>
      </div>

      <LoginModal
        open={loginOpen}
        onOpenChange={setLoginOpen}
        action="write a review"
      />
      <ReviewSubmissionDialog
        place={place}
        open={reviewOpen}
        onOpenChange={setReviewOpen}
        onSubmit={handleReviewSubmit}
      />
    </div>
  );
}

function SectionHeading({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description?: string;
}) {
  return (
    <div>
      <p className="text-xs font-bold uppercase tracking-[0.2em] text-emerald-700">
        {eyebrow}
      </p>
      <h2 className="mt-2 text-3xl font-bold tracking-tight text-zinc-950">
        {title}
      </h2>
      {description && (
        <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
          {description}
        </p>
      )}
    </div>
  );
}

function SnapshotFact({
  icon,
  label,
  value,
}: {
  icon: ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div>
      <div className="flex items-center gap-2 text-emerald-700 [&_svg]:size-4">
        {icon}
        <span className="text-xs font-semibold uppercase tracking-wide">
          {label}
        </span>
      </div>
      <p className="mt-2 font-semibold leading-5">{value}</p>
    </div>
  );
}

function RatingChart({
  rating,
  responseCount,
}: {
  rating: number;
  responseCount: number;
}) {
  const data = [
    { segment: "rating", value: rating },
    { segment: "remaining", value: Math.max(0, 5 - rating) },
  ];

  return (
    <div className="p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-500">
        Overall rating
      </p>
      <div className="relative mx-auto mt-1 max-w-44">
        <EChartsPieChart
          data={data}
          config={ratingChartConfig}
          dataKey="value"
          nameKey="segment"
          className="h-36"
        >
          <EChartsPieChart.Pie
            innerRadius="72%"
            outerRadius="94%"
            paddingAngle={2}
            cornerRadius={12}
            startAngle={90}
            endAngle={-270}
          />
        </EChartsPieChart>
        <div className="pointer-events-none absolute inset-0 z-20 flex flex-col items-center justify-center">
          <div className="flex items-end gap-1">
            <strong className="text-4xl font-black tracking-tight text-zinc-950">
              {rating.toFixed(1)}
            </strong>
            <span className="mb-1.5 text-sm text-muted-foreground">/ 5</span>
          </div>
          <Stars rating={Math.round(rating)} size={13} />
        </div>
      </div>
      <p className="border-t pt-3 text-center text-xs text-muted-foreground">
        Based on {responseCount} visible reviews
      </p>
    </div>
  );
}

function MetricPieBlock({
  icon,
  label,
  values,
  responseCount,
}: {
  icon: ReactNode;
  label: string;
  values: Array<string | null | undefined>;
  responseCount?: number;
}) {
  const [selected, setSelected] = useState<string | null>(null);
  const breakdown = countValues(values);
  const total = responseCount ?? values.filter(Boolean).length;
  const chartData = breakdown.map((item, index) => ({
    sector: `answer-${index}`,
    label: item.value,
    value: item.count,
    share: `${item.percentage}%`,
  }));
  const chartConfig = Object.fromEntries(
    chartData.map((item, index) => {
      const color = pieColors[index % pieColors.length];
      return [
        item.sector,
        {
          label: item.label,
          colors: { light: [color.light], dark: [color.dark] },
        },
      ];
    }),
  ) satisfies ChartConfig;

  return (
    <article className="min-w-0 overflow-hidden rounded-2xl border bg-white p-4 shadow-sm shadow-zinc-950/[0.02]">
      <div className="flex items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2 text-sm font-semibold [&_svg]:size-4">
          <span className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-emerald-100 text-emerald-700">
            {icon}
          </span>
          <span className="truncate">{label}</span>
        </div>
        <Badge variant="outline" className="shrink-0 text-[10px]">
          {total}
        </Badge>
      </div>
      {chartData.length > 0 ? (
        <>
          <div className="relative mt-1 h-44 w-full">
            <EChartsPieChart
              data={chartData}
              config={chartConfig}
              dataKey="value"
              nameKey="sector"
              className="h-full w-full"
              selectedSector={selected}
              onSelectionChange={(selection) =>
                setSelected(selection?.dataKey ?? null)
              }
            >
              <EChartsPieChart.Tooltip roundness="md" />
              <EChartsPieChart.Pie
                isClickable
                innerRadius="52%"
                outerRadius="94%"
                paddingAngle={3}
                startAngle={90}
                endAngle={-270}
              >
                <EChartsPieChart.Label dataKey="share" />
              </EChartsPieChart.Pie>
            </EChartsPieChart>
            <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
              <strong className="text-xl tracking-tight">{total}</strong>
              <span className="text-[10px] text-muted-foreground">reports</span>
            </div>
          </div>
          <div className="space-y-1 border-t pt-2">
            {chartData.map((item, index) => (
              <button
                key={item.sector}
                type="button"
                aria-pressed={selected === item.sector}
                onClick={() =>
                  setSelected((current) =>
                    current === item.sector ? null : item.sector,
                  )
                }
                className={`flex w-full items-center gap-2 text-left text-[11px] transition-opacity ${selected !== null && selected !== item.sector
                  ? "opacity-35"
                  : ""
                  }`}
              >
                <span
                  className="size-2.5 shrink-0 rounded-[3px]"
                  style={{
                    backgroundColor:
                      pieColors[index % pieColors.length].light,
                  }}
                />
                <span className="min-w-0 flex-1 truncate text-zinc-700">
                  {item.label}
                </span>
                <strong className="shrink-0">{item.share}</strong>
              </button>
            ))}
          </div>
        </>
      ) : (
        <p className="mt-5 text-sm text-muted-foreground">No reports yet.</p>
      )}
    </article>
  );
}

function TravelGuideCard({ review }: { review: PlaceReview }) {
  const [showAllMedia, setShowAllMedia] = useState(false);
  const photos = review.photos ?? [];
  const videos = review.video_embeds ?? [];
  const mediaItems: Array<
    | { type: "photo"; item: (typeof photos)[number] }
    | { type: "video"; item: (typeof videos)[number] }
  > = [];

  for (let index = 0; index < Math.max(photos.length, videos.length); index += 1) {
    if (photos[index]) mediaItems.push({ type: "photo", item: photos[index] });
    if (videos[index]) mediaItems.push({ type: "video", item: videos[index] });
  }

  const visibleMedia = showAllMedia ? mediaItems : mediaItems.slice(0, 2);
  const hiddenMediaCount = Math.max(0, mediaItems.length - 2);
  const observations: Array<{
    label: string;
    value: string | null | undefined;
  }> = [
      { label: "Crowd", value: review.observations.crowd_level },
      { label: "Access", value: review.observations.access_difficulty },
      { label: "Road", value: review.observations.road_condition },
      { label: "Safety", value: review.observations.safety },
      { label: "Cleanliness", value: review.observations.cleanliness },
      {
        label: "Signal",
        value:
          review.observations.carrier && review.observations.network
            ? `${review.observations.carrier} · ${review.observations.network}`
            : review.observations.network,
      },
    ];

  return (
    <article className="overflow-hidden rounded-2xl border bg-white">
      <div className="p-5 sm:p-6">
        <div className="flex flex-col justify-between gap-4 sm:flex-row">
          <div className="flex gap-3">
            <span className="flex size-11 shrink-0 items-center justify-center rounded-full bg-zinc-950 text-xs font-bold text-white">
              {review.author_initials}
            </span>
            <div>
              <p className="font-semibold">{review.author_name}</p>
              <p className="mt-1 text-xs text-muted-foreground">
                Visited {formatDate(review.visited_at)} · from{" "}
                {review.starting_location} · {review.group_type} of{" "}
                {review.group_size}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Stars rating={review.rating} size={15} />
            <strong className="text-sm">{review.rating}.0</strong>
          </div>
        </div>

        <div className="mt-5 rounded-2xl bg-zinc-50 p-4">
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-zinc-500">
            Their quick observations
          </p>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {observations
              .filter((item) => item.value)
              .map((item) => (
                <div key={item.label} className="flex items-start gap-2 text-sm">
                  <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-emerald-600" />
                  <span>
                    <span className="text-muted-foreground">{item.label}:</span>{" "}
                    <strong className="font-medium">{item.value}</strong>
                  </span>
                </div>
              ))}
          </div>
          <div className="mt-4 flex flex-wrap gap-2 border-t pt-4">
            <Badge variant="outline">{review.actual_cost}</Badge>
            <Badge variant="outline">{review.travel_style} trip</Badge>
            {review.observations.payment_methods.map((method) => (
              <Badge key={method} variant="outline">
                {method}
              </Badge>
            ))}
          </div>
        </div>
      </div>

      <div className="border-t px-5 py-6 sm:px-6">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-emerald-700">
          Their travel guide
        </p>
        <h3 className="mt-2 text-xl font-bold">{review.title}</h3>
        <p className="mt-3 whitespace-pre-line leading-7 text-zinc-700">
          {review.travel_guide}
        </p>

        {mediaItems.length > 0 && (
          <div className="mt-6 border-t pt-6">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-emerald-700">
              Photos and social videos
            </p>
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              {visibleMedia.map((media) => {
                if (media.type === "photo") {
                  const photo = media.item;
                  return (
                    <figure
                      key={photo.id}
                      className="overflow-hidden rounded-xl border bg-zinc-50"
                    >
                      <img
                        src={resolvePlaceImage(photo)}
                        alt={photo.alt}
                        className="aspect-video w-full object-cover"
                        style={{ objectPosition: photo.object_position }}
                      />
                      {(photo.caption || photo.credit) && (
                        <figcaption className="flex flex-wrap items-center justify-between gap-2 px-3 py-2 text-xs text-muted-foreground">
                          <span>{photo.caption}</span>
                          {photo.credit && <span>Photo: {photo.credit}</span>}
                        </figcaption>
                      )}
                    </figure>
                  );
                }

                const video = media.item;
                return (
                  <figure
                    key={video.id}
                    className="overflow-hidden rounded-xl border bg-zinc-50"
                  >
                    <VideoEmbedPlayer embed={video} />
                    {video.caption && (
                      <figcaption className="px-3 py-2 text-xs text-muted-foreground">
                        {video.caption}
                      </figcaption>
                    )}
                  </figure>
                );
              })}
            </div>

            {hiddenMediaCount > 0 && (
              <div className="mt-4 flex justify-center">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowAllMedia((current) => !current)}
                >
                  {showAllMedia
                    ? "Show less"
                    : `View ${hiddenMediaCount} more`}
                </Button>
              </div>
            )}
          </div>
        )}

        <div className="mt-5 flex items-center justify-between border-t pt-4 text-xs text-muted-foreground">
          <span>Submitted {formatDate(review.submitted_at)}</span>
          <span className="flex items-center gap-1.5">
            <ThumbsUp size={13} />
            Helpful to {review.helpful_count} travelers
          </span>
        </div>
      </div>
    </article>
  );
}

function Stars({ rating, size }: { rating: number; size: number }) {
  return (
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map((value) => (
        <Star
          key={value}
          size={size}
          className={
            value <= rating
              ? "fill-amber-400 text-amber-400"
              : "text-zinc-300"
          }
        />
      ))}
    </div>
  );
}

function countValues(values: Array<string | null | undefined>) {
  const cleanValues = values.filter((value): value is string => Boolean(value));
  const counts = new Map<string, number>();

  cleanValues.forEach((value) => {
    counts.set(value, (counts.get(value) ?? 0) + 1);
  });

  return Array.from(counts.entries())
    .map(([value, count]) => ({
      value,
      count,
      percentage:
        cleanValues.length > 0 ? Math.round((count / cleanValues.length) * 100) : 0,
    }))
    .sort((a, b) => b.count - a.count || a.value.localeCompare(b.value));
}

function mostCommon(values: string[]): string {
  return countValues(values)[0]?.value ?? "No reports yet";
}

function reportedCostRange(reviews: PlaceReview[]): string {
  const costs = reviews
    .map((review) => review.actual_cost.match(/[\d,]+/)?.[0])
    .filter((value): value is string => Boolean(value))
    .map((value) => Number(value.replace(/,/g, "")))
    .filter((value) => Number.isFinite(value));

  if (costs.length === 0) return "No cost reports yet";

  const minimum = Math.min(...costs).toLocaleString("en-US");
  const maximum = Math.max(...costs).toLocaleString("en-US");
  return minimum === maximum
    ? `৳${minimum} per person`
    : `৳${minimum}–${maximum} per person`;
}

function titleCase(value: string): string {
  return value.replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  // ISO datetime strings already have time; only append T00:00:00 for bare date strings
  const parsed = value.includes("T") ? new Date(value) : new Date(`${value}T00:00:00`);
  if (isNaN(parsed.getTime())) return "—";
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(parsed);
}
