import { useState, useRef } from "react";
import { PhotoItem } from "@/types/community";
import { Button } from "@/components/ui/button";
import { ImagePlus, X, Trash2, ImageIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { Label } from "@/components/ui/label";

interface PhotoUploaderProps {
  existingPhotos?: PhotoItem[];
  onPhotosChange: (files: File[]) => void;
  onDeleteExisting?: (photoId: string) => void;
}

export function PhotoUploader({
  existingPhotos = [],
  onPhotosChange,
  onDeleteExisting,
}: PhotoUploaderProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      addFiles(Array.from(e.target.files));
    }
  };

  const addFiles = (files: File[]) => {
    const newFiles = [...selectedFiles, ...files];
    setSelectedFiles(newFiles);
    onPhotosChange(newFiles);

    const newPreviews = files.map((file) => URL.createObjectURL(file));
    setPreviews([...previews, ...newPreviews]);
  };

  const removeNewPhoto = (index: number) => {
    URL.revokeObjectURL(previews[index]);
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    const newPreviews = previews.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);
    setPreviews(newPreviews);
    onPhotosChange(newFiles);
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files) {
      addFiles(Array.from(e.dataTransfer.files));
    }
  };

  return (
    <div className="space-y-4">
      <Label>Photos</Label>
      
      <div
        className={cn(
          "relative border-2 border-dashed rounded-xl p-8 transition-colors flex flex-col items-center justify-center gap-3 cursor-pointer",
          isDragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
        )}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="bg-primary/10 p-4 rounded-full text-primary">
          <ImagePlus size={32} />
        </div>
        <div className="text-center">
          <p className="font-medium text-sm">Click to upload or drag and drop</p>
          <p className="text-xs text-muted-foreground mt-1">PNG, JPG, WebP up to 10MB</p>
        </div>
        <input
          type="file"
          multiple
          accept="image/*"
          className="hidden"
          ref={fileInputRef}
          onChange={handleFileChange}
        />
      </div>

      {(existingPhotos.length > 0 || previews.length > 0) && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 mt-6">
          {/* Existing Photos */}
          {existingPhotos.map((photo) => (
            <div key={photo.id} className="relative group aspect-square rounded-lg overflow-hidden border bg-muted">
              <img src={photo.url} alt="Existing" className="h-full w-full object-cover" />
              <Button
                variant="destructive"
                size="icon"
                className="absolute top-1 right-1 h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteExisting?.(photo.id);
                }}
                type="button"
              >
                <Trash2 size={14} />
              </Button>
              <div className="absolute bottom-0 left-0 right-0 bg-black/50 py-1 text-center">
                <span className="text-[10px] text-white font-medium">Existing</span>
              </div>
            </div>
          ))}

          {/* New Photos Previews */}
          {previews.map((preview, index) => (
            <div key={index} className="relative group aspect-square rounded-lg overflow-hidden border bg-muted">
              <img src={preview} alt="Preview" className="h-full w-full object-cover" />
              <Button
                variant="destructive"
                size="icon"
                className="absolute top-1 right-1 h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => {
                  e.stopPropagation();
                  removeNewPhoto(index);
                }}
                type="button"
              >
                <X size={14} />
              </Button>
              <div className="absolute bottom-0 left-0 right-0 bg-primary/80 py-1 text-center">
                <span className="text-[10px] text-white font-medium">New</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
