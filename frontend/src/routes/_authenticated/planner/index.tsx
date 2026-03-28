import { useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  userItinerariesQueryOptions,
  generateItinerary,
  deleteItinerary,
} from "@/services/itinerary.service";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import {
  MapPin,
  Calendar,
  Wallet,
  Users,
  Sparkles,
  Loader2,
  Trash2,
  Eye,
  Compass,
} from "lucide-react";
import type { GenerateItineraryPayload, TravelStyle, GroupType } from "@/types/itinerary";
import { Link } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/planner/")({
  component: PlannerPage,
});

const INTEREST_OPTIONS = [
  { value: "nature", label: "🌿 Nature" },
  { value: "food", label: "🍛 Food" },
  { value: "history", label: "🏛️ History" },
  { value: "adventure", label: "🏔️ Adventure" },
  { value: "culture", label: "🎭 Culture" },
  { value: "photography", label: "📸 Photography" },
  { value: "shopping", label: "🛍️ Shopping" },
  { value: "spiritual", label: "🕌 Spiritual" },
];

function PlannerPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Form state
  const [destination, setDestination] = useState("");
  const [durationDays, setDurationDays] = useState(3);
  const [budget, setBudget] = useState(10000);
  const [travelStyle, setTravelStyle] = useState<TravelStyle>("budget");
  const [interests, setInterests] = useState<string[]>([]);
  const [groupType, setGroupType] = useState<GroupType>("solo");

  // Existing itineraries
  const { data: itineraries, isLoading: isLoadingList } = useQuery(
    userItinerariesQueryOptions()
  );

  // Generate mutation
  const generateMutation = useMutation({
    mutationFn: generateItinerary,
    onSuccess: (data) => {
      toast.success("Itinerary generated successfully!");
      queryClient.invalidateQueries({ queryKey: ["itineraries"] });
      navigate({ to: "/planner/$itineraryId", params: { itineraryId: data.id } });
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || "Failed to generate itinerary. Please try again."
      );
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: deleteItinerary,
    onSuccess: () => {
      toast.success("Itinerary deleted");
      queryClient.invalidateQueries({ queryKey: ["itineraries"] });
    },
    onError: () => {
      toast.error("Failed to delete itinerary");
    },
  });

  const toggleInterest = (interest: string) => {
    setInterests((prev) =>
      prev.includes(interest)
        ? prev.filter((i) => i !== interest)
        : [...prev, interest]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!destination.trim()) {
      toast.error("Please enter a destination");
      return;
    }
    const payload: GenerateItineraryPayload = {
      destination: destination.trim(),
      duration_days: durationDays,
      budget,
      travel_style: travelStyle,
      interests,
      group_type: groupType,
    };
    generateMutation.mutate(payload);
  };

  return (
    <div className="container mx-auto py-8 px-4 space-y-10">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center gap-2">
          <Compass className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold tracking-tight">AI Travel Planner</h1>
        </div>
        <p className="text-muted-foreground max-w-xl mx-auto">
          Tell us about your trip and our AI will create a personalized hour-by-hour
          itinerary using community travel data from real travelers.
        </p>
      </div>

      {/* Generator Form */}
      <Card className="max-w-2xl mx-auto p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Destination */}
          <div className="space-y-2">
            <Label htmlFor="destination" className="flex items-center gap-2">
              <MapPin className="h-4 w-4" /> Destination
            </Label>
            <Input
              id="destination"
              placeholder="e.g. Sylhet, Cox's Bazar, Sundarbans..."
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              required
            />
          </div>

          {/* Duration & Budget */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="duration" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" /> Duration (days)
              </Label>
              <Input
                id="duration"
                type="number"
                min={1}
                max={14}
                value={durationDays}
                onChange={(e) => setDurationDays(Number(e.target.value))}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="budget" className="flex items-center gap-2">
                <Wallet className="h-4 w-4" /> Budget (BDT)
              </Label>
              <Input
                id="budget"
                type="number"
                min={500}
                step={500}
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                required
              />
            </div>
          </div>

          {/* Travel Style & Group Type */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Sparkles className="h-4 w-4" /> Travel Style
              </Label>
              <select
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={travelStyle}
                onChange={(e) => setTravelStyle(e.target.value as TravelStyle)}
              >
                <option value="budget">🎒 Budget</option>
                <option value="comfort">🛋️ Comfort</option>
                <option value="luxury">✨ Luxury</option>
              </select>
            </div>
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Users className="h-4 w-4" /> Group Type
              </Label>
              <select
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={groupType}
                onChange={(e) => setGroupType(e.target.value as GroupType)}
              >
                <option value="solo">🧑 Solo</option>
                <option value="couple">💑 Couple</option>
                <option value="family">👨‍👩‍👧‍👦 Family</option>
                <option value="friends">👯 Friends</option>
              </select>
            </div>
          </div>

          {/* Interests */}
          <div className="space-y-2">
            <Label>Interests</Label>
            <div className="flex flex-wrap gap-2">
              {INTEREST_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => toggleInterest(opt.value)}
                  className={`
                    inline-flex items-center rounded-full px-3 py-1.5 text-sm font-medium
                    border transition-colors cursor-pointer
                    ${
                      interests.includes(opt.value)
                        ? "bg-primary text-primary-foreground border-primary"
                        : "bg-background text-foreground border-input hover:bg-accent"
                    }
                  `}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Submit */}
          <Button
            type="submit"
            className="w-full"
            disabled={generateMutation.isPending}
          >
            {generateMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating Itinerary...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Generate AI Itinerary
              </>
            )}
          </Button>
        </form>
      </Card>

      {/* Existing Itineraries */}
      {itineraries && itineraries.length > 0 && (
        <div className="max-w-2xl mx-auto space-y-4">
          <h2 className="text-xl font-semibold tracking-tight">Your Itineraries</h2>
          <div className="space-y-3">
            {itineraries.map((item) => (
              <Card key={item.id} className="p-4">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-semibold truncate">{item.destination}</h3>
                      <Badge variant="secondary">{item.travel_style}</Badge>
                      <Badge variant="outline">{item.group_type}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {item.duration_days} day{item.duration_days > 1 ? "s" : ""} ·{" "}
                      ৳{item.budget.toLocaleString()} · {item.activity_count} activities ·{" "}
                      {new Date(item.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Button
                      variant="outline"
                      size="sm"
                      render={
                        <Link
                          to="/planner/$itineraryId"
                          params={{ itineraryId: item.id }}
                        />
                      }
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteMutation.mutate(item.id)}
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
