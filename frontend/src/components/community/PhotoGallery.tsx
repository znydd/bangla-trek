import { useState } from "react";
import { PhotoItem } from "@/types/community";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, ImageIcon } from "lucide-react";

interface PhotoGalleryProps {
  photos: PhotoItem[];
}

export function PhotoGallery({ photos }: PhotoGalleryProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  if (photos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 bg-muted/30 rounded-xl border-2 border-dashed border-border/50 text-muted-foreground">
        <ImageIcon size={40} strokeWidth={1} className="mb-2 opacity-20" />
        <p className="text-sm">No photos available</p>
      </div>
    );
  }

  const handlePrevious = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (selectedIndex !== null) {
      setSelectedIndex((selectedIndex - 1 + photos.length) % photos.length);
    }
  };

  const handleNext = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (selectedIndex !== null) {
      setSelectedIndex((selectedIndex + 1) % photos.length);
    }
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {photos.map((photo, index) => (
          <div
            key={photo.id}
            className="group relative aspect-square overflow-hidden rounded-lg bg-muted cursor-zoom-in border"
            onClick={() => setSelectedIndex(index)}
          >
            <img
              src={photo.url}
              alt={photo.caption || "Gallery image"}
              className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
            {photo.caption && (
              <div className="absolute inset-x-0 bottom-0 bg-black/60 p-2 translate-y-full transition-transform group-hover:translate-y-0">
                <p className="text-[10px] text-white line-clamp-1">{photo.caption}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      <Dialog
        open={selectedIndex !== null}
        onOpenChange={(open) => !open && setSelectedIndex(null)}
      >
        <DialogContent className="sm:max-w-4xl max-h-[90vh] p-0 overflow-hidden bg-black/95 border-none">
          <DialogHeader className="sr-only">
            <DialogTitle>Photo Lightbox</DialogTitle>
          </DialogHeader>
          
          <div className="relative flex flex-col h-full items-center justify-center min-h-[400px]">
            {selectedIndex !== null && (
              <>
                <img
                  src={photos[selectedIndex].url}
                  alt={photos[selectedIndex].caption || "Full size image"}
                  className="max-h-[80vh] max-w-full object-contain"
                />
                
                {photos.length > 1 && (
                  <>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute left-4 top-1/2 -translate-y-1/2 text-white hover:bg-white/20 rounded-full h-12 w-12"
                      onClick={handlePrevious}
                    >
                      <ChevronLeft size={32} />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-white hover:bg-white/20 rounded-full h-12 w-12"
                      onClick={handleNext}
                    >
                      <ChevronRight size={32} />
                    </Button>
                  </>
                )}

                <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/80 to-transparent p-6 text-white text-center">
                  {photos[selectedIndex].caption && (
                    <p className="text-sm font-medium mb-1">{photos[selectedIndex].caption}</p>
                  )}
                  <p className="text-xs text-white/60">
                    {selectedIndex + 1} / {photos.length}
                  </p>
                </div>
              </>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
