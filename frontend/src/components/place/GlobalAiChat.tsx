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
  Paperclip,
  PanelRightClose,
  X,
  Loader2,
  Sparkles,
  Plus,
  History,
  Trash2,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";

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
  useSidebar,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { LoginModal } from "@/components/ui/login-modal";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import aiMascot from "@/data/ai_mascot.svg";
import svgSparkle from "@/data/ai_sparkle.svg";
import { useAuth } from "@/hooks/useAuth";
import {
  createAIConversation,
  listAIConversations,
  streamAIMessage,
  addPlaceToAIContext,
  removePlaceFromAIContext,
  getAIConversationDetail,
  deleteAIConversation,
  type AIConversationRead,
} from "@/services/ai.service";

interface GlobalAiChatProps {
  width: number;
  onWidthChange: (width: number) => void;
  onResizeStateChange: (resizing: boolean) => void;
}

interface ChatMessage {
  id: string | number;
  role: "assistant" | "user";
  text: string;
}

interface ContextItem {
  id?: string;
  name: string;
}

interface AiContextEventDetail {
  placeName: string;
  placeId?: string;
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
  const { isMobile, open, openMobile, setOpen, setOpenMobile } = useSidebar();
  const { isAuthenticated } = useAuth();

  const [isResizing, setIsResizing] = useState(false);
  const [contexts, setContexts] = useState<ContextItem[]>([]);
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<AIConversationRead[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [deletingConvId, setDeletingConvId] = useState<string | null>(null);
  const [loginOpen, setLoginOpen] = useState(false);

  const visible = isMobile ? openMobile : open;

  const refreshConversations = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const list = await listAIConversations();
      setConversations(list);
    } catch {
      // ignore
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (visible && isAuthenticated) {
      void refreshConversations();
    }
  }, [visible, isAuthenticated, refreshConversations]);

  const handleNewChat = async () => {
    if (!isAuthenticated) {
      setLoginOpen(true);
      return;
    }
    try {
      const newConv = await createAIConversation("Bangla Trek Trip Chat");
      setActiveConvId(newConv.id);
      setMessages([]);
      setContexts([]);
      void refreshConversations();
    } catch {
      setActiveConvId(null);
      setMessages([]);
      setContexts([]);
    }
  };

  const handleSelectConversation = async (convId: string) => {
    if (convId === activeConvId) return;
    setActiveConvId(convId);
    try {
      const detail = await getAIConversationDetail(convId);
      if (detail.messages && detail.messages.length > 0) {
        setMessages(
          detail.messages.map((m) => ({
            id: m.id,
            role: m.role as "user" | "assistant",
            text: m.content,
          })),
        );
      } else {
        setMessages([]);
      }
      if (detail.context_places) {
        setContexts(
          detail.context_places.map((cp) => ({
            id: cp.place_id,
            name: cp.name,
          })),
        );
      } else {
        setContexts([]);
      }
    } catch {
      // fallback
    }
  };

  const handleDeleteConversation = async (
    e: React.MouseEvent,
    convId: string,
  ) => {
    e.stopPropagation();
    e.preventDefault();
    if (deletingConvId) return;
    setDeletingConvId(convId);
    try {
      await deleteAIConversation(convId);
      if (activeConvId === convId) {
        setActiveConvId(null);
        setMessages([]);
        setContexts([]);
      }
      await refreshConversations();
    } catch {
      // fallback
    } finally {
      setDeletingConvId(null);
    }
  };

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
    const toggleAssistant = () => {
      if (!isAuthenticated) {
        setLoginOpen(true);
        return;
      }
      setAssistantOpen(!visible);
    };
    window.addEventListener(TOGGLE_GLOBAL_AI_CHAT_EVENT, toggleAssistant);
    return () =>
      window.removeEventListener(TOGGLE_GLOBAL_AI_CHAT_EVENT, toggleAssistant);
  }, [setAssistantOpen, visible, isAuthenticated]);

  // Handle adding place context from event
  useEffect(() => {
    const addContext = async (event: Event) => {
      if (!isAuthenticated) {
        setLoginOpen(true);
        return;
      }
      const { placeName, placeId } = (
        event as CustomEvent<AiContextEventDetail>
      ).detail;
      if (!placeName) return;

      setContexts((current) => {
        if (current.some((c) => c.name === placeName)) return current;
        return [...current, { name: placeName, id: placeId }];
      });

      // If active conversation exists and placeId is provided, sync with backend DB
      if (activeConvId && placeId) {
        try {
          await addPlaceToAIContext(activeConvId, placeId);
        } catch {
          // fallback
        }
      }

      setAssistantOpen(true);
    };

    window.addEventListener(ADD_GLOBAL_AI_CONTEXT_EVENT, addContext);
    return () =>
      window.removeEventListener(ADD_GLOBAL_AI_CONTEXT_EVENT, addContext);
  }, [setAssistantOpen, isAuthenticated, activeConvId]);

  // Init AI conversation when sidebar opens and authenticated
  useEffect(() => {
    if (!visible || !isAuthenticated || activeConvId) return;

    const initConv = async () => {
      try {
        const convs = await listAIConversations();
        if (convs.length > 0) {
          setActiveConvId(convs[0].id);
        } else {
          const newConv = await createAIConversation(
            "Bangla Trek Trip Assistant",
          );
          setActiveConvId(newConv.id);
        }
      } catch {
        // Fallback for local testing
      }
    };
    initConv();
  }, [visible, isAuthenticated, activeConvId]);

  // Load conversation details (past messages and pinned place contexts) when activeConvId is set
  useEffect(() => {
    if (!activeConvId || !isAuthenticated) return;

    const loadDetail = async () => {
      try {
        const detail = await getAIConversationDetail(activeConvId);
        if (detail.messages && detail.messages.length > 0) {
          setMessages(
            detail.messages.map((m) => ({
              id: m.id,
              role: m.role as "user" | "assistant",
              text: m.content,
            })),
          );
        }
        if (detail.context_places && detail.context_places.length > 0) {
          setContexts((current) => {
            const existingNames = new Set(current.map((c) => c.name));
            const fetchedItems = detail.context_places.map((cp) => ({
              id: cp.place_id,
              name: cp.name,
            }));
            const merged = [...current];
            for (const item of fetchedItems) {
              if (!existingNames.has(item.name)) {
                merged.push(item);
              }
            }
            return merged;
          });
        }
      } catch {
        // Fallback for unauthenticated or test mode
      }
    };
    loadDetail();
  }, [activeConvId, isAuthenticated]);

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

  const removeContextItem = async (item: ContextItem) => {
    setContexts((current) => current.filter((c) => c.name !== item.name));
    if (activeConvId && item.id) {
      try {
        await removePlaceFromAIContext(activeConvId, item.id);
      } catch {
        // fallback
      }
    }
  };

  const sendPrompt = async () => {
    const cleanPrompt = prompt.trim();
    if (!cleanPrompt || isStreaming) return;
    if (!isAuthenticated) {
      setLoginOpen(true);
      return;
    }

    const userMsgId = Date.now();
    const assistantMsgId = Date.now() + 1;

    setMessages((current) => [
      ...current,
      { id: userMsgId, role: "user", text: cleanPrompt },
      { id: assistantMsgId, role: "assistant", text: "" },
    ]);
    setPrompt("");
    setIsStreaming(true);

    let convId = activeConvId;
    if (!convId && isAuthenticated) {
      try {
        const newConv = await createAIConversation(cleanPrompt.slice(0, 30));
        convId = newConv.id;
        setActiveConvId(convId);
      } catch {
        // ignore
      }
    }

    if (convId && isAuthenticated) {
      await streamAIMessage(
        convId,
        cleanPrompt,
        (chunk) => {
          setMessages((current) =>
            current.map((msg) =>
              msg.id === assistantMsgId
                ? { ...msg, text: msg.text + chunk }
                : msg,
            ),
          );
        },
        () => {
          setIsStreaming(false);
        },
        () => {
          setIsStreaming(false);
        },
      );
    } else {
      // Local fallback mode
      const contextNames = contexts.map((c) => c.name).join(", ");
      const mockText =
        contexts.length > 0
          ? `Bangla Trek AI recommendations considering **${contextNames}**:\n\n### Travel Guide\n• **Best Season**: Oct–Mar.\n• **Transport**: Hire local CNG or Chander Gari.\n• **Payment**: Carry cash or bKash.\n\n*Check local weather before traveling.*`
          : `Hello! I am **Bangla Trek AI**. Please add a place (e.g. Sajek Valley, Debotakhum) to ground recommendations in community reviews & budget stats.`;

      for (const word of mockText.split(" ")) {
        await new Promise((r) => setTimeout(r, 60));
        setMessages((current) =>
          current.map((msg) =>
            msg.id === assistantMsgId
              ? { ...msg, text: msg.text + word + " " }
              : msg,
          ),
        );
      }
      setIsStreaming(false);
    }
  };

  return (
    <>
      <LoginModal
        open={loginOpen}
        onOpenChange={setLoginOpen}
        action="use the AI travel assistant"
      />
      {!visible && (
        <button
          type="button"
          aria-label="Open AI sidebar"
          title="Ask Bangla Trek AI"
          onClick={() => {
            if (!isAuthenticated) {
              setLoginOpen(true);
            } else {
              setAssistantOpen(true);
            }
          }}
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
        className="z-50 inset-y-2! mr-2 h-[calc(100svh-1rem)]! rounded-2xl border border-zinc-200 bg-sidebar shadow-none! group-data-[collapsible=offcanvas]:invisible group-data-[collapsible=offcanvas]:mr-0! [&>[data-slot=sidebar-inner]]:rounded-2xl [&>[data-slot=sidebar-inner]]:overflow-hidden"
        style={{ width: `${width}px`, borderColor: "#e4e4e7", boxShadow: "none" }}
      >
        {!isMobile && visible && (
          <button
            type="button"
            aria-label="Resize AI sidebar width"
            onPointerDown={startResize}
            onPointerMove={resize}
            onPointerUp={finishResize}
            onPointerCancel={finishResize}
            className="absolute left-0 top-0 z-20 flex h-full w-4 -translate-x-1/2 cursor-col-resize items-center justify-center opacity-0 transition-opacity hover:opacity-100 focus-visible:opacity-100"
          >
            <span className="flex h-12 w-1.5 items-center justify-center rounded-full bg-zinc-300 shadow-sm" />
          </button>
        )}
        <SidebarHeader className="h-16 flex-row items-center justify-between border-b px-3.5 py-0 shrink-0">
          <div className="flex min-w-0 items-center gap-2">
            <Button
              type="button"
              size="icon-sm"
              variant="ghost"
              aria-label="Close AI assistant"
              onClick={() => setAssistantOpen(false)}
            >
              <PanelRightClose />
            </Button>
            <img
              src={aiMascot}
              alt=""
              className="ai-mascot-hover size-12 shrink-0"
            />
            <div className="min-w-0">
              <h2 className="truncate text-sm font-semibold">Bangla Trek AI</h2>
              <p className="truncate text-[11px] text-muted-foreground">
                Travel assistant
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            {/* New Chat Button */}
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={handleNewChat}
              className="h-8 gap-1 rounded-xl border-emerald-200 bg-emerald-50 px-2.5 text-xs font-semibold text-emerald-800 hover:bg-emerald-100 hover:text-emerald-900"
              title="Start a new conversation"
            >
              <Plus size={14} strokeWidth={2.5} />
              <span className="hidden sm:inline">New Chat</span>
            </Button>

            {/* History Dropdown */}
            <DropdownMenu onOpenChange={(open) => open && void refreshConversations()}>
              <DropdownMenuTrigger
                render={
                  <Button
                    type="button"
                    size="icon-sm"
                    variant="ghost"
                    className="h-8 w-8 rounded-xl text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                    title="Chat History"
                    aria-label="Chat History"
                  />
                }
              >
                <History size={16} />
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-64 max-h-80 overflow-y-auto">
                <DropdownMenuGroup>
                  <DropdownMenuLabel className="text-xs font-bold uppercase tracking-wider text-muted-foreground px-2 py-1">
                    Chat History
                  </DropdownMenuLabel>
                </DropdownMenuGroup>
                <DropdownMenuSeparator />
                {conversations.length === 0 ? (
                  <div className="p-3 text-center text-xs text-muted-foreground">
                    No previous chats
                  </div>
                ) : (
                  conversations.map((conv) => (
                    <DropdownMenuItem
                      key={conv.id}
                      onClick={() => void handleSelectConversation(conv.id)}
                      className={`group flex items-center justify-between text-xs py-2 px-2.5 cursor-pointer rounded-lg ${
                        conv.id === activeConvId
                          ? "bg-emerald-50 text-emerald-950 font-semibold"
                          : "text-zinc-700 hover:bg-zinc-100"
                      }`}
                    >
                      <span className="truncate flex-1 pr-2">
                        {conv.title || "Trip Chat"}
                      </span>
                      <div className="flex items-center gap-1 shrink-0">
                        <button
                          type="button"
                          title="Delete chat history"
                          aria-label="Delete chat history"
                          disabled={deletingConvId === conv.id}
                          onClick={(e) => void handleDeleteConversation(e, conv.id)}
                          className="rounded p-1 text-zinc-400 hover:bg-red-100 hover:text-red-600 transition-colors disabled:opacity-50"
                        >
                          {deletingConvId === conv.id ? (
                            <Loader2 size={13} className="animate-spin text-red-600" />
                          ) : (
                            <Trash2 size={13} />
                          )}
                        </button>
                      </div>
                    </DropdownMenuItem>
                  ))
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </SidebarHeader>

        <SidebarContent className="relative flex min-h-0 flex-1 flex-col overflow-hidden bg-background">
          <ChatContainerRoot className="relative min-h-0 flex-1 overflow-y-auto [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-thumb]:bg-zinc-300 [&::-webkit-scrollbar-thumb]:rounded-full">
            <ChatContainerContent className="min-h-full gap-5 px-4 py-6">
              {messages.length === 0 ? (
                <div className="flex min-h-[50vh] flex-col items-center justify-center px-4 text-center">
                  <span className="flex size-12 items-center justify-center rounded-2xl">
                    <img src={svgSparkle} className="size-20" alt="" />
                  </span>
                  <h3 className="mt-4 text-base font-semibold">
                    Where do you want to go in Bangladesh?
                  </h3>
                  <p className="mt-1 max-w-xs text-xs leading-5 text-muted-foreground">
                    Ask about itineraries, travel routes, budgets, or attach place cards from Bangla Trek.
                  </p>

                  {contexts.length === 0 && (
                    <div className="mt-6 w-full rounded-2xl border border-amber-200/80 bg-amber-50/70 p-3.5 text-left text-xs leading-5 text-amber-900 shadow-xs">
                      <p className="font-semibold flex items-center gap-1.5 text-amber-950">
                        <Sparkles className="size-3.5 text-amber-600 shrink-0" />
                        No place context attached
                      </p>
                      <p className="mt-1 text-[11px] text-amber-800 leading-4">
                        For accurate local guides and cost estimates, click <strong>"Use in AI chat"</strong> on any place card (e.g. Sajek, Debotakhum).
                      </p>
                    </div>
                  )}
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
                          : "max-w-[88%] rounded-2xl rounded-bl-md border bg-white px-4 py-3 text-sm leading-relaxed text-zinc-800"
                      }
                    >
                      {message.role === "assistant" ? (
                        message.text ? (
                          <div className="prose prose-sm prose-emerald max-w-none text-zinc-800 font-sans [&_p]:mb-2 [&_p:last-child]:mb-0 [&_ul]:mb-3 [&_ul]:list-disc [&_ul]:pl-4 [&_ol]:mb-3 [&_ol]:list-decimal [&_ol]:pl-4 [&_h1]:text-base [&_h1]:font-bold [&_h1]:mb-2 [&_h2]:text-sm [&_h2]:font-bold [&_h2]:mb-1.5 [&_h3]:text-xs [&_h3]:font-bold [&_h3]:mt-3 [&_h3]:mb-1 [&_h4]:text-xs [&_h4]:font-bold [&_h4]:mt-2 [&_h4]:mb-1 [&_li]:mb-1 [&_strong]:font-semibold [&_strong]:text-zinc-950">
                            <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                              {message.text}
                            </ReactMarkdown>
                          </div>
                        ) : isStreaming ? (
                          <Loader2 className="animate-spin size-4 text-zinc-500" />
                        ) : null
                      ) : (
                        <span className="whitespace-pre-wrap">{message.text}</span>
                      )}
                    </MessageContent>
                  </Message>
                ))
              )}
              <ChatContainerScrollAnchor />
            </ChatContainerContent>
            <ScrollButton className="absolute bottom-3 left-1/2 -translate-x-1/2 shadow-md" />
          </ChatContainerRoot>
        </SidebarContent>

        <SidebarFooter className="border-t bg-sidebar p-3 shrink-0">
          {contexts.length === 0 && (
            <div className="mb-2 flex items-center justify-between rounded-lg border border-amber-200/80 bg-amber-50/80 px-2.5 py-1.5 text-[11px] font-medium text-amber-900">
              <span className="flex items-center gap-1.5 truncate">
                <Sparkles className="size-3.5 text-amber-600 shrink-0" />
                No place context attached
              </span>
              <span className="text-[10px] text-amber-700 shrink-0">
                Attach a place card
              </span>
            </div>
          )}

          <PromptInput
            value={prompt}
            onValueChange={setPrompt}
            onSubmit={sendPrompt}
            maxHeight={180}
            className="!rounded-xl border-sidebar-border bg-background p-2 shadow-lg shadow-black/5"
          >
            {contexts.length > 0 && (
              <div className="flex flex-wrap gap-2 px-2 pt-1 pb-1">
                {contexts.map((context) => (
                  <span
                    key={context.name}
                    className="relative flex min-h-8 items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 py-1 pl-2.5 pr-8 text-xs font-semibold text-emerald-800"
                  >
                    <MapPin className="size-3.5 shrink-0" />
                    {context.name}
                    <button
                      type="button"
                      aria-label={`Remove ${context.name} from AI chat`}
                      title={`Remove ${context.name}`}
                      onClick={(event) => {
                        event.stopPropagation();
                        void removeContextItem(context);
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
                </Button>
              </PromptInputActions>

              <Button
                type="submit"
                size="icon-sm"
                className="rounded-full bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50"
                disabled={!prompt.trim() || isStreaming}
              >
                <ArrowUp />
              </Button>
            </div>
          </PromptInput>
        </SidebarFooter>
      </Sidebar>
    </>
  );
}
