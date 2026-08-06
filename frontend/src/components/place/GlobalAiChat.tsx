import {
  useCallback,
  useEffect,
  useState,
  type PointerEvent,
} from "react";
import {
  ArrowUp,
  Bot,
  Globe2,
  MapPin,
  MoreHorizontal,
  Paperclip,
  PanelRightClose,
  X,
} from "lucide-react";
import {
  ChatContainerContent,
  ChatContainerRoot,
  ChatContainerScrollAnchor,
} from "@/components/ui/chat-container";
import { Message, MessageContent } from "@/components/ui/message";
import {
  PromptInput,
  PromptInputActions,
  PromptInputTextarea,
} from "@/components/ui/prompt-input";
import { ScrollButton } from "@/components/ui/scroll-button";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
  useSidebar,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import aiMascot from "@/data/ai_mascot.svg";
import svgSparkle from "@/data/ai_sparkle.svg";
import dragHandle from "@/data/drag-handle-svgrepo-com.svg";

interface GlobalAiChatProps {
  width: number;
  onWidthChange: (width: number) => void;
  onResizeStateChange: (resizing: boolean) => void;
}

interface ChatMessage {
  id: number;
  role: "assistant" | "user";
  text: string;
}

interface AiContextEventDetail {
  placeName: string;
}

export const TOGGLE_GLOBAL_AI_CHAT_EVENT = "bangla-trek:toggle-ai-chat";
export const ADD_GLOBAL_AI_CONTEXT_EVENT = "bangla-trek:add-ai-context";
const DEFAULT_SIDEBAR_WIDTH = 440;
const SIDEBAR_CLOSE_THRESHOLD = 280;

export function GlobalAiChat({
  width,
  onWidthChange,
  onResizeStateChange,
}: GlobalAiChatProps) {
  const {
    isMobile,
    open,
    openMobile,
    setOpen,
    setOpenMobile,
  } = useSidebar();
  const [isResizing, setIsResizing] = useState(false);
  const [contexts, setContexts] = useState<string[]>([]);
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const visible = isMobile ? openMobile : open;

  const setAssistantOpen = useCallback(
    (nextOpen: boolean) => {
      if (isMobile) {
        setOpenMobile(nextOpen);
      } else {
        setOpen(nextOpen);
      }
    },
    [isMobile, setOpen, setOpenMobile],
  );

  useEffect(() => {
    const toggleAssistant = () => setAssistantOpen(!visible);
    window.addEventListener(TOGGLE_GLOBAL_AI_CHAT_EVENT, toggleAssistant);
    return () =>
      window.removeEventListener(TOGGLE_GLOBAL_AI_CHAT_EVENT, toggleAssistant);
  }, [setAssistantOpen, visible]);

  useEffect(() => {
    const addContext = (event: Event) => {
      const { placeName } = (event as CustomEvent<AiContextEventDetail>).detail;
      if (!placeName) return;

      setContexts((current) =>
        current.includes(placeName) ? current : [...current, placeName],
      );
      setAssistantOpen(true);
    };

    window.addEventListener(ADD_GLOBAL_AI_CONTEXT_EVENT, addContext);
    return () =>
      window.removeEventListener(ADD_GLOBAL_AI_CONTEXT_EVENT, addContext);
  }, [setAssistantOpen]);

  useEffect(() => {
    if (!isResizing) return;

    const previousUserSelect = document.body.style.userSelect;
    const previousCursor = document.body.style.cursor;
    document.body.style.userSelect = "none";
    document.body.style.cursor = "col-resize";

    return () => {
      document.body.style.userSelect = previousUserSelect;
      document.body.style.cursor = previousCursor;
    };
  }, [isResizing]);

  const clampWidth = (nextWidth: number) => {
    const maximumWidth = Math.max(320, Math.min(720, window.innerWidth - 560));
    return Math.min(maximumWidth, Math.max(320, nextWidth));
  };

  const startResize = (event: PointerEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);
    setIsResizing(true);
    onResizeStateChange(true);
  };

  const resize = (event: PointerEvent<HTMLButtonElement>) => {
    if (!event.currentTarget.hasPointerCapture(event.pointerId)) return;

    const nextWidth = window.innerWidth - event.clientX;

    if (nextWidth <= SIDEBAR_CLOSE_THRESHOLD) {
      event.currentTarget.releasePointerCapture(event.pointerId);
      setIsResizing(false);
      onResizeStateChange(false);
      onWidthChange(clampWidth(DEFAULT_SIDEBAR_WIDTH));
      setAssistantOpen(false);
      return;
    }

    onWidthChange(clampWidth(nextWidth));
  };

  const finishResize = (event: PointerEvent<HTMLButtonElement>) => {
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    setIsResizing(false);
    onResizeStateChange(false);
  };

  const sendPrompt = () => {
    const cleanPrompt = prompt.trim();
    if (!cleanPrompt) return;

    setMessages((current) => [
      ...current,
      { id: Date.now(), role: "user", text: cleanPrompt },
      {
        id: Date.now() + 1,
        role: "assistant",
        text:
          contexts.length > 0
            ? "This UI preview would answer using " +
            contexts.join(", ") +
            " as travel context. The real AI response will be connected later."
            : "This is the chat UI preview. Add a place from its card or detail page later, then the assistant will use it as context.",
      },
    ]);
    setPrompt("");
  };

  return (
    <>
      {!visible && (
        <button
          type="button"
          aria-label="Open AI sidebar"
          title="Ask Bangla Trek AI"
          onClick={() => setAssistantOpen(true)}
          className="group fixed bottom-12 right-12 z-[60] flex size-[160px] items-center justify-center rounded-full bg-transparent p-0 transition-transform hover:scale-110 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500 sm:bottom-16 sm:right-16"
        >
          <span
            aria-hidden="true"
            className="absolute bottom-1 h-3 w-11 rounded-full bg-violet-500/20 blur-md transition-transform group-hover:scale-125"
          />
          <img
            src={aiMascot}
            alt=""
            className="ai-mascot-hover relative size-[100px] drop-shadow-lg"
          />
        </button>
      )}

      <Sidebar
        side="right"
        variant="sidebar"
        collapsible="offcanvas"
        aria-label="Bangla Trek AI assistant"
        className="z-50 inset-y-2! mr-2 h-[calc(100svh-1rem)]! rounded-2xl border border-zinc-200 bg-sidebar shadow-none! group-data-[collapsible=offcanvas]:invisible group-data-[collapsible=offcanvas]:mr-0! [&>[data-slot=sidebar-inner]]:rounded-2xl"
        style={{ borderColor: "#e4e4e7", boxShadow: "none" }}
      >
        <SidebarHeader className="h-16 flex-row items-center  border-b px-4 py-0">
          <Button
            type="button"
            size="icon-sm"
            variant="ghost"
            aria-label="Close AI assistant"
            onClick={() => setAssistantOpen(false)}
          >
            <PanelRightClose />
          </Button>
          <div className="flex min-w-0 items-center gap-3">
            <img
              src={aiMascot}
              alt=""
              className="ai-mascot-hover size-16 shrink-0"
            />
            <div className="min-w-0">
              <h2 className="truncate text-sm font-semibold">Bangla Trek AI</h2>
              <p className="truncate text-xs text-muted-foreground">
                Your Bangladesh travel assistant
              </p>
            </div>
          </div>

        </SidebarHeader>

        <SidebarContent className="relative overflow-hidden bg-background">
          <ChatContainerRoot className="relative min-h-0 flex-1">
            <ChatContainerContent className="min-h-full gap-5 px-4 py-6">
              {messages.length === 0 ? (
                <div className="flex min-h-[55vh] flex-col items-center justify-center px-6 text-center">
                  <span className="flex size-12 items-center justify-center rounded-2xl ">
                    <img
                      src={svgSparkle}
                      className="size-24"
                    />
                  </span>
                  <h3 className="mt-4 text-base font-semibold">
                    Where do you want to go?
                  </h3>
                  <p className="mt-1 max-w-xs text-sm leading-6 text-muted-foreground">
                    Ask about routes, budgets, seasons or compare places you
                    attach from Bangla Trek.
                  </p>
                </div>
              ) : (
                messages.map((message) => (
                  <Message
                    key={message.id}
                    className={
                      message.role === "user" ? "justify-end" : "justify-start"
                    }
                  >
                    {message.role === "assistant" && (
                      <span className="mt-1 flex size-7 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-800">
                        <Bot size={14} />
                      </span>
                    )}
                    <MessageContent
                      className={
                        message.role === "user"
                          ? "max-w-[85%] rounded-2xl rounded-br-md bg-zinc-950 px-4 py-3 text-sm leading-6 text-white"
                          : "max-w-[85%] rounded-2xl rounded-bl-md border bg-white px-4 py-3 text-sm leading-6"
                      }
                    >
                      {message.text}
                    </MessageContent>
                  </Message>
                ))
              )}
              <ChatContainerScrollAnchor />
            </ChatContainerContent>
            <ScrollButton className="absolute bottom-3 left-1/2 -translate-x-1/2 shadow-md" />
          </ChatContainerRoot>
        </SidebarContent>

        <SidebarFooter className="border-t bg-sidebar p-3">
          <PromptInput
            value={prompt}
            onValueChange={setPrompt}
            onSubmit={sendPrompt}
            maxHeight={180}
            className="!rounded-xl border-sidebar-border bg-background p-2 shadow-lg shadow-black/5"
          >
            {contexts.length > 0 && (
              <div className="flex flex-wrap gap-2 px-2 pt-1">
                {contexts.map((context) => (
                  <span
                    key={context}
                    className="relative flex min-h-8 items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 py-1 pl-2.5 pr-9 text-xs font-semibold text-emerald-800"
                  >
                    <MapPin className="size-3.5 shrink-0" />
                    {context}
                    <button
                      type="button"
                      aria-label={`Remove ${context} from AI chat`}
                      title={`Remove ${context}`}
                      onClick={(event) => {
                        event.stopPropagation();
                        setContexts((current) =>
                          current.filter((item) => item !== context),
                        );
                      }}
                      className="absolute right-1 top-1/2 flex size-5 -translate-y-1/2 items-center justify-center rounded-xl bg-emerald-800 text-white shadow-sm transition-colors hover:bg-red-600 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-700"
                    >
                      <X className="size-3" strokeWidth={2.5} />
                    </button>
                  </span>
                ))}
              </div>
            )}

            <PromptInputTextarea
              placeholder="Message Bangla Trek AI"
              className="min-h-14 px-3 py-3 text-base text-foreground placeholder:text-muted-foreground"
            />

            <div className="flex items-center justify-between gap-3 px-1 pb-1">
              <PromptInputActions>
                <Button
                  type="button"
                  size="icon-sm"
                  variant="outline"
                  className="rounded-full"
                  title="Attach"
                  aria-label="Attach"
                >
                  <Paperclip />
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  className="rounded-full"
                >
                  <Globe2 />
                  Search
                </Button>
                <Button
                  type="button"
                  size="icon-sm"
                  variant="outline"
                  className="rounded-full"
                  title="More options"
                  aria-label="More options"
                >
                  <MoreHorizontal />
                </Button>
              </PromptInputActions>

              <Button
                type="button"
                size="icon"
                aria-label="Send message"
                disabled={!prompt.trim()}
                onClick={sendPrompt}
                className="size-9 shrink-0 rounded-full bg-zinc-950 text-white hover:bg-zinc-800"
              >
                <ArrowUp />
              </Button>
            </div>
          </PromptInput>
          <p className="px-2 pb-1 text-center text-[10px] text-muted-foreground">
            Login and live AI responses will be connected later.
          </p>
        </SidebarFooter>

        <SidebarRail
          tabIndex={0}
          aria-label={"Resize AI sidebar. Current width " + width + " pixels."}
          title="Drag to resize · double-click to reset"
          onClick={(event) => event.preventDefault()}
          onPointerDown={startResize}
          onPointerMove={resize}
          onPointerUp={finishResize}
          onPointerCancel={finishResize}
          onDoubleClick={() => onWidthChange(clampWidth(DEFAULT_SIDEBAR_WIDTH))}
          onKeyDown={(event) => {
            if (event.key === "ArrowLeft") {
              event.preventDefault();
              onWidthChange(clampWidth(width + 20));
            }
            if (event.key === "ArrowRight") {
              event.preventDefault();
              onWidthChange(clampWidth(width - 20));
            }
          }}
          className={cn(
            "!cursor-col-resize touch-none after:hidden! group-data-[collapsible=offcanvas]:hidden!",
            isResizing && "bg-transparent!",
          )}
        >
          <span
            aria-hidden="true"
            className="pointer-events-none absolute left-1/2 top-1/2 flex h-8 w-5 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-md border border-zinc-300 bg-white shadow-none dark:bg-zinc-900"
          >
            <img
              src={dragHandle}
              alt=""
              className="size-3 opacity-70 dark:invert"
            />
          </span>
          <span className="sr-only">Resize sidebar</span>
        </SidebarRail>
      </Sidebar>
    </>
  );
}
