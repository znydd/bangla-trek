import { useState } from "react";
import {
  CalendarDays,
  CircleDollarSign,
  Info,
  MessageSquareText,
  Mic,
  Route,
  Square,
  Star,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { PhotoUploader } from "@/components/place/PhotoUploader";
import { VideoEmbedInput } from "@/components/place/VideoEmbedInput";
import { VideoEmbedPlayer } from "@/components/place/VideoEmbedPlayer";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import type { PlaceDetail, ReviewDraft, TravelStyle } from "@/types/place";

interface ReviewSubmissionDialogProps {
  place: PlaceDetail;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (draft: ReviewDraft) => void;
}

const crowdOptions = ["Almost empty", "Light crowd", "Busy", "Very crowded"];
const difficultyOptions = ["Easy", "Moderate", "Difficult", "Guide required"];
const roadOptions = ["Paved", "Rough", "Off-road", "Boat and walking"];
const paymentOptions = ["Cash", "bKash", "Nagad", "Card"];
const carrierOptions = ["GP", "Robi", "Banglalink", "Teletalk"];
const networkOptions = ["No signal", "2G", "3G", "4G", "5G"];
const reliabilityOptions = ["Stable", "Intermittent", "Limited areas"];
const safetyOptions = ["Very safe", "Mostly safe", "Felt uncertain", "Unsafe"];
const cleanlinessOptions = ["Clean", "Okay", "Littered", "Poor"];

export function ReviewSubmissionDialog({
  place,
  open,
  onOpenChange,
  onSubmit,
}: ReviewSubmissionDialogProps) {
  const [isListening, setIsListening] = useState(false);
  const [draft, setDraft] = useState<ReviewDraft>({
    author_name: "UI Preview User",
    rating: 5,
    visited_at: "2026-01-18",
    travel_style: "adventure",
    group_type: "Friends",
    group_size: 4,
    starting_location: "Dhaka",
    actual_cost: "4500",
    title: "A practical guide for first-time visitors",
    travel_guide:
      "We took an overnight bus from Dhaka to Bandarban, then shared a jeep to Rowangchhari. Four of us split the local boat and guide cost. We stayed in a basic guesthouse in Rowangchhari for about ৳1,200 per room. Start early, carry cash and bring enough drinking water.",
    photo_files: [],
    video_embeds: [],
    crowd_level: "Light crowd",
    access_difficulty: "Moderate",
    road_condition: "Boat and walking",
    payment_methods: ["Cash", "bKash"],
    carrier: "GP",
    network: "4G",
    network_reliability: "Intermittent",
    safety: "Mostly safe",
    cleanliness: "Clean",
  });

  const update = <Key extends keyof ReviewDraft>(
    key: Key,
    value: ReviewDraft[Key],
  ) => setDraft((current) => ({ ...current, [key]: value }));

  const togglePayment = (payment: string) => {
    update(
      "payment_methods",
      draft.payment_methods.includes(payment)
        ? draft.payment_methods.filter((item) => item !== payment)
        : [...draft.payment_methods, payment],
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[94vh] overflow-y-auto p-0 sm:max-w-5xl">
        <div className="border-b bg-zinc-950 px-6 py-7 text-white sm:px-9">
          <DialogHeader>
            <div className="mb-2 flex items-center gap-2 text-emerald-300">
              <MessageSquareText size={16} />
              <span className="text-xs font-semibold uppercase tracking-[0.18em]">
                Community review
              </span>
            </div>
            <DialogTitle className="text-2xl font-bold sm:text-3xl">
              Review {place.name}
            </DialogTitle>
            <DialogDescription className="max-w-2xl text-zinc-400">
              Select the conditions you observed, then leave one useful travel
              guide in your own words. Login will be connected later.
            </DialogDescription>
          </DialogHeader>
        </div>

        <form
          className="space-y-10 p-6 sm:p-9"
          onSubmit={(event) => {
            event.preventDefault();
            setIsListening(false);
            onSubmit(draft);
            onOpenChange(false);
          }}
        >
          <FormSection
            number="01"
            title="About your visit"
            description="This context helps other travelers understand your answers."
          >
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <Field label="Your name" htmlFor="review-name">
                <Input
                  id="review-name"
                  value={draft.author_name}
                  onChange={(event) => update("author_name", event.target.value)}
                />
              </Field>
              <Field label="Visit date" htmlFor="review-date">
                <div className="relative">
                  <CalendarDays className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="review-date"
                    type="date"
                    value={draft.visited_at}
                    onChange={(event) => update("visited_at", event.target.value)}
                    className="pl-9"
                  />
                </div>
              </Field>
              <Field label="Started from" htmlFor="review-origin">
                <Input
                  id="review-origin"
                  value={draft.starting_location}
                  onChange={(event) =>
                    update("starting_location", event.target.value)
                  }
                />
              </Field>
              <Field label="Group size" htmlFor="review-group-size">
                <Input
                  id="review-group-size"
                  type="number"
                  min="1"
                  value={draft.group_size}
                  onChange={(event) =>
                    update("group_size", Number(event.target.value))
                  }
                />
              </Field>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <Field label="Travel style" htmlFor="review-style">
                <select
                  id="review-style"
                  value={draft.travel_style}
                  onChange={(event) =>
                    update("travel_style", event.target.value as TravelStyle)
                  }
                  className="h-9 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus:border-ring focus:ring-3 focus:ring-ring/30"
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
                  value={draft.group_type}
                  onChange={(event) => update("group_type", event.target.value)}
                />
              </Field>
              <Field label="Total cost per person (৳)" htmlFor="review-cost">
                <div className="relative">
                  <CircleDollarSign className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="review-cost"
                    type="number"
                    min="0"
                    value={draft.actual_cost}
                    onChange={(event) => update("actual_cost", event.target.value)}
                    className="pl-9"
                  />
                </div>
              </Field>
            </div>
          </FormSection>

          <FormSection
            number="02"
            title="Quick, structured review"
            description="These answers become the easy-to-scan community metrics shown at the top of the place page."
          >
            <div className="rounded-2xl border bg-zinc-50 p-5">
              <Label>Overall experience</Label>
              <div className="mt-2 flex items-center gap-3">
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      type="button"
                      aria-label={`${rating} stars`}
                      onClick={() => update("rating", rating)}
                      className="rounded-lg p-1 transition-transform hover:scale-110"
                    >
                      <Star
                        size={28}
                        className={
                          rating <= draft.rating
                            ? "fill-amber-400 text-amber-400"
                            : "text-zinc-300"
                        }
                      />
                    </button>
                  ))}
                </div>
                <span className="text-sm font-medium">{draft.rating}/5</span>
              </div>
            </div>

            <div className="grid gap-x-8 gap-y-6 lg:grid-cols-2">
              <ChoiceGroup
                label="Crowd level"
                options={crowdOptions}
                value={draft.crowd_level}
                onChange={(value) => update("crowd_level", value)}
              />
              <ChoiceGroup
                label="Access difficulty"
                options={difficultyOptions}
                value={draft.access_difficulty}
                onChange={(value) => update("access_difficulty", value)}
              />
              <ChoiceGroup
                label="Road and access"
                options={roadOptions}
                value={draft.road_condition}
                onChange={(value) => update("road_condition", value)}
              />
              <ChoiceGroup
                label="How safe did it feel?"
                options={safetyOptions}
                value={draft.safety}
                onChange={(value) => update("safety", value)}
              />
              <ChoiceGroup
                label="Cleanliness"
                options={cleanlinessOptions}
                value={draft.cleanliness}
                onChange={(value) => update("cleanliness", value)}
              />
              <ChoiceGroup
                label="Payment methods that worked"
                options={paymentOptions}
                values={draft.payment_methods}
                onToggle={togglePayment}
              />
              <ChoiceGroup
                label="Mobile carrier used"
                options={carrierOptions}
                value={draft.carrier}
                onChange={(value) => update("carrier", value)}
              />
              <ChoiceGroup
                label="Strongest network"
                options={networkOptions}
                value={draft.network}
                onChange={(value) => update("network", value)}
              />
              <ChoiceGroup
                label="Network reliability"
                options={reliabilityOptions}
                value={draft.network_reliability}
                onChange={(value) => update("network_reliability", value)}
              />
            </div>
          </FormSection>

          <FormSection
            number="03"
            title="Your travel guide"
            description="One complete account is easier to write, read and preserve than separate journey and accommodation boxes."
          >
            <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">
              <div className="flex gap-3">
                <Info className="mt-0.5 size-5 shrink-0 text-emerald-700" />
                <div>
                  <p className="font-semibold text-emerald-950">
                    What makes a useful guide?
                  </p>
                  <p className="mt-1 text-sm leading-6 text-emerald-900/75">
                    Explain how you reached the place, transport and fare, travel
                    time, where you stayed and its cost, food, what to carry, and
                    anything you wish you had known.
                  </p>
                </div>
              </div>
            </div>

            <Field label="Guide title" htmlFor="review-title">
              <Input
                id="review-title"
                value={draft.title}
                onChange={(event) => update("title", event.target.value)}
              />
            </Field>

            <Field label="Tell travelers how to make this trip" htmlFor="review-guide">
              <div className="overflow-hidden rounded-2xl border bg-background focus-within:border-ring focus-within:ring-3 focus-within:ring-ring/20">
                <div className="flex items-center justify-between border-b bg-zinc-50 px-4 py-3">
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <Route size={16} className="text-emerald-700" />
                    Travel guide
                  </div>
                  <Button
                    type="button"
                    size="sm"
                    variant={isListening ? "destructive" : "outline"}
                    aria-pressed={isListening}
                    onClick={() => setIsListening((current) => !current)}
                  >
                    {isListening ? <Square /> : <Mic />}
                    {isListening ? "Stop listening" : "Speak instead"}
                  </Button>
                </div>
                {isListening && (
                  <div className="flex items-center gap-3 border-b bg-red-50 px-4 py-3 text-sm text-red-800">
                    <span className="relative flex size-3">
                      <span className="absolute inline-flex size-full animate-ping rounded-full bg-red-400 opacity-75" />
                      <span className="relative inline-flex size-3 rounded-full bg-red-500" />
                    </span>
                    Listening… Speech-to-text is a UI preview and will be connected later.
                  </div>
                )}
                <Textarea
                  id="review-guide"
                  value={draft.travel_guide}
                  onChange={(event) => update("travel_guide", event.target.value)}
                  placeholder="Example: We left Dhaka at 10 PM by bus… From Bandarban we took… It cost… We stayed at… Bring… Avoid…"
                  className="min-h-64 resize-y rounded-none border-0 px-4 py-4 leading-7 shadow-none focus-visible:ring-0"
                />
                <div className="border-t px-4 py-2 text-right text-xs text-muted-foreground">
                  {draft.travel_guide.length} characters
                </div>
              </div>
            </Field>
          </FormSection>

          <FormSection
            number="04"
            title="Photos and social videos"
            description="Add your own photos or attach public YouTube, Facebook and TikTok videos from the trip."
          >
            <PhotoUploader
              onPhotosChange={(files: File[]) => update("photo_files", files)}
            />

            <VideoEmbedInput
              videos={draft.video_embeds}
              onChange={(videos: any) => update("video_embeds", videos)}
            />

            {draft.video_embeds.some((video) => video.url.trim()) && (
              <div className="space-y-3">
                <Label>Video preview</Label>
                <div className="grid gap-4 md:grid-cols-2">
                  {draft.video_embeds
                    .filter((video) => video.url.trim())
                    .map((video, index) => (
                      <VideoEmbedPlayer
                        key={`${video.url}-${index}`}
                        embed={{
                          id: `review-video-preview-${index}`,
                          url: video.url,
                          platform: video.platform,
                        }}
                      />
                    ))}
                </div>
              </div>
            )}

            <p className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs leading-5 text-amber-950">
              UI preview: selected photos use temporary browser URLs and disappear
              after refresh. Permanent uploads will be connected to media storage
              with the backend.
            </p>
          </FormSection>

          <div className="flex flex-col-reverse gap-3 border-t pt-6 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-xs text-muted-foreground">
              Prototype only · this review is kept in browser memory until refresh.
            </p>
            <div className="flex gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
              >
                Cancel
              </Button>
              <Button type="submit" className="min-w-40">
                Publish review
              </Button>
            </div>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function FormSection({
  number,
  title,
  description,
  children,
}: {
  number: string;
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-5">
      <div className="flex gap-3">
        <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-zinc-950 text-xs font-bold text-white">
          {number}
        </span>
        <div>
          <h3 className="font-semibold">{title}</h3>
          <p className="text-sm leading-6 text-muted-foreground">{description}</p>
        </div>
      </div>
      <div className="space-y-5 sm:pl-11">{children}</div>
    </section>
  );
}

function Field({
  label,
  htmlFor,
  children,
}: {
  label: string;
  htmlFor: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-2">
      <Label htmlFor={htmlFor}>{label}</Label>
      {children}
    </div>
  );
}

function ChoiceGroup({
  label,
  options,
  value,
  values,
  onChange,
  onToggle,
}: {
  label: string;
  options: string[];
  value?: string;
  values?: string[];
  onChange?: (value: string) => void;
  onToggle?: (value: string) => void;
}) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => {
          const selected = value === option || values?.includes(option);
          return (
            <button
              key={option}
              type="button"
              onClick={() =>
                values ? onToggle?.(option) : onChange?.(option)
              }
              className={`rounded-full border px-3 py-2 text-sm transition-colors ${
                selected
                  ? "border-emerald-700 bg-emerald-700 text-white"
                  : "bg-white text-zinc-700 hover:border-emerald-300 hover:bg-emerald-50"
              }`}
            >
              {option}
            </button>
          );
        })}
      </div>
    </div>
  );
}
