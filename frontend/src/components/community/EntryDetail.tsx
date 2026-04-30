import { CommunityEntry } from "@/types/community";
import { PhotoGallery } from "./PhotoGallery";
import { VideoEmbedPlayer } from "./VideoEmbedPlayer";
import { AmenitiesList } from "./AmenitiesList";
import { TagBadge } from "./TagBadge";
import { CategoryIcon, getCategoryLabel } from "./CategoryIcon";
import { getPriceRangeLabel } from "./EntryCard";
import { useAuth } from "@/hooks/useAuth";
import { NomadMetrics } from "./NomadMetrics";
import { LocationMap } from "@/components/community/LocationMap";
import { ReviewsSection } from "@/components/reviews/ReviewsSection";
import { 
  MoreVertical, 
  Edit, 
  Trash2, 
  MapPin, 
  Clock, 
  Calendar, 
  User as UserIcon,
  ChevronLeft,
  AlertTriangle,
  Loader2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import { Link } from "@tanstack/react-router";
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface EntryDetailProps {
  entry: CommunityEntry;
  onDelete?: (id: string) => Promise<void>;
  isDeleting?: boolean;
}

export function EntryDetail({ entry, onDelete, isDeleting }: EntryDetailProps) {
  const { user } = useAuth();
  const isAuthor = user?.id === entry.user_id;
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const handleDelete = async () => {
    if (onDelete) {
      await onDelete(entry.id);
      setShowDeleteDialog(false);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-5xl">
      <div className="mb-6">
        <Button variant="ghost" size="sm" render={<Link to="/community" />} className="-ml-2 text-muted-foreground">
          <ChevronLeft size={16} className="mr-1" />
          Back to community
        </Button>
      </div>

      <div className="flex flex-col md:flex-row justify-between items-start gap-4 mb-8">
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            {entry.tags.map((tag) => (
              <TagBadge key={tag} tag={tag} className="px-3 py-1 text-sm" />
            ))}
            <div className="flex items-center gap-1.5 bg-secondary px-3 py-1 rounded-full text-sm font-medium">
              <CategoryIcon category={entry.category} size={14} />
              <span>{getCategoryLabel(entry.category)}</span>
            </div>
          </div>
          <h1 className="text-4xl font-bold tracking-tight">{entry.name}</h1>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <MapPin size={18} className="text-primary" />
              <span>{entry.location}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Clock size={18} />
              <span>{getPriceRangeLabel(entry.price_range)}</span>
            </div>
          </div>
        </div>

        {isAuthor && (
          <DropdownMenu>
            <DropdownMenuTrigger render={<Button variant="outline" size="icon" className="rounded-full" />}>
              <MoreVertical size={20} />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-40">
              <DropdownMenuItem render={<Link to="/community/$entryId/edit" params={{ entryId: entry.id }} className="w-full" />}>
                <Edit size={16} className="mr-2" />
                Edit Entry
              </DropdownMenuItem>
              <DropdownMenuItem 
                variant="destructive"
                onClick={() => setShowDeleteDialog(true)}
              >
                <Trash2 size={16} className="mr-2" />
                Delete Entry
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        {/* ... (rest of the component content) ... */}
        <div className="lg:col-span-2 space-y-10">
          <section>
            <h2 className="text-2xl font-semibold mb-4">Photos</h2>
            <PhotoGallery photos={entry.photos} />
          </section>

          <section className="bg-muted/30 p-6 rounded-2xl border border-border/50">
            <h2 className="text-2xl font-semibold mb-4">Travel Tips</h2>
            <div className="prose prose-sm dark:prose-invert max-w-none">
              {entry.travel_tips ? (
                <p className="whitespace-pre-wrap text-foreground/80 leading-relaxed">
                  {entry.travel_tips}
                </p>
              ) : (
                <p className="text-muted-foreground italic">No tips provided for this location.</p>
              )}
            </div>
          </section>

          <ReviewsSection entryId={entry.id} />
        </div>

        <div className="space-y-8">
          <section className="bg-card rounded-2xl border p-6 shadow-sm">
            <h3 className="font-semibold text-lg mb-4">Information</h3>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="bg-primary/10 p-2 rounded-lg text-primary">
                  <UserIcon size={20} />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">Contributed by</p>
                  <p className="font-medium">{entry.author_name}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="bg-primary/10 p-2 rounded-lg text-primary">
                  <Calendar size={20} />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">Posted on</p>
                  <p className="font-medium">{new Date(entry.created_at).toLocaleDateString(undefined, { dateStyle: 'long' })}</p>
                </div>
              </div>
            </div>

            <Separator className="my-6" />

            <h3 className="font-semibold text-lg mb-4">Amenities</h3>
            <AmenitiesList amenities={entry.amenities} />
          </section>
          <section>
            <h3 className="font-semibold text-lg mb-3">Location</h3>
            <LocationMap
              latitude={entry.latitude}
              longitude={entry.longitude}
              locationQuery={entry.location}
              name={entry.name}
            />
          </section>
          {entry.video_embeds.length > 0 && (
            <section className="space-y-4">
              <h3 className="font-semibold text-xl">Videos</h3>
              <div className="grid grid-cols-1 gap-4">
                {entry.video_embeds.map((embed) => (
                  <VideoEmbedPlayer key={embed.id} embed={embed} />
                ))}
              </div>
            </section>
          )}
        </div>
      </div>
      <NomadMetrics entryId={entry.id} />
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <div className="flex items-center gap-2 text-destructive mb-2">
              <AlertTriangle size={20} />
              <DialogTitle>Confirm Deletion</DialogTitle>
            </div>
            <DialogDescription>
              Are you sure you want to delete <span className="font-semibold text-foreground">"{entry.name}"</span>? 
              This action cannot be undone and will permanently remove this entry from the community data.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-4 gap-2">
            <Button
              variant="ghost"
              onClick={() => setShowDeleteDialog(false)}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={isDeleting}
              className="min-w-25"
            >
              {isDeleting ? (
                <>
                  <Loader2 size={16} className="mr-2 animate-spin" />
                  Deleting...
                </>
              ) : (
                "Delete Entry"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
