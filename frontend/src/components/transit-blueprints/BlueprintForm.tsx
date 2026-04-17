import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { BlueprintStepTimeline } from "./BlueprintStepTimeline";
import type {
  CreateTransitBlueprintPayload,
  ParsedStepPreview,
} from "@/types/transit-blueprint";
import { parsePreview } from "@/services/transit-blueprint.service";
import {
  Sparkles,
  Loader2,
  Send,
  Eye,
} from "lucide-react";

interface BlueprintFormProps {
  onSubmit: (data: CreateTransitBlueprintPayload) => Promise<void>;
  isLoading: boolean;
}

export function BlueprintForm({ onSubmit, isLoading }: BlueprintFormProps) {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [rawDescription, setRawDescription] = useState("");
  const [notes, setNotes] = useState("");
  const [estimatedDuration, setEstimatedDuration] = useState("");
  const [estimatedCost, setEstimatedCost] = useState("");

  // Preview state
  const [previewSteps, setPreviewSteps] = useState<ParsedStepPreview[]>([]);
  const [previewDuration, setPreviewDuration] = useState<number | null>(null);
  const [previewCost, setPreviewCost] = useState<number | null>(null);
  const [isParsing, setIsParsing] = useState(false);
  const [parseError, setParseError] = useState<string | null>(null);
  const [hasPreview, setHasPreview] = useState(false);

  const canParse = rawDescription.trim().length >= 10;
  const canSubmit =
    origin.trim().length > 0 &&
    destination.trim().length > 0 &&
    rawDescription.trim().length >= 10;

  const handleParsePreview = async () => {
    if (!canParse) return;

    setIsParsing(true);
    setParseError(null);

    try {
      const result = await parsePreview({
        raw_description: rawDescription,
        origin: origin || undefined,
        destination: destination || undefined,
      });

      setPreviewSteps(result.steps);
      setPreviewDuration(result.total_estimated_duration_mins);
      setPreviewCost(result.total_estimated_cost_bdt);
      setHasPreview(true);
    } catch (err: any) {
      setParseError(
        err?.response?.data?.detail ||
          "Failed to parse description. Please try again.",
      );
    } finally {
      setIsParsing(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;

    await onSubmit({
      origin: origin.trim(),
      destination: destination.trim(),
      raw_description: rawDescription.trim(),
      notes: notes.trim() || null,
      estimated_duration_mins: estimatedDuration
        ? parseInt(estimatedDuration)
        : null,
      estimated_cost_bdt: estimatedCost ? parseFloat(estimatedCost) : null,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Origin & Destination */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="origin">Origin *</Label>
          <Input
            id="origin"
            placeholder="e.g. Dhaka"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="destination">Destination *</Label>
          <Input
            id="destination"
            placeholder="e.g. Lawachara National Park"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            required
          />
        </div>
      </div>

      {/* Raw Description */}
      <div className="space-y-2">
        <Label htmlFor="raw-description">
          Transit Description *
        </Label>
        <p className="text-xs text-muted-foreground">
          Write the step-by-step route in natural language. Our AI will parse it
          into structured directions.
        </p>
        <Textarea
          id="raw-description"
          placeholder="e.g. Take Shyamoli Paribahan bus from Sayedabad terminal to Srimangal (about 4 hours, 450 taka). From Srimangal bus stand, hire a local CNG for 80 taka to Lawachara National Park entry gate. Then walk 20 minutes to the observation tower."
          value={rawDescription}
          onChange={(e) => {
            setRawDescription(e.target.value);
            setHasPreview(false);
          }}
          rows={5}
          required
          minLength={10}
        />
      </div>

      {/* AI Parse Preview button */}
      <div className="flex items-center gap-3">
        <Button
          type="button"
          variant="outline"
          onClick={handleParsePreview}
          disabled={!canParse || isParsing}
          className="gap-2"
        >
          {isParsing ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Parsing with AI...
            </>
          ) : (
            <>
              <Sparkles size={16} />
              Preview AI Parse
            </>
          )}
        </Button>
        {hasPreview && (
          <span className="text-xs text-green-600 flex items-center gap-1">
            <Eye size={12} />
            Preview ready — check below
          </span>
        )}
      </div>

      {/* Parse Error */}
      {parseError && (
        <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-lg border border-destructive/20">
          {parseError}
        </div>
      )}

      {/* Preview Steps */}
      {hasPreview && previewSteps.length > 0 && (
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader className="p-4 pb-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold flex items-center gap-2">
                <Sparkles size={14} className="text-primary" />
                AI-Parsed Steps Preview
              </h3>
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                {previewDuration != null && (
                  <span>
                    Total:{" "}
                    {previewDuration >= 60
                      ? `${Math.floor(previewDuration / 60)}h ${previewDuration % 60}m`
                      : `${previewDuration}m`}
                  </span>
                )}
                {previewCost != null && (
                  <span>৳{previewCost.toLocaleString()}</span>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <BlueprintStepTimeline steps={previewSteps} />
          </CardContent>
        </Card>
      )}

      {/* Optional fields */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="est-duration">
            Estimated Total Duration (minutes)
          </Label>
          <Input
            id="est-duration"
            type="number"
            placeholder="e.g. 300"
            value={estimatedDuration}
            onChange={(e) => setEstimatedDuration(e.target.value)}
            min={0}
          />
          <p className="text-xs text-muted-foreground">
            Leave blank to use AI estimate
          </p>
        </div>
        <div className="space-y-2">
          <Label htmlFor="est-cost">Estimated Total Cost (BDT)</Label>
          <Input
            id="est-cost"
            type="number"
            placeholder="e.g. 530"
            value={estimatedCost}
            onChange={(e) => setEstimatedCost(e.target.value)}
            min={0}
            step="0.01"
          />
          <p className="text-xs text-muted-foreground">
            Leave blank to use AI estimate
          </p>
        </div>
      </div>

      {/* Notes */}
      <div className="space-y-2">
        <Label htmlFor="notes">Notes & Tips (optional)</Label>
        <Textarea
          id="notes"
          placeholder="e.g. Road conditions might be bad during monsoon season. CNG prices may vary..."
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={3}
        />
      </div>

      {/* Submit */}
      <div className="flex justify-end pt-2">
        <Button
          type="submit"
          disabled={!canSubmit || isLoading}
          className="gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Creating...
            </>
          ) : (
            <>
              <Send size={16} />
              Submit Blueprint
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
