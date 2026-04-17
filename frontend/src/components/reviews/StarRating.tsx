import { Star } from "lucide-react";
import { cn } from "@/lib/utils";

interface StarRatingProps {
  value: number;
  onChange?: (value: number) => void;
  size?: "sm" | "md" | "lg";
  label?: string;
}

const sizeClass = {
  sm: "h-4 w-4",
  md: "h-5 w-5",
  lg: "h-7 w-7",
};

export function StarRating({
  value,
  onChange,
  size = "md",
  label,
}: StarRatingProps) {
  const interactive = Boolean(onChange);

  return (
    <div className="flex items-center gap-1" aria-label={label}>
      {[1, 2, 3, 4, 5].map((star) => {
        const filled = star <= Math.round(value);
        const icon = (
          <Star
            className={cn(
              sizeClass[size],
              filled
                ? "fill-amber-400 text-amber-400"
                : "fill-transparent text-muted-foreground/30",
            )}
          />
        );

        if (!interactive) {
          return <span key={star}>{icon}</span>;
        }

        return (
          <button
            key={star}
            type="button"
            onClick={() => onChange?.(star)}
            className="rounded-sm transition-transform hover:scale-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            aria-label={`${star} star${star === 1 ? "" : "s"}`}
          >
            {icon}
          </button>
        );
      })}
    </div>
  );
}
