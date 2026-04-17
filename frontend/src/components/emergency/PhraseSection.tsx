import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { EmergencyPhraseCategory } from "@/types/emergency";
import { Copy, Check } from "lucide-react";
import { useState } from "react";

interface PhraseSectionProps {
  categories: EmergencyPhraseCategory[];
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleCopy}
      className="h-7 w-7 p-0 shrink-0"
      title="Copy Bengali text"
    >
      {copied ? (
        <Check size={12} className="text-green-600" />
      ) : (
        <Copy size={12} />
      )}
    </Button>
  );
}

export function PhraseSection({ categories }: PhraseSectionProps) {
  return (
    <div className="space-y-6">
      {categories.map((category) => (
        <div key={category.category}>
          <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
            {category.category}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {category.phrases.map((phrase) => (
              <Card
                key={phrase.id}
                className="border-border/50 hover:border-primary/20 transition-all"
              >
                <CardContent className="p-3 space-y-1.5">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm font-medium">{phrase.english}</p>
                    <CopyButton text={phrase.bengali} />
                  </div>
                  <p className="text-base font-semibold text-primary">
                    {phrase.bengali}
                  </p>
                  <p className="text-xs text-muted-foreground italic">
                    {phrase.romanized}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
