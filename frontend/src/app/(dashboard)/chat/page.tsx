"use client";

import { MessageSquare } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { ChatInput } from "@/components/chat/chat-input";
import { ConversationList } from "@/components/chat/conversation-list";
import { MessageBubble } from "@/components/chat/message-bubble";
import { useConversation } from "@/hooks/use-chat";
import { useChatStream } from "@/hooks/use-chat";

export default function ChatPage() {
  const [activeId, setActiveId] = useState<string | null>(null);
  const { data: conversation } = useConversation(activeId);
  const stream = useChatStream(activeId ?? "");
  const scrollRef = useRef<HTMLDivElement>(null);

  // Switching conversations must clear any leftover streaming state
  // (error/answer text/etc.) from whatever was previously active —
  // otherwise a stale error banner from a prior conversation lingers
  // and shows on a brand new one that was never actually asked anything.
  useEffect(() => {
    stream.reset();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [conversation?.messages, stream.streamedText]);

  const handleSend = (question: string) => {
    if (!activeId) return;
    stream.send(question);
  };

  const messages = conversation?.messages ?? [];
  const hasMessages = messages.length > 0 || stream.isStreaming || stream.streamedText;

  return (
    <div className="flex h-full">
      <ConversationList activeId={activeId} onSelect={(id) => setActiveId(id || null)} />

      <div className="flex flex-1 flex-col">
        {!activeId ? (
          <EmptyState />
        ) : (
          <>
            <div ref={scrollRef} className="flex-1 overflow-y-auto py-4">
              {!hasMessages && (
                <p className="px-6 py-10 text-center text-sm text-ink/40 dark:text-paper/40">
                  Ask a question about your uploaded documents to get started.
                </p>
              )}
              {messages.map((m) => (
                <MessageBubble
                  key={m.id}
                  messageId={m.id}
                  role={m.role}
                  content={m.content}
                  citations={m.citations}
                  feedback={m.feedback}
                />
              ))}
              {stream.pendingQuestion && (
                <MessageBubble role="user" content={stream.pendingQuestion} />
              )}
              {stream.isStreaming || stream.streamedText ? (
                <MessageBubble
                  role="assistant"
                  content={stream.streamedText}
                  citations={stream.citations}
                  isStreaming={stream.isStreaming}
                />
              ) : null}
              {stream.error && (
                <p className="mx-6 rounded-card bg-danger-soft px-4 py-2.5 text-[13px] text-danger">
                  {stream.error}
                </p>
              )}
            </div>
            <ChatInput
              onSend={handleSend}
              onStop={stream.stop}
              isStreaming={stream.isStreaming}
              showSuggestions={!hasMessages}
            />
          </>
        )}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center text-center">
      <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-highlighter-soft">
        <MessageSquare className="h-5 w-5 text-highlighter-dark" />
      </span>
      <p className="font-display text-lg text-ink dark:text-paper">Start a new conversation</p>
      <p className="mt-1 max-w-sm text-sm text-ink/50 dark:text-paper/50">
        Pick an existing conversation on the left, or create a new one to start asking your documents
        questions.
      </p>
    </div>
  );
}
