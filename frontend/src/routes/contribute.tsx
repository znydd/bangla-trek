import { useState, type ReactNode, type SubmitEvent } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  BadgeCheck,
  CheckCircle2,
  CircleDollarSign,
  ClipboardCheck,
  Compass,
  MapPin,
  Route as RouteIcon,
  Search,
  Send,
  ShieldCheck,
  Star,
} from "lucide-react";
import { toast } from "sonner";
import { PhotoUploader } from "@/components/place/PhotoUploader";
import { VideoEmbedInput } from "@/components/place/VideoEmbedInput";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { resolvePlaceImage } from "@/data/synthetic-place";
import { checkDuplicatePlace } from "@/services/place.service";
import { useAuth } from "@/hooks/useAuth";
import { LoginModal } from "@/components/ui/login-modal";
import type { VideoEmbed } from "@/types/community";

export const Route = createFileRoute("/contribute")({
  component: ContributePlacePage,
});

type VideoDraft = Omit<VideoEmbed, "id">;

const categoryOptions = [
  "Nature & adventure",
  "Waterfall",
  "Beach & island",
  "Hill & viewpoint",
  "Heritage & culture",
  "Wildlife & forest",
  "Village experience",
];

const divisionOptions = [
  "Barishal",
  "Chattogram",
  "Dhaka",
  "Khulna",
  "Mymensingh",
  "Rajshahi",
  "Rangpur",
  "Sylhet",
];

const idealForOptions = [
  "Adventure",
  "Friends",
  "Family",
  "Couples",
  "Photography",
  "Nature",
  "Solo travel",
];

const crowdOptions = ["Almost empty", "Light crowd", "Busy", "Very crowded"];
const difficultyOptions = ["Easy", "Moderate", "Difficult", "Guide required"];
const roadOptions = ["Paved", "Rough", "Off-road", "Boat and walking"];
const safetyOptions = ["Very safe", "Mostly safe", "Felt uncertain", "Unsafe"];
const cleanlinessOptions = ["Clean", "Okay", "Littered", "Poor"];
const paymentOptions = ["Cash", "bKash", "Nagad", "Card"];
const carrierOptions = ["GP", "Robi", "Banglalink", "Teletalk"];
const networkOptions = ["No signal", "2G", "3G", "4G", "5G"];
const reliabilityOptions = ["Stable", "Intermittent", "Limited areas"];

function ContributePlacePage() {
  const { isAuthenticated } = useAuth();
  const [searchQuery, setSearchQuery] = useState("");
  const [searchComplete, setSearchComplete] = useState(false);
  const [formUnlocked, setFormUnlocked] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);
  const [placePhotos, setPlacePhotos] = useState<File[]>([]);
  const [reviewPhotos, setReviewPhotos] = useState<File[]>([]);
  const [reviewVideos, setReviewVideos] = useState<VideoDraft[]>([]);
  const [idealFor, setIdealFor] = useState<string[]>(["Adventure"]);
  const [paymentMethods, setPaymentMethods] = useState<string[]>(["Cash"]);
  const [rating, setRating] = useState(5);

  const { data: duplicateResult } = useQuery({
    queryKey: ["places", "duplicate-check", searchQuery],
    queryFn: () => checkDuplicatePlace({ name: searchQuery }),
    enabled: searchComplete && searchQuery.trim().length > 0,
  });

  const matches = (duplicateResult?.matches || []).map((p: any) => ({
    id: p.id,
    slug: p.slug,
    name: p.name,
    category: p.category,
    tags: [],
    summary: p.summary,
    rating: 5,
    review_count: 1,
    location: { upazila: p.upazila || "", district: p.district || "" },
    cover_image: null,
    source: { verified: true },
  }));
  const exactDuplicate = duplicateResult?.is_duplicate ?? false;

  const [place, setPlace] = useState({
    name: "",
    category: categoryOptions[0],
    summary: "",
    description: "",
    village: "",
    upazila: "",
    district: "",
    division: "Chattogram",
    nearestHub: "",
    latitude: "",
    longitude: "",
    bestSeason: "",
    duration: "",
    budget: "",
    accessDifficulty: "Moderate",
    guideRequirement: "Local guide recommended",
    highlights: "",
    warnings: "",
  });

  const [review, setReview] = useState({
    visitedAt: "",
    startingLocation: "",
    groupType: "Friends",
    groupSize: "4",
    travelStyle: "adventure",
    actualCost: "",
    crowdLevel: "Light crowd",
    accessDifficulty: "Moderate",
    roadCondition: "Boat and walking",
    safety: "Mostly safe",
    cleanliness: "Clean",
    carrier: "GP",
    network: "4G",
    networkReliability: "Intermittent",
    title: "",
    travelGuide: "",
  });

  const handleDuplicateSearch = (event: SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!searchQuery.trim()) return;
    setSearchComplete(true);
    setFormUnlocked(false);
  };

  const unlockProposal = () => {
    setPlace((current) => ({ ...current, name: searchQuery.trim() }));
    setFormUnlocked(true);
    window.setTimeout(() => {
      document
        .getElementById("place-proposal-form")
        ?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 50);
  };

  const handleProposalSubmit = (event: SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!isAuthenticated) {
      setLoginOpen(true);
      return;
    }
    if (placePhotos.length === 0) {
      toast.error("Add at least one clear place photo before submitting.");
      document
        .getElementById("place-photos")
        ?.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    if (idealFor.length === 0 || paymentMethods.length === 0) {
      toast.error("Select at least one ideal traveler type and payment method.");
      return;
    }
    setSubmitted(true);
    toast.success("Place proposal submitted for admin review.");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  if (submitted) {
    return (
      <div className="min-h-[75vh] bg-[#f7f7f2] px-4 py-16">
        <LoginModal open={loginOpen} onOpenChange={setLoginOpen} action="submit a place proposal" />
        <div className="mx-auto max-w-2xl rounded-3xl border bg-white p-8 text-center shadow-sm sm:p-12">
          <span className="mx-auto flex size-16 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">
            <ClipboardCheck size={30} />
          </span>
          <Badge className="mt-6 bg-amber-100 text-amber-900">
            Pending admin review
          </Badge>
          <h1 className="mt-4 text-3xl font-black tracking-tight sm:text-4xl">
            Your proposal for {place.name} is in review
          </h1>
          <p className="mx-auto mt-4 max-w-xl leading-7 text-muted-foreground">
            It is not part of the public place listing yet. You will be able to
            track it from your contribution history once the backend is connected.
          </p>
          <div className="mt-8 grid gap-3 rounded-2xl bg-zinc-50 p-5 text-left text-sm sm:grid-cols-3">
            <StatusStep label="Submitted" complete />
            <StatusStep label="Admin review" active />
            <StatusStep label="Published" />
          </div>
          <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
            <Button variant="outline" render={<Link to="/" />}>
              Back to Explore
            </Button>
            <Button
              onClick={() => {
                setSubmitted(false);
                setSearchComplete(false);
                setFormUnlocked(false);
                setSearchQuery("");
              }}
            >
              Propose another place
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#f7f7f2] pb-28">
      <LoginModal open={loginOpen} onOpenChange={setLoginOpen} action="submit a place proposal" />
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-sm font-semibold text-zinc-600 hover:text-zinc-950"
        >
          <ArrowLeft size={16} />
          Back to Explore
        </Link>

        <header className="mt-6 overflow-hidden rounded-3xl bg-zinc-950 px-6 py-10 text-white sm:px-10 lg:px-14">
          <div className="max-w-3xl">
            <Badge className="bg-emerald-400 text-zinc-950">
              Community contribution
            </Badge>
            <h1 className="mt-5 text-4xl font-black tracking-[-0.04em] sm:text-5xl">
              Help travelers discover a place worth knowing
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-white/70">
              Search first to prevent duplicates. If the place is new, share the
              location, practical details and one first-hand travel report for the
              Bangla Trek team to review.
            </p>
          </div>
        </header>

        <div className="mt-6 grid gap-2 rounded-2xl border bg-white p-3 sm:grid-cols-4">
          <ProgressStep number="1" label="Search existing places" active />
          <ProgressStep number="2" label="Describe the place" active={formUnlocked} />
          <ProgressStep number="3" label="Add your experience" active={formUnlocked} />
          <ProgressStep number="4" label="Submit for review" active={formUnlocked} />
        </div>

        <section className="mt-8 rounded-3xl border bg-white p-6 shadow-sm sm:p-8">
          <div className="flex items-start gap-4">
            <span className="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-700">
              <Search size={21} />
            </span>
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald-700">
                Required first step
              </p>
              <h2 className="mt-1 text-2xl font-bold">Is the place already listed?</h2>
              <p className="mt-1 text-sm leading-6 text-muted-foreground">
                Search by its local name, nearby village, upazila or district.
              </p>
            </div>
          </div>

          <form
            onSubmit={handleDuplicateSearch}
            className="mt-6 flex flex-col gap-3 sm:flex-row"
          >
            <div className="relative flex-1">
              <MapPin className="absolute left-4 top-1/2 size-5 -translate-y-1/2 text-muted-foreground" />
              <Input
                required
                value={searchQuery}
                onChange={(event) => {
                  setSearchQuery(event.target.value);
                  setSearchComplete(false);
                  setFormUnlocked(false);
                }}
                placeholder="Search a place, village or district…"
                className="h-12 pl-12 text-base"
              />
            </div>
            <Button type="submit" size="lg" className="h-12 px-7">
              Check for duplicates
            </Button>
          </form>

          {searchComplete && matches.length > 0 && (
            <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-5">
              <div className="flex gap-3 text-amber-950">
                <AlertTriangle className="mt-0.5 size-5 shrink-0" />
                <div>
                  <p className="font-semibold">
                    {exactDuplicate
                      ? "This place already exists"
                      : "Check these possible matches first"}
                  </p>
                  <p className="mt-1 text-sm leading-6 text-amber-900/75">
                    {exactDuplicate
                      ? "A duplicate proposal cannot be submitted. Open the existing place to add your observations and travel guide instead."
                      : "These places share a name or location with your search. Open them to confirm whether your place is already listed."}
                  </p>
                </div>
              </div>
              <div className="mt-4 grid gap-3">
                {matches.map((match: any) => (
                  <div
                    key={match.id}
                    className="flex flex-col gap-4 rounded-2xl border bg-white p-3 sm:flex-row sm:items-center"
                  >
                    <img
                      src={resolvePlaceImage(match.cover_image)}
                      alt={match.cover_image.alt}
                      className="h-24 w-full rounded-xl object-cover sm:w-32"
                    />
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="font-bold">{match.name}</h3>
                        {match.source.verified && (
                          <Badge className="bg-emerald-100 text-emerald-800">
                            <BadgeCheck /> Verified
                          </Badge>
                        )}
                      </div>
                      <p className="mt-1 text-sm text-muted-foreground">
                        {match.location.upazila}, {match.location.district}
                      </p>
                    </div>
                    <Button
                      render={
                        <Link
                          to="/places/$placeId"
                          params={{ placeId: match.slug }}
                        />
                      }
                    >
                      Open place and review
                      <ArrowRight />
                    </Button>
                  </div>
                ))}
              </div>
              {!exactDuplicate && (
                <div className="mt-4 flex justify-end border-t border-amber-200 pt-4">
                  <Button variant="outline" onClick={unlockProposal}>
                    None of these is my place
                    <ArrowRight />
                  </Button>
                </div>
              )}
            </div>
          )}

          {searchComplete && matches.length === 0 && (
            <div className="mt-6 flex flex-col gap-4 rounded-2xl border border-emerald-200 bg-emerald-50 p-5 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex gap-3 text-emerald-950">
                <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                <div>
                  <p className="font-semibold">No matching place found</p>
                  <p className="mt-1 text-sm text-emerald-900/70">
                    You can continue and propose “{searchQuery.trim()}” for review.
                  </p>
                </div>
              </div>
              <Button onClick={unlockProposal} className="shrink-0">
                Continue with this place
                <ArrowRight />
              </Button>
            </div>
          )}
        </section>

        {formUnlocked && (
          <form
            id="place-proposal-form"
            onSubmit={handleProposalSubmit}
            className="mt-10 scroll-mt-24 space-y-8"
          >
            <ContributionSection
              number="01"
              icon={<MapPin />}
              title="Place identity and exact location"
              description="Tell us what the place is called and where travelers can find it."
            >
              <div className="grid gap-5 sm:grid-cols-2">
                <Field label="Place name" htmlFor="place-name">
                  <Input
                    id="place-name"
                    required
                    value={place.name}
                    onChange={(event) =>
                      setPlace({ ...place, name: event.target.value })
                    }
                  />
                </Field>
                <Field label="Category" htmlFor="place-category">
                  <select
                    id="place-category"
                    value={place.category}
                    onChange={(event) =>
                      setPlace({ ...place, category: event.target.value })
                    }
                    className="h-9 w-full rounded-lg border border-input bg-background px-3 text-sm"
                  >
                    {categoryOptions.map((category) => (
                      <option key={category}>{category}</option>
                    ))}
                  </select>
                </Field>
              </div>

              <Field label="One-line summary" htmlFor="place-summary">
                <Input
                  id="place-summary"
                  required
                  maxLength={180}
                  value={place.summary}
                  onChange={(event) =>
                    setPlace({ ...place, summary: event.target.value })
                  }
                  placeholder="What makes this place worth discovering?"
                />
              </Field>

              <Field label="About the place" htmlFor="place-description">
                <Textarea
                  id="place-description"
                  required
                  value={place.description}
                  onChange={(event) =>
                    setPlace({ ...place, description: event.target.value })
                  }
                  placeholder="Describe the landscape, atmosphere and what visitors experience there."
                  className="min-h-32 resize-y leading-6"
                />
              </Field>

              <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                <Field label="Village or local area" htmlFor="place-village">
                  <Input
                    id="place-village"
                    value={place.village}
                    onChange={(event) =>
                      setPlace({ ...place, village: event.target.value })
                    }
                  />
                </Field>
                <Field label="Upazila" htmlFor="place-upazila">
                  <Input
                    id="place-upazila"
                    required
                    value={place.upazila}
                    onChange={(event) =>
                      setPlace({ ...place, upazila: event.target.value })
                    }
                  />
                </Field>
                <Field label="District" htmlFor="place-district">
                  <Input
                    id="place-district"
                    required
                    value={place.district}
                    onChange={(event) =>
                      setPlace({ ...place, district: event.target.value })
                    }
                  />
                </Field>
                <Field label="Division" htmlFor="place-division">
                  <select
                    id="place-division"
                    value={place.division}
                    onChange={(event) =>
                      setPlace({ ...place, division: event.target.value })
                    }
                    className="h-9 w-full rounded-lg border border-input bg-background px-3 text-sm"
                  >
                    {divisionOptions.map((division) => (
                      <option key={division}>{division}</option>
                    ))}
                  </select>
                </Field>
                <Field label="Nearest travel hub" htmlFor="place-hub">
                  <Input
                    id="place-hub"
                    required
                    value={place.nearestHub}
                    onChange={(event) =>
                      setPlace({ ...place, nearestHub: event.target.value })
                    }
                    placeholder="Town, bus stand or launch terminal"
                  />
                </Field>
              </div>

              <div className="grid gap-5 sm:grid-cols-2">
                <Field label="Latitude (optional)" htmlFor="place-latitude">
                  <Input
                    id="place-latitude"
                    type="number"
                    step="any"
                    value={place.latitude}
                    onChange={(event) =>
                      setPlace({ ...place, latitude: event.target.value })
                    }
                    placeholder="23.8103"
                  />
                </Field>
                <Field label="Longitude (optional)" htmlFor="place-longitude">
                  <Input
                    id="place-longitude"
                    type="number"
                    step="any"
                    value={place.longitude}
                    onChange={(event) =>
                      setPlace({ ...place, longitude: event.target.value })
                    }
                    placeholder="90.4125"
                  />
                </Field>
              </div>
            </ContributionSection>

            <ContributionSection
              number="02"
              icon={<Compass />}
              title="Practical travel facts"
              description="Give visitors the quick facts they need before opening the full guide."
            >
              <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                <Field label="Best time to travel" htmlFor="place-season">
                  <Input
                    id="place-season"
                    required
                    value={place.bestSeason}
                    onChange={(event) =>
                      setPlace({ ...place, bestSeason: event.target.value })
                    }
                    placeholder="November–January"
                  />
                </Field>
                <Field label="Suggested duration" htmlFor="place-duration">
                  <Input
                    id="place-duration"
                    required
                    value={place.duration}
                    onChange={(event) =>
                      setPlace({ ...place, duration: event.target.value })
                    }
                    placeholder="2 days / 1 night"
                  />
                </Field>
                <Field label="Expected budget per person" htmlFor="place-budget">
                  <Input
                    id="place-budget"
                    required
                    value={place.budget}
                    onChange={(event) =>
                      setPlace({ ...place, budget: event.target.value })
                    }
                    placeholder="৳3,000–5,000"
                  />
                </Field>
                <Field label="Access difficulty" htmlFor="place-access">
                  <select
                    id="place-access"
                    value={place.accessDifficulty}
                    onChange={(event) =>
                      setPlace({ ...place, accessDifficulty: event.target.value })
                    }
                    className="h-9 w-full rounded-lg border border-input bg-background px-3 text-sm"
                  >
                    {difficultyOptions.map((option) => (
                      <option key={option}>{option}</option>
                    ))}
                  </select>
                </Field>
                <Field label="Guide requirement" htmlFor="place-guide">
                  <select
                    id="place-guide"
                    value={place.guideRequirement}
                    onChange={(event) =>
                      setPlace({ ...place, guideRequirement: event.target.value })
                    }
                    className="h-9 w-full rounded-lg border border-input bg-background px-3 text-sm"
                  >
                    <option>Not usually needed</option>
                    <option>Local guide recommended</option>
                    <option>Local guide required</option>
                  </select>
                </Field>
              </div>

              <ChoiceChips
                label="Ideal for"
                options={idealForOptions}
                values={idealFor}
                onToggle={(value) => toggleValue(value, idealFor, setIdealFor)}
              />

              <div className="grid gap-5 lg:grid-cols-2">
                <Field label="Highlights — one per line" htmlFor="place-highlights">
                  <Textarea
                    id="place-highlights"
                    required
                    value={place.highlights}
                    onChange={(event) =>
                      setPlace({ ...place, highlights: event.target.value })
                    }
                    placeholder={"Peaceful boat ride\nSunrise viewpoint\nLocal village trail"}
                    className="min-h-36 resize-y"
                  />
                </Field>
                <Field label="Know before you go — one per line" htmlFor="place-warnings">
                  <Textarea
                    id="place-warnings"
                    required
                    value={place.warnings}
                    onChange={(event) =>
                      setPlace({ ...place, warnings: event.target.value })
                    }
                    placeholder={"Carry cash\nAvoid after heavy rain\nReturn before dark"}
                    className="min-h-36 resize-y"
                  />
                </Field>
              </div>
            </ContributionSection>

            <ContributionSection
              number="03"
              icon={<ShieldCheck />}
              title="Place photos"
              description="Upload clear, recent photos. The first photo becomes the cover image."
            >
              <div id="place-photos" className="scroll-mt-28">
                <PhotoUploader onPhotosChange={setPlacePhotos} />
                <p className="mt-3 text-xs text-muted-foreground">
                  {placePhotos.length} photo{placePhotos.length === 1 ? "" : "s"} selected.
                  At least one is required. Photo uploads remain local in this UI preview.
                </p>
              </div>
            </ContributionSection>

            <ContributionSection
              number="04"
              icon={<RouteIcon />}
              title="Your first-hand travel report"
              description="A new place needs at least one dated experience so the practical information has context."
            >
              <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                <Field label="When did you visit?" htmlFor="review-date">
                  <Input
                    id="review-date"
                    type="date"
                    required
                    value={review.visitedAt}
                    onChange={(event) =>
                      setReview({ ...review, visitedAt: event.target.value })
                    }
                  />
                </Field>
                <Field label="Where did you start from?" htmlFor="review-origin">
                  <Input
                    id="review-origin"
                    required
                    value={review.startingLocation}
                    onChange={(event) =>
                      setReview({ ...review, startingLocation: event.target.value })
                    }
                  />
                </Field>
                <Field label="Cost per person" htmlFor="review-cost">
                  <div className="relative">
                    <CircleDollarSign className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="review-cost"
                      required
                      type="number"
                      min="0"
                      value={review.actualCost}
                      onChange={(event) =>
                        setReview({ ...review, actualCost: event.target.value })
                      }
                      className="pl-9"
                    />
                  </div>
                </Field>
                <Field label="Travel style" htmlFor="review-style">
                  <select
                    id="review-style"
                    value={review.travelStyle}
                    onChange={(event) =>
                      setReview({ ...review, travelStyle: event.target.value })
                    }
                    className="h-9 w-full rounded-lg border border-input bg-background px-3 text-sm"
                  >
                    <option value="budget">Budget</option>
                    <option value="comfort">Comfort</option>
                    <option value="adventure">Adventure</option>
                    <option value="family">Family</option>
                  </select>
                </Field>
                <Field label="Who traveled with you?" htmlFor="review-group-type">
                  <Input
                    id="review-group-type"
                    value={review.groupType}
                    onChange={(event) =>
                      setReview({ ...review, groupType: event.target.value })
                    }
                  />
                </Field>
                <Field label="Group size" htmlFor="review-group-size">
                  <Input
                    id="review-group-size"
                    type="number"
                    min="1"
                    value={review.groupSize}
                    onChange={(event) =>
                      setReview({ ...review, groupSize: event.target.value })
                    }
                  />
                </Field>
              </div>

              <div className="rounded-2xl border bg-zinc-50 p-5">
                <Label>Overall experience</Label>
                <div className="mt-2 flex items-center gap-3">
                  <div className="flex gap-1">
                    {[1, 2, 3, 4, 5].map((value) => (
                      <button
                        key={value}
                        type="button"
                        aria-label={`${value} stars`}
                        onClick={() => setRating(value)}
                        className="rounded-lg p-1 hover:scale-110"
                      >
                        <Star
                          size={27}
                          className={
                            value <= rating
                              ? "fill-amber-400 text-amber-400"
                              : "text-zinc-300"
                          }
                        />
                      </button>
                    ))}
                  </div>
                  <span className="text-sm font-semibold">{rating}/5</span>
                </div>
              </div>

              <div className="grid gap-x-8 gap-y-6 lg:grid-cols-2">
                <SingleChoice label="Crowd level" options={crowdOptions} value={review.crowdLevel} onChange={(value) => setReview({ ...review, crowdLevel: value })} />
                <SingleChoice label="Access difficulty" options={difficultyOptions} value={review.accessDifficulty} onChange={(value) => setReview({ ...review, accessDifficulty: value })} />
                <SingleChoice label="Road and access" options={roadOptions} value={review.roadCondition} onChange={(value) => setReview({ ...review, roadCondition: value })} />
                <SingleChoice label="How safe did it feel?" options={safetyOptions} value={review.safety} onChange={(value) => setReview({ ...review, safety: value })} />
                <SingleChoice label="Cleanliness" options={cleanlinessOptions} value={review.cleanliness} onChange={(value) => setReview({ ...review, cleanliness: value })} />
                <ChoiceChips label="Payment methods that worked" options={paymentOptions} values={paymentMethods} onToggle={(value) => toggleValue(value, paymentMethods, setPaymentMethods)} />
                <SingleChoice label="Mobile carrier" options={carrierOptions} value={review.carrier} onChange={(value) => setReview({ ...review, carrier: value })} />
                <SingleChoice label="Strongest network" options={networkOptions} value={review.network} onChange={(value) => setReview({ ...review, network: value })} />
                <SingleChoice label="Signal reliability" options={reliabilityOptions} value={review.networkReliability} onChange={(value) => setReview({ ...review, networkReliability: value })} />
              </div>

              <Field label="Travel guide title" htmlFor="review-title">
                <Input
                  id="review-title"
                  required
                  value={review.title}
                  onChange={(event) =>
                    setReview({ ...review, title: event.target.value })
                  }
                  placeholder="A useful takeaway for the next traveler"
                />
              </Field>
              <Field label="How did you make the trip?" htmlFor="review-guide">
                <Textarea
                  id="review-guide"
                  required
                  value={review.travelGuide}
                  onChange={(event) =>
                    setReview({ ...review, travelGuide: event.target.value })
                  }
                  placeholder="Explain your transport, fares, travel time, accommodation, food, what to carry and anything you wish you had known."
                  className="min-h-56 resize-y leading-7"
                />
              </Field>

              <div className="grid gap-8 border-t pt-6 lg:grid-cols-2">
                <PhotoUploader onPhotosChange={setReviewPhotos} />
                <VideoEmbedInput videos={reviewVideos} onChange={setReviewVideos} />
              </div>
              <p className="text-xs text-muted-foreground">
                {reviewPhotos.length} review photo{reviewPhotos.length === 1 ? "" : "s"} selected.
              </p>
            </ContributionSection>

            <section className="rounded-3xl border border-amber-200 bg-amber-50 p-6 sm:p-8">
              <div className="flex gap-4">
                <AlertTriangle className="mt-1 size-6 shrink-0 text-amber-700" />
                <div>
                  <h2 className="text-xl font-bold text-amber-950">
                    Your place will not publish immediately
                  </h2>
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-amber-900/75">
                    Bangla Trek will check for duplicates, location accuracy,
                    safety concerns and media quality. If approved, the place will
                    receive a Community Added badge and appear in the main listing.
                  </p>
                </div>
              </div>
              <div className="mt-6 flex flex-col-reverse gap-3 border-t border-amber-200 pt-6 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-xs text-amber-900/70">
                  UI preview only · no information is sent to the backend yet.
                </p>
                <Button type="submit" size="lg" className="min-w-52">
                  <Send />
                  Submit place for review
                </Button>
              </div>
            </section>
          </form>
        )}
      </div>
    </div>
  );
}

function ContributionSection({
  number,
  icon,
  title,
  description,
  children,
}: {
  number: string;
  icon: ReactNode;
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <section className="scroll-mt-24 rounded-3xl border bg-white p-6 shadow-sm sm:p-8">
      <div className="flex gap-4 border-b pb-6">
        <span className="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-zinc-950 text-white [&_svg]:size-5">
          {icon}
        </span>
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald-700">
            Step {number}
          </p>
          <h2 className="mt-1 text-2xl font-bold">{title}</h2>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">
            {description}
          </p>
        </div>
      </div>
      <div className="mt-7 space-y-6">{children}</div>
    </section>
  );
}

function ProgressStep({
  number,
  label,
  active,
}: {
  number: string;
  label: string;
  active: boolean;
}) {
  return (
    <div
      className={`flex items-center gap-3 rounded-xl px-3 py-2 text-sm ${
        active ? "bg-emerald-50 font-semibold text-emerald-900" : "text-zinc-400"
      }`}
    >
      <span
        className={`flex size-7 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
          active ? "bg-emerald-700 text-white" : "bg-zinc-100"
        }`}
      >
        {number}
      </span>
      {label}
    </div>
  );
}

function StatusStep({
  label,
  complete = false,
  active = false,
}: {
  label: string;
  complete?: boolean;
  active?: boolean;
}) {
  return (
    <div className="flex items-center gap-2">
      <span
        className={`flex size-6 items-center justify-center rounded-full ${
          complete
            ? "bg-emerald-600 text-white"
            : active
              ? "bg-amber-400 text-amber-950"
              : "bg-zinc-200 text-zinc-500"
        }`}
      >
        {complete ? <CheckCircle2 size={14} /> : <span className="size-2 rounded-full bg-current" />}
      </span>
      <span className={active ? "font-semibold" : "text-muted-foreground"}>
        {label}
      </span>
    </div>
  );
}

function Field({
  label,
  htmlFor,
  children,
}: {
  label: string;
  htmlFor: string;
  children: ReactNode;
}) {
  return (
    <div className="space-y-2">
      <Label htmlFor={htmlFor}>{label}</Label>
      {children}
    </div>
  );
}

function SingleChoice({
  label,
  options,
  value,
  onChange,
}: {
  label: string;
  options: string[];
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => onChange(option)}
            className={`rounded-full border px-3 py-2 text-sm transition-colors ${
              value === option
                ? "border-emerald-700 bg-emerald-700 text-white"
                : "bg-white text-zinc-700 hover:border-emerald-300 hover:bg-emerald-50"
            }`}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}

function ChoiceChips({
  label,
  options,
  values,
  onToggle,
}: {
  label: string;
  options: string[];
  values: string[];
  onToggle: (value: string) => void;
}) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => onToggle(option)}
            className={`rounded-full border px-3 py-2 text-sm transition-colors ${
              values.includes(option)
                ? "border-emerald-700 bg-emerald-700 text-white"
                : "bg-white text-zinc-700 hover:border-emerald-300 hover:bg-emerald-50"
            }`}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}

function toggleValue(
  value: string,
  values: string[],
  setValues: (values: string[]) => void,
) {
  setValues(
    values.includes(value)
      ? values.filter((candidate) => candidate !== value)
      : [...values, value],
  );
}
