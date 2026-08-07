import { VideoEmbed } from "@/types/community";

interface VideoEmbedPlayerProps {
  embed: VideoEmbed;
}

export function VideoEmbedPlayer({ embed }: VideoEmbedPlayerProps) {
  const getEmbedUrl = (url: string, platform: VideoEmbed["platform"]) => {
    try {
      if (platform === "youtube") {
        // Handle various YouTube URL formats
        let videoId = "";
        const urlObj = new URL(url);
        if (urlObj.hostname === "youtu.be") {
          videoId = urlObj.pathname.slice(1);
        } else if (urlObj.hostname.includes("youtube.com")) {
          videoId = urlObj.searchParams.get("v") || "";
          if (!videoId && urlObj.pathname.startsWith("/embed/")) {
            videoId = urlObj.pathname.split("/")[2];
          }
        }
        return videoId ? `https://www.youtube.com/embed/${videoId}` : null;
      }

      if (platform === "facebook") {
        // Facebook uses a plugin URL
        return `https://www.facebook.com/plugins/video.php?href=${encodeURIComponent(url)}&show_text=0&width=560`;
      }

      if (platform === "tiktok") {
        // TikTok embed URL parsing is tricky, but often follows this pattern
        // Example: https://www.tiktok.com/@user/video/VIDEO_ID
        const match = url.match(/\/video\/(\d+)/);
        if (match && match[1]) {
          return `https://www.tiktok.com/embed/v2/${match[1]}`;
        }
        // Fallback to original URL if it already looks like an embed
        if (url.includes("/embed/")) return url;
      }
    } catch (e) {
      console.error("Invalid URL for video embed", e);
    }
    return null;
  };

  const embedUrl = getEmbedUrl(embed.url, embed.platform);

  if (!embedUrl) {
    return (
      <div className="aspect-video bg-muted flex items-center justify-center rounded-lg border border-dashed text-muted-foreground text-sm">
        Invalid {embed.platform} video URL
      </div>
    );
  }

  return (
    <div className="relative w-full aspect-video rounded-lg overflow-hidden border bg-black">
      <iframe
        src={embedUrl}
        className="absolute top-0 left-0 w-full h-full"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowFullScreen
        title={`${embed.platform} video`}
      />
    </div>
  );
}
