"use client";

import { Send, Square } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/input";

const SUGGESTIONS = [
  "Summarize the key points of this document",
  "What are the main risks mentioned?",
  "List any dates or deadlines referenced",
];

interface ChatInputProps {
  onSend: (question: string) => void;
  onStop: () => void;
  isStreaming: boolean;
  showSuggestions?: boolean;
}

export function ChatInput({ onSend, onStop, isStreaming, showSuggestions }: ChatInputProps) {
  const [value, setValue] = useState("");

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || isStreaming) return;
    onSend(trimmed);
    setValue("");
  };

  return (
    <div className="border-t border-ink/8 dark:border-ink-border bg-paper dark:bg-ink px-6 py-4">
      {showSuggestions && (
        <div className="mb-3 flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => setValue(s)}
              className="rounded-full border border-ink/12 dark:border-ink-border px-3 py-1.5 text-[12px] text-ink/60 dark:text-paper/60 hover:border-ink/25 dark:hover:border-ink-border hover:text-ink dark:hover:text-paper"
            >
              {s}
            </button>
          ))}
        </div>
      )}
      <div className="flex items-end gap-3">
        <Textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Ask a question about your documents…"
          className="max-h-40"
          rows={1}
        />
        {isStreaming ? (
          <Button variant="outline" size="icon" onClick={onStop} aria-label="Stop generating">
            <Square className="h-4 w-4" />
          </Button>
        ) : (
          <Button size="icon" onClick={submit} aria-label="Send message" disabled={!value.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}
