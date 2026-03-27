import { VideoEmbed } from "@/types/community";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Plus, Trash2, Youtube, Facebook, Music2, AlertCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface VideoEmbedInputProps {
  videos: { url: string; platform: VideoEmbed["platform"] }[];
  onChange: (videos: { url: string; platform: VideoEmbed["platform"] }[]) => void;
}

export function VideoEmbedInput({ videos, onChange }: VideoEmbedInputProps) {
  const detectPlatform = (url: string): VideoEmbed["platform"] => {
    if (url.includes("youtube.com") || url.includes("youtu.be")) return "youtube";
    if (url.includes("facebook.com")) return "facebook";
    if (url.includes("tiktok.com")) return "tiktok";
    return "youtube"; // default
  };

  const handleUrlChange = (index: number, url: string) => {
    const newVideos = [...videos];
    newVideos[index] = {
      url,
      platform: detectPlatform(url),
    };
    onChange(newVideos);
  };

  const addVideo = () => {
    onChange([...videos, { url: "", platform: "youtube" }]);
  };

  const removeVideo = (index: number) => {
    onChange(videos.filter((_, i) => i !== index));
  };

  const getIcon = (platform: VideoEmbed["platform"]) => {
    switch (platform) {
      case "youtube": return <Youtube size={14} className="text-red-600" />;
      case "facebook": return <Facebook size={14} className="text-blue-600" />;
      case "tiktok": return <Music2 size={14} className="text-pink-600" />;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Label>Video Reels (YouTube, Facebook, TikTok)</Label>
        <Button 
          type="button" 
          variant="outline" 
          size="sm" 
          onClick={addVideo}
          className="h-8 rounded-full"
        >
          <Plus size={14} className="mr-1" />
          Add Video
        </Button>
      </div>

      <div className="space-y-3">
        {videos.map((video, index) => (
          <div key={index} className="flex gap-2 items-start">
            <div className="flex-1 relative">
              <Input
                placeholder="Paste video URL here..."
                value={video.url}
                onChange={(e) => handleUrlChange(index, e.target.value)}
                className="pr-24"
              />
              {video.url && (
                <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                  <Badge variant="secondary" className="h-5 px-1.5 text-[10px] flex items-center gap-1 font-normal">
                    {getIcon(video.platform)}
                    <span className="capitalize">{video.platform}</span>
                  </Badge>
                </div>
              )}
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => removeVideo(index)}
              className="text-muted-foreground hover:text-destructive h-9 w-9 shrink-0"
            >
              <Trash2 size={18} />
            </Button>
          </div>
        ))}

        {videos.length === 0 && (
          <div className="text-center py-6 bg-muted/20 rounded-xl border-2 border-dashed flex flex-col items-center justify-center text-muted-foreground italic">
            <p className="text-xs">No videos added yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
