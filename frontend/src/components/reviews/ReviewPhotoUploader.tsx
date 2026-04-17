import { useRef, useState } from "react";
import { ImagePlus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

interface ReviewPhotoUploaderProps {
  onPhotosChange: (files: File[]) => void;
  disabled?: boolean;
}

export function ReviewPhotoUploader({
  onPhotosChange,
  disabled,
}: ReviewPhotoUploaderProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const addFiles = (newFiles: File[]) => {
    const imageFiles = newFiles.filter((file) => file.type.startsWith("image/"));
    const nextFiles = [...files, ...imageFiles];
    const nextPreviews = [
      ...previews,
      ...imageFiles.map((file) => URL.createObjectURL(file)),
    ];
    setFiles(nextFiles);
    setPreviews(nextPreviews);
    onPhotosChange(nextFiles);
  };

  const removeFile = (index: number) => {
    URL.revokeObjectURL(previews[index]);
    const nextFiles = files.filter((_, i) => i !== index);
    const nextPreviews = previews.filter((_, i) => i !== index);
    setFiles(nextFiles);
    setPreviews(nextPreviews);
    onPhotosChange(nextFiles);
  };

  return (
    <div className="space-y-3">
      <Label>Photos</Label>
      <button
        type="button"
        disabled={disabled}
        onClick={() => inputRef.current?.click()}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setIsDragging(false);
          addFiles(Array.from(event.dataTransfer.files));
        }}
        className={cn(
          "flex w-full flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-6 text-center transition-colors",
          isDragging
            ? "border-primary bg-primary/5"
            : "border-border hover:border-primary/50",
          disabled && "cursor-not-allowed opacity-60",
        )}
      >
        <span className="rounded-full bg-primary/10 p-3 text-primary">
          <ImagePlus size={24} />
        </span>
        <span className="text-sm font-medium">
          Click to upload or drag photos here
        </span>
        <span className="text-xs text-muted-foreground">
          JPG, PNG, or WebP travel photos
        </span>
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        multiple
        className="hidden"
        disabled={disabled}
        onChange={(event) => {
          if (event.target.files) {
            addFiles(Array.from(event.target.files));
          }
        }}
      />

      {previews.length > 0 && (
        <div className="grid grid-cols-3 gap-3 sm:grid-cols-5">
          {previews.map((preview, index) => (
            <div
              key={preview}
              className="group relative aspect-square overflow-hidden rounded-lg border bg-muted"
            >
              <img
                src={preview}
                alt="Review upload preview"
                className="h-full w-full object-cover"
              />
              <Button
                type="button"
                variant="destructive"
                size="icon-xs"
                className="absolute right-1 top-1 opacity-0 transition-opacity group-hover:opacity-100"
                onClick={() => removeFile(index)}
              >
                <X size={12} />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
