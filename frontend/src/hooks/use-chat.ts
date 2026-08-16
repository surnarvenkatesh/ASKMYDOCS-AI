import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useRef, useState } from "react";
import { API_BASE_URL, apiClient } from "@/lib/api-client";
import { useAuthStore } from "@/lib/auth-store";
import type { Citation, Conversation, ConversationDetail, StreamEvent } from "@/types/api";

const CONVERSATIONS_KEY = ["conversations"];

export function useConversations() {
  return useQuery({
    queryKey: CONVERSATIONS_KEY,
    queryFn: async () => {
      const { data } = await apiClient.get<Conversation[]>("/chat/conversations");
      return data;
    },
  });
}

export function useConversation(conversationId: string | null) {
  return useQuery({
    queryKey: [...CONVERSATIONS_KEY, conversationId],
    queryFn: async () => {
      const { data } = await apiClient.get<ConversationDetail>(`/chat/conversations/${conversationId}`);
      return data;
    },
    enabled: Boolean(conversationId),
  });
}

export function useCreateConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (title?: string) => {
      const { data } = await apiClient.post<Conversation>("/chat/conversations", { title });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CONVERSATIONS_KEY });
    },
  });
}

export function useRenameConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ conversationId, title }: { conversationId: string; title: string }) => {
      const { data } = await apiClient.patch<Conversation>(`/chat/conversations/${conversationId}`, {
        title,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CONVERSATIONS_KEY });
    },
  });
}

export function useDeleteConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (conversationId: string) => {
      await apiClient.delete(`/chat/conversations/${conversationId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CONVERSATIONS_KEY });
    },
  });
}

interface StreamingState {
  isStreaming: boolean;
  pendingQuestion: string | null;
  streamedText: string;
  citations: Citation[];
  warning: string | null;
  error: string | null;
}

/**
 * Consumes the SSE chat endpoint via fetch + ReadableStream (rather than
 * EventSource, which can't send Authorization headers or a JSON body).
 * Parses `data: {...}\n\n` frames as they arrive.
 */
export function useChatStream(conversationId: string, documentIds?: string[]) {
  const queryClient = useQueryClient();
  const [state, setState] = useState<StreamingState>({
    isStreaming: false,
    pendingQuestion: null,
    streamedText: "",
    citations: [],
    warning: null,
    error: null,
  });
  const abortRef = useRef<AbortController | null>(null);

  const send = useCallback(
    async (question: string) => {
      setState({
        isStreaming: true,
        pendingQuestion: question,
        streamedText: "",
        citations: [],
        warning: null,
        error: null,
      });
      const controller = new AbortController();
      abortRef.current = controller;

      const token = useAuthStore.getState().accessToken;

      try {
        const response = await fetch(
          `${API_BASE_URL}/chat/conversations/${conversationId}/messages`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: token ? `Bearer ${token}` : "",
            },
            body: JSON.stringify({ question, document_ids: documentIds ?? null }),
            signal: controller.signal,
          }
        );

        if (!response.body) throw new Error("No response stream from server");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const frames = buffer.split("\n\n");
          buffer = frames.pop() ?? "";

          for (const frame of frames) {
            const line = frame.trim();
            if (!line.startsWith("data:")) continue;
            const event: StreamEvent = JSON.parse(line.slice(5).trim());

            setState((prev) => {
              switch (event.type) {
                case "token":
                  return { ...prev, streamedText: prev.streamedText + event.text };
                case "citations":
                  return { ...prev, citations: event.citations };
                case "warning":
                  return { ...prev, warning: event.text };
                case "error":
                  return { ...prev, error: event.text, isStreaming: false };
                case "done":
                  return { ...prev, isStreaming: false };
                default:
                  return prev;
              }
            });
          }
        }
      } catch (err) {
        if ((err as Error).name !== "AbortError") {
          setState((prev) => ({ ...prev, error: "Connection lost. Please try again.", isStreaming: false }));
        }
      } finally {
        setState((prev) => ({ ...prev, isStreaming: false }));
        await queryClient.invalidateQueries({ queryKey: [...CONVERSATIONS_KEY, conversationId] });
        setState((prev) => ({ ...prev, streamedText: "", citations: [], pendingQuestion: null }));
      }
    },
    [conversationId, documentIds, queryClient]
  );

  const stop = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setState({
      isStreaming: false,
      pendingQuestion: null,
      streamedText: "",
      citations: [],
      warning: null,
      error: null,
    });
  }, []);

  return { ...state, send, stop, reset };
}
