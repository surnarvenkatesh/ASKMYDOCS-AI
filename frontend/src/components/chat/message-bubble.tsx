"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, RotateCcw } from "lucide-react";
import { useState } from "react";
import { CitationCard } from "@/components/chat/citation-card";
import { TypingIndicator } from "@/components/chat/typing-indicator";
import type { Citation, MessageRole } from "@/types/api";

interface MessageBubbleProps {
  role: MessageRole;
  content: string;
  citations?: Citation[];
  isStreaming?: boolean;
  onRegenerate?: () => void;
}

export function MessageBubble({ role, content, citations = [], isStreaming, onRegenerate }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const isUser = role === "user";

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  if (isUser) {
    return (
      <div className="flex justify-end px-6 py-2">
        <div className="max-w-[70%] rounded-card bg-ink px-4 py-2.5 text-[14px] text-paper dark:bg-ink-card">{content}</div>
      </div>
    );
  }

  return (
    <div className="px-6 py-4">
      <div className="max-w-3xl">
        {content ? (
          <div className="prose-chat text-ink dark:text-paper">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        ) : isStreaming ? (
          <TypingIndicator />
        ) : null}

        {citations.length > 0 && (
          <div className="mt-3 flex gap-3 overflow-x-auto pb-1">
            {citations.map((citation) => (
              <CitationCard key={citation.ref_id} citation={citation} />
            ))}
          </div>
        )}

        {!isStreaming && content && (
          <div className="mt-2 flex items-center gap-3 text-ink/40 dark:text-paper/40">
            <button onClick={handleCopy} className="flex items-center gap-1 text-[12px] hover:text-ink/70 dark:hover:text-paper/70">
              <Copy className="h-3.5 w-3.5" /> {copied ? "Copied" : "Copy"}
            </button>
            {onRegenerate && (
              <button onClick={onRegenerate} className="flex items-center gap-1 text-[12px] hover:text-ink/70 dark:hover:text-paper/70">
                <RotateCcw className="h-3.5 w-3.5" /> Regenerate
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
