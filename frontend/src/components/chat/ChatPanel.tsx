import { useState, useRef, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  chatHistoryQueryOptions,
  sendChatMessage,
} from "@/services/chat.service";
import { Button } from "@/components/ui/button";
import {
  MessageCircle,
  Send,
  Loader2,
  X,
  Bot,
  User,
  Sparkles,
} from "lucide-react";
import { toast } from "sonner";
import type { ChatMessage } from "@/types/chat";

interface ChatPanelProps {
  itineraryId: string;
  destination: string;
  onItineraryUpdated?: () => void;
}

export default function ChatPanel({
  itineraryId,
  destination,
  onItineraryUpdated,
}: ChatPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const queryClient = useQueryClient();

  const { data: history = [], isLoading: isLoadingHistory } = useQuery({
    ...chatHistoryQueryOptions(itineraryId),
    enabled: isOpen,
  });

  const sendMutation = useMutation({
    mutationFn: sendChatMessage,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["chat", itineraryId] });
      if (data.updated_activities) {
        toast.success("Itinerary updated based on AI suggestions!");
        queryClient.invalidateQueries({
          queryKey: ["itineraries", itineraryId],
        });
        onItineraryUpdated?.();
      }
      setMessage("");
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || "Failed to send message. Try again."
      );
    },
  });

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, sendMutation.isPending]);

  // Focus input when panel opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const handleSend = () => {
    const trimmed = message.trim();
    if (!trimmed || sendMutation.isPending) return;

    sendMutation.mutate({
      itinerary_id: itineraryId,
      message: trimmed,
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const SUGGESTIONS = [
    "Add more nature spots",
    `Make it under 5000 taka`,
    "Add local street food stops",
    "Make the schedule more relaxed",
    "Add cultural experiences",
    "Suggest hidden gems nearby",
  ];

  // Floating toggle button
  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-2 bg-primary text-primary-foreground 
                   px-4 py-3 rounded-full shadow-lg hover:shadow-xl transition-all 
                   hover:scale-105 active:scale-95 cursor-pointer"
        id="chat-toggle-btn"
      >
        <MessageCircle size={20} />
        <span className="font-medium text-sm hidden sm:inline">
          Refine with AI
        </span>
      </button>
    );
  }

  return (
    <div
      className="fixed bottom-0 right-0 z-50 w-full sm:w-[420px] h-[600px] sm:bottom-6 sm:right-6 
                    sm:rounded-2xl overflow-hidden shadow-2xl border bg-background flex flex-col"
      id="chat-panel"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b bg-primary/5">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary/10">
            <Bot size={18} className="text-primary" />
          </div>
          <div>
            <h3 className="font-semibold text-sm">AI Travel Assistant</h3>
            <p className="text-xs text-muted-foreground">
              Refining: {destination}
            </p>
          </div>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="p-1.5 rounded-lg hover:bg-muted transition-colors cursor-pointer"
        >
          <X size={16} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
        {isLoadingHistory ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : history.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4 space-y-4">
            <div className="p-3 rounded-full bg-primary/10">
              <Sparkles className="h-8 w-8 text-primary" />
            </div>
            <div>
              <p className="font-semibold">Refine Your Itinerary</p>
              <p className="text-sm text-muted-foreground mt-1">
                Tell me how you'd like to adjust your {destination} trip. Try
                something like:
              </p>
            </div>
            <div className="flex flex-wrap gap-2 justify-center">
              {SUGGESTIONS.slice(0, 4).map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => {
                    setMessage(suggestion);
                    inputRef.current?.focus();
                  }}
                  className="text-xs px-3 py-1.5 rounded-full border bg-background
                             hover:bg-accent transition-colors cursor-pointer"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {history.map((msg: ChatMessage) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {sendMutation.isPending && (
              <div className="flex items-start gap-2">
                <div className="p-1.5 rounded-full bg-primary/10 shrink-0 mt-0.5">
                  <Bot size={14} className="text-primary" />
                </div>
                <div className="bg-muted rounded-2xl rounded-tl-sm px-3 py-2">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 size={14} className="animate-spin" />
                    Thinking...
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick suggestions (when there's history) */}
      {history.length > 0 && !sendMutation.isPending && (
        <div className="px-4 pb-1 flex gap-1.5 overflow-x-auto">
          {SUGGESTIONS.slice(0, 3).map((s) => (
            <button
              key={s}
              onClick={() => {
                setMessage(s);
                inputRef.current?.focus();
              }}
              className="text-xs px-2.5 py-1 rounded-full border bg-background 
                         hover:bg-accent transition-colors whitespace-nowrap shrink-0 cursor-pointer"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="px-4 py-3 border-t">
        <div className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask to refine your itinerary..."
            rows={1}
            className="flex-1 resize-none rounded-xl border bg-muted/50 px-3 py-2 text-sm
                       placeholder:text-muted-foreground focus:outline-none focus:ring-1 
                       focus:ring-ring min-h-[40px] max-h-[100px]"
            style={{
              height: "auto",
              minHeight: "40px",
            }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = "auto";
              target.style.height =
                Math.min(target.scrollHeight, 100) + "px";
            }}
          />
          <Button
            size="sm"
            onClick={handleSend}
            disabled={!message.trim() || sendMutation.isPending}
            className="rounded-xl h-10 w-10 p-0 shrink-0"
          >
            {sendMutation.isPending ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Send size={16} />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex items-start gap-2 ${isUser ? "flex-row-reverse" : ""}`}
    >
      <div
        className={`p-1.5 rounded-full shrink-0 mt-0.5 ${
          isUser ? "bg-primary text-primary-foreground" : "bg-primary/10"
        }`}
      >
        {isUser ? (
          <User size={14} />
        ) : (
          <Bot size={14} className="text-primary" />
        )}
      </div>
      <div
        className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm leading-relaxed ${
          isUser
            ? "bg-primary text-primary-foreground rounded-tr-sm"
            : "bg-muted rounded-tl-sm"
        }`}
      >
        {message.content.split("\n").map((line, i) => (
          <p key={i} className={i > 0 ? "mt-1" : ""}>
            {line}
          </p>
        ))}
        <p
          className={`text-[10px] mt-1 ${
            isUser
              ? "text-primary-foreground/60"
              : "text-muted-foreground/60"
          }`}
        >
          {new Date(message.created_at).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
}
