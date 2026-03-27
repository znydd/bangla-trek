import { useState } from "react";
import { 
  CommunityEntry, 
  CreateEntryPayload, 
  EntryCategory, 
  PriceRange, 
  EntryTag 
} from "@/types/community";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PhotoUploader } from "./PhotoUploader";
import { VideoEmbedInput } from "./VideoEmbedInput";
import { Badge } from "@/components/ui/badge";
import { X, Plus, Loader2 } from "lucide-react";
import { getCategoryLabel } from "./CategoryIcon";
import { getPriceRangeLabel } from "./EntryCard";
import { cn } from "@/lib/utils";

interface EntryFormProps {
  mode: "create" | "edit";
  defaultValues?: Partial<CommunityEntry>;
  onSubmit: (data: CreateEntryPayload, photos: File[], deletedPhotoIds: string[]) => Promise<void>;
  isLoading?: boolean;
}

export function EntryForm({ mode, defaultValues, onSubmit, isLoading }: EntryFormProps) {
  const [formData, setFormData] = useState<CreateEntryPayload>({
    name: defaultValues?.name || "",
    category: defaultValues?.category || "attraction",
    location: defaultValues?.location || "",
    price_range: defaultValues?.price_range || "mid_range",
    amenities: defaultValues?.amenities || [],
    travel_tips: defaultValues?.travel_tips || "",
    video_embeds: defaultValues?.video_embeds?.map(v => ({ url: v.url, platform: v.platform })) || [],
    tags: defaultValues?.tags || [],
  });

  const [selectedPhotos, setSelectedPhotos] = useState<File[]>([]);
  const [deletedPhotoIds, setDeletedPhotoIds] = useState<string[]>([]);
  const [amenityInput, setAmenityInput] = useState("");

  const handleAmenityKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && amenityInput.trim()) {
      e.preventDefault();
      if (!formData.amenities.includes(amenityInput.trim())) {
        setFormData({
          ...formData,
          amenities: [...formData.amenities, amenityInput.trim()],
        });
      }
      setAmenityInput("");
    }
  };

  const removeAmenity = (index: number) => {
    setFormData({
      ...formData,
      amenities: formData.amenities.filter((_, i) => i !== index),
    });
  };

  const toggleTag = (tag: EntryTag) => {
    const newTags = formData.tags.includes(tag)
      ? formData.tags.filter((t) => t !== tag)
      : [...formData.tags, tag];
    setFormData({ ...formData, tags: newTags });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(formData, selectedPhotos, deletedPhotoIds);
  };

  const categories: EntryCategory[] = ["attraction", "hotel", "guesthouse", "homestay", "restaurant"];
  const priceRanges: PriceRange[] = ["budget", "mid_range", "premium", "luxury"];

  return (
    <form onSubmit={handleSubmit} className="space-y-10 pb-20">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g. Sajek Valley, Panigram Resort"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="location">Location</Label>
          <Input
            id="location"
            required
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            placeholder="e.g. Rangamati, Jessore"
          />
        </div>

        <div className="space-y-2">
          <Label>Category</Label>
          <Select
            value={formData.category}
            onValueChange={(value) => setFormData({ ...formData, category: value as EntryCategory })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {categories.map((cat) => (
                <SelectItem key={cat} value={cat}>
                  {getCategoryLabel(cat)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Price Range</Label>
          <Select
            value={formData.price_range}
            onValueChange={(value) => setFormData({ ...formData, price_range: value as PriceRange })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {priceRanges.map((pr) => (
                <SelectItem key={pr} value={pr}>
                  {getPriceRangeLabel(pr)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-3">
        <Label>Tags</Label>
        <div className="flex gap-3">
          <Button
            type="button"
            variant={formData.tags.includes("trending") ? "secondary" : "outline"}
            className={cn(
              "rounded-full px-6",
              formData.tags.includes("trending") && "bg-orange-100 text-orange-700 border-orange-200 hover:bg-orange-200"
            )}
            onClick={() => toggleTag("trending")}
          >
            Trending
          </Button>
          <Button
            type="button"
            variant={formData.tags.includes("hidden_gem") ? "secondary" : "outline"}
            className={cn(
              "rounded-full px-6",
              formData.tags.includes("hidden_gem") && "bg-emerald-100 text-emerald-700 border-emerald-200 hover:bg-emerald-200"
            )}
            onClick={() => toggleTag("hidden_gem")}
          >
            Hidden Gem
          </Button>
        </div>
      </div>

      <div className="space-y-3">
        <Label htmlFor="amenities">Amenities</Label>
        <div className="flex flex-wrap gap-2 mb-3">
          {formData.amenities.map((amenity, index) => (
            <Badge key={index} variant="secondary" className="pl-3 pr-1 py-1 gap-1">
              {amenity}
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-4 w-4 rounded-full hover:bg-muted"
                onClick={() => removeAmenity(index)}
              >
                <X size={10} />
              </Button>
            </Badge>
          ))}
        </div>
        <div className="relative">
          <Input
            id="amenities"
            value={amenityInput}
            onChange={(e) => setAmenityInput(e.target.value)}
            onKeyDown={handleAmenityKeyDown}
            placeholder="Type amenity and press Enter..."
            className="pr-10"
          />
          <Plus size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="tips">Travel Tips</Label>
        <Textarea
          id="tips"
          rows={5}
          value={formData.travel_tips}
          onChange={(e) => setFormData({ ...formData, travel_tips: e.target.value })}
          placeholder="Share your experience and tips for other travelers..."
          className="resize-none"
        />
      </div>

      <VideoEmbedInput
        videos={formData.video_embeds}
        onChange={(videos) => setFormData({ ...formData, video_embeds: videos })}
      />

      <PhotoUploader
        existingPhotos={defaultValues?.photos}
        onPhotosChange={setSelectedPhotos}
        onDeleteExisting={(id) => setDeletedPhotoIds([...deletedPhotoIds, id])}
      />

      <div className="pt-6 flex justify-end gap-4">
        <Button 
          type="button" 
          variant="ghost" 
          onClick={() => window.history.back()}
          disabled={isLoading}
        >
          Cancel
        </Button>
        <Button type="submit" size="lg" className="px-10" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            mode === "create" ? "Create Entry" : "Save Changes"
          )}
        </Button>
      </div>
    </form>
  );
}
