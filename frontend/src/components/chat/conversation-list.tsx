"use client";

import { Check, Loader2, Pencil, Plus, Trash2, X } from "lucide-react";
import { useState } from "react";
import { cn, formatDate } from "@/lib/utils";
import {
  useConversations,
  useCreateConversation,
  useDeleteConversation,
  useRenameConversation,
} from "@/hooks/use-chat";
import type { Conversation } from "@/types/api";

interface ConversationListProps {
  activeId: string | null;
  onSelect: (id: string) => void;
}

export function ConversationList({ activeId, onSelect }: ConversationListProps) {
  const { data: conversations, isLoading } = useConversations();
  const createConversation = useCreateConversation();
  const deleteConversation = useDeleteConversation();
  const renameConversation = useRenameConversation();

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");

  const deletingId = deleteConversation.isPending ? deleteConversation.variables : null;

  const handleCreate = async () => {
    const conversation = await createConversation.mutateAsync(undefined);
    onSelect(conversation.id);
  };

  const startEditing = (c: Conversation) => {
    setEditingId(c.id);
    setEditingTitle(c.title);
  };

  const commitRename = () => {
    const trimmed = editingTitle.trim();
    if (editingId && trimmed) {
      renameConversation.mutate({ conversationId: editingId, title: trimmed });
    }
    setEditingId(null);
  };

  const cancelEditing = () => {
    setEditingId(null);
  };

  return (
    <div className="flex h-full w-72 shrink-0 flex-col border-r border-ink/8 dark:border-ink-border">
      <div className="p-3">
        <button
          onClick={handleCreate}
          className="flex w-full items-center gap-2 rounded-card border border-ink/12 dark:border-ink-border px-3 py-2 text-sm text-ink/70 dark:text-paper/70 hover:bg-ink/5 dark:bg-paper/5"
        >
          <Plus className="h-4 w-4" /> New conversation
        </button>
      </div>
      <div className="flex-1 space-y-0.5 overflow-y-auto px-2">
        {isLoading && <p className="px-3 py-2 text-[13px] text-ink/40 dark:text-paper/40">Loading…</p>}
        {conversations?.length === 0 && (
          <p className="px-3 py-2 text-[13px] text-ink/40 dark:text-paper/40">No conversations yet.</p>
        )}
        {conversations?.map((c: Conversation) => {
          const isEditing = editingId === c.id;
          return (
            <div
              key={c.id}
              className={cn(
                "group flex cursor-pointer items-center justify-between rounded-card px-3 py-2.5",
                activeId === c.id ? "bg-ink/8 dark:bg-paper/8" : "hover:bg-ink/5 dark:bg-paper/5"
              )}
              onClick={() => !isEditing && onSelect(c.id)}
            >
              {isEditing ? (
                <div className="flex min-w-0 flex-1 items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
                  <input
                    autoFocus
                    value={editingTitle}
                    onChange={(e) => setEditingTitle(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") commitRename();
                      if (e.key === "Escape") cancelEditing();
                    }}
                    className="min-w-0 flex-1 rounded-sheet border border-ink/20 dark:border-ink-border bg-paper-card dark:bg-ink-card px-2 py-1 text-[13px] text-ink dark:text-paper outline-none focus-visible:border-highlighter-dark"
                  />
                  <button
                    onClick={commitRename}
                    className="shrink-0 text-sage-dark hover:text-sage"
                    aria-label="Save name"
                  >
                    <Check className="h-3.5 w-3.5" />
                  </button>
                  <button
                    onClick={cancelEditing}
                    className="shrink-0 text-ink/40 dark:text-paper/40 hover:text-ink dark:hover:text-paper"
                    aria-label="Cancel"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
              ) : (
                <>
                  <div className="min-w-0">
                    <p className="truncate text-[13px] font-medium text-ink dark:text-paper">{c.title}</p>
                    <p className="text-[11px] text-ink/40 dark:text-paper/40">{formatDate(c.updated_at)}</p>
                  </div>
                  <div className="hidden shrink-0 items-center gap-2 group-hover:flex">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        startEditing(c);
                      }}
                      className="text-ink/30 dark:text-paper/30 hover:text-ink dark:hover:text-paper"
                      aria-label="Rename conversation"
                    >
                      <Pencil className="h-3.5 w-3.5" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteConversation.mutate(c.id, {
                          onSuccess: () => {
                            if (activeId === c.id) onSelect("");
                          },
                        });
                      }}
                      disabled={deletingId === c.id}
                      className="text-ink/30 dark:text-paper/30 hover:text-danger disabled:cursor-not-allowed disabled:opacity-50"
                      aria-label="Delete conversation"
                    >
                      {deletingId === c.id ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Trash2 className="h-3.5 w-3.5" />
                      )}
                    </button>
                  </div>
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
