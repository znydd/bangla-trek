import { MapPin, Hotel, BedDouble, Home, UtensilsCrossed, LucideProps } from "lucide-react";
import { EntryCategory } from "@/types/community";

interface CategoryIconProps extends LucideProps {
  category: EntryCategory;
}

export function CategoryIcon({ category, ...props }: CategoryIconProps) {
  switch (category) {
    case "attraction":
      return <MapPin {...props} />;
    case "hotel":
      return <Hotel {...props} />;
    case "guesthouse":
      return <BedDouble {...props} />;
    case "homestay":
      return <Home {...props} />;
    case "restaurant":
      return <UtensilsCrossed {...props} />;
    default:
      return null;
  }
}

export function getCategoryLabel(category: EntryCategory) {
  switch (category) {
    case "attraction":
      return "Attraction";
    case "hotel":
      return "Hotel";
    case "guesthouse":
      return "Guesthouse";
    case "homestay":
      return "Homestay";
    case "restaurant":
      return "Restaurant";
    default:
      return category;
  }
}
