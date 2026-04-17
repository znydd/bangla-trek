import { useState } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { translatePhrase } from "@/services/emergency.service";
import type { TranslateResponse } from "@/types/emergency";
import { Languages, Loader2, Sparkles, Copy, Check } from "lucide-react";

const DIALECTS = [
  { value: "standard", label: "Standard Bengali" },
  { value: "sylheti", label: "Sylheti (সিলেটি)" },
  { value: "chittagonian", label: "Chittagonian (চাটগাঁইয়া)" },
  { value: "barisali", label: "Barisali (বরিশাইল্যা)" },
  { value: "rangpuri", label: "Rangpuri (রংপুরী)" },
];

export function CustomTranslator() {
  const [text, setText] = useState("");
  const [dialect, setDialect] = useState("standard");
  const [result, setResult] = useState<TranslateResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const canTranslate = text.trim().length > 0;

  const handleTranslate = async () => {
    if (!canTranslate) return;
    setIsLoading(true);
    setError(null);

    try {
      const res = await translatePhrase({
        text: text.trim(),
        dialect: dialect !== "standard" ? dialect : undefined,
      });
      setResult(res);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail || "Translation failed. Please try again.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async (copyText: string) => {
    await navigator.clipboard.writeText(copyText);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <Card className="border-border/50">
      <CardHeader className="p-5 pb-3">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Languages size={18} className="text-primary" />
          AI Dialect Translator
        </h2>
        <p className="text-sm text-muted-foreground">
          Type any emergency phrase in English and our AI will translate it into
          Bengali or a local dialect.
        </p>
      </CardHeader>
      <CardContent className="p-5 pt-0 space-y-4">
        <Textarea
          placeholder="e.g. I need help, my friend is hurt and we are lost in the hills"
          value={text}
          onChange={(e) => {
            setText(e.target.value);
            setResult(null);
          }}
          rows={3}
        />

        <div className="flex items-center gap-3">
          <Select
            value={dialect}
            onValueChange={(value) => {
              if (value) setDialect(value);
            }}
          >
            <SelectTrigger className="w-[220px]">
              <SelectValue placeholder="Select dialect" />
            </SelectTrigger>
            <SelectContent>
              {DIALECTS.map((d) => (
                <SelectItem key={d.value} value={d.value}>
                  {d.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button
            onClick={handleTranslate}
            disabled={!canTranslate || isLoading}
            className="gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Translating...
              </>
            ) : (
              <>
                <Sparkles size={16} />
                Translate
              </>
            )}
          </Button>
        </div>

        {error && (
          <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-lg border border-destructive/20">
            {error}
          </div>
        )}

        {result && (
          <div className="bg-primary/5 border border-primary/20 rounded-xl p-4 space-y-4">
            {/* Standard Bengali */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  Bengali
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCopy(result.bengali)}
                  className="h-7 px-2 gap-1 text-xs"
                >
                  {copied ? <Check size={12} /> : <Copy size={12} />}
                  Copy
                </Button>
              </div>
              <p className="text-xl font-semibold text-primary leading-relaxed">
                {result.bengali}
              </p>
              <p className="text-sm text-muted-foreground italic mt-1">
                {result.romanized}
              </p>
            </div>

            {/* Dialect version */}
            {result.dialect_text && (
              <div className="border-t border-primary/10 pt-3">
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  {result.dialect} Dialect
                </span>
                <p className="text-xl font-semibold text-primary leading-relaxed mt-1">
                  {result.dialect_text}
                </p>
                {result.dialect_romanized && (
                  <p className="text-sm text-muted-foreground italic mt-1">
                    {result.dialect_romanized}
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
