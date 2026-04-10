import { useState, useRef, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { BANGLADESH_DESTINATIONS } from "@/data/destinations";
import { MapPin } from "lucide-react";

interface DestinationComboboxProps {
  value: string;
  onChange: (value: string) => void;
  id?: string;
  placeholder?: string;
  required?: boolean;
}

export function DestinationCombobox({
  value,
  onChange,
  id,
  placeholder = "Search destinations...",
  required,
}: DestinationComboboxProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState(value);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Sync external value changes
  useEffect(() => {
    setSearch(value);
  }, [value]);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filtered = BANGLADESH_DESTINATIONS.filter((d) =>
    d.toLowerCase().includes(search.toLowerCase())
  );

  const handleSelect = (destination: string) => {
    setSearch(destination);
    onChange(destination);
    setOpen(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSearch(val);
    onChange(val);
    setOpen(true);
  };

  return (
    <div ref={wrapperRef} className="relative">
      <Input
        id={id}
        value={search}
        onChange={handleInputChange}
        onFocus={() => setOpen(true)}
        placeholder={placeholder}
        required={required}
        autoComplete="off"
      />
      {open && filtered.length > 0 && (
        <div className="absolute z-50 mt-1 w-full max-h-56 overflow-auto rounded-md border bg-popover shadow-md">
          {filtered.map((destination) => (
            <button
              key={destination}
              type="button"
              onClick={() => handleSelect(destination)}
              className={`
                flex w-full items-center gap-2 px-3 py-2 text-sm cursor-pointer transition-colors
                hover:bg-accent hover:text-accent-foreground
                ${destination === value ? "bg-accent/50 font-medium" : ""}
              `}
            >
              <MapPin size={14} className="shrink-0 text-muted-foreground" />
              {destination}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
