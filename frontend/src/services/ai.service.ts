import api from "@/lib/api";

export interface AIConversationRead {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface AIPlaceContextRead {
  place_id: string;
  slug: string;
  name: string;
  category: string;
  district?: string | null;
  upazila?: string | null;
  added_at: string;
}

export interface AIMessageRead {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  model?: string | null;
  status: string;
  created_at: string;
}

export interface AIConversationDetailRead {
  id: string;
  title: string;
  context_places: AIPlaceContextRead[];
  messages: AIMessageRead[];
  created_at: string;
  updated_at: string;
}

export const createAIConversation = async (title: string = "New Conversation"): Promise<AIConversationRead> => {
  const res = await api.post<AIConversationRead>("/api/v1/ai/conversations", { title });
  return res.data;
};

export const listAIConversations = async (): Promise<AIConversationRead[]> => {
  const res = await api.get<AIConversationRead[]>("/api/v1/ai/conversations");
  return res.data;
};

export const getAIConversationDetail = async (id: string): Promise<AIConversationDetailRead> => {
  const res = await api.get<AIConversationDetailRead>(`/api/v1/ai/conversations/${id}`);
  return res.data;
};

export const deleteAIConversation = async (id: string) => {
  await api.delete(`/api/v1/ai/conversations/${id}`);
};

export const addPlaceToAIContext = async (convId: string, placeId: string): Promise<AIConversationDetailRead> => {
  const res = await api.put<AIConversationDetailRead>(`/api/v1/ai/conversations/${convId}/places/${placeId}`);
  return res.data;
};

export const removePlaceFromAIContext = async (convId: string, placeId: string): Promise<AIConversationDetailRead> => {
  const res = await api.delete<AIConversationDetailRead>(`/api/v1/ai/conversations/${convId}/places/${placeId}`);
  return res.data;
};

export const streamAIMessage = async (
  convId: string,
  content: string,
  onChunk: (chunk: string) => void,
  onDone: () => void,
  onError?: (err: unknown) => void
) => {
  const apiBase = import.meta.env.VITE_API_URL || "http://localhost:8000";
  const url = `${apiBase}/api/v1/ai/conversations/${convId}/messages`;

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ content }),
    });

    if (!response.ok) {
      throw new Error(`HTTP Error ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    if (!reader) {
      onDone();
      return;
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith("data: ")) {
          const rawData = trimmed.slice(6);
          if (rawData === "[DONE]") {
            onDone();
            return;
          }
          try {
            const parsed = JSON.parse(rawData);
            if (parsed.chunk) {
              onChunk(parsed.chunk);
            }
          } catch {
            // ignore partial json
          }
        }
      }
    }
    onDone();
  } catch (err) {
    if (onError) onError(err);
    else onDone();
  }
};
