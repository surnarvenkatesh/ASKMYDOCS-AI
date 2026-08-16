"use client";

import { useRef, useState } from "react";
import { Check, Download, Pencil, RefreshCw, Trash2, Upload, X } from "lucide-react";
import { Badge } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  useDeleteDocument,
  useDocuments,
  useReindexDocument,
  useRenameDocument,
  useUploadDocument,
} from "@/hooks/use-documents";
import { formatBytes, formatDate } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/api-client";
import { useAuthStore } from "@/lib/auth-store";
import type { DocumentStatus } from "@/types/api";

const STATUS_VARIANT: Record<DocumentStatus, "neutral" | "sage" | "highlighter" | "danger"> = {
  pending: "neutral",
  processing: "highlighter",
  indexed: "sage",
  failed: "danger",
};

export default function DocumentsPage() {
  const [search, setSearch] = useState("");
  const { data, isLoading } = useDocuments(search || undefined);
  const upload = useUploadDocument();
  const deleteDocument = useDeleteDocument();
  const reindex = useReindexDocument();
  const renameDocument = useRenameDocument();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState("");

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    Array.from(files).forEach((file) => upload.mutate(file));
  };

  const startEditing = (id: string, currentName: string) => {
    setEditingId(id);
    setEditingName(currentName);
  };

  const commitRename = () => {
    const trimmed = editingName.trim();
    if (editingId && trimmed) {
      renameDocument.mutate({ documentId: editingId, filename: trimmed });
    }
    setEditingId(null);
  };

  const cancelEditing = () => setEditingId(null);

  return (
    <div className="mx-auto max-w-5xl px-8 py-10">
      <h1 className="font-display text-2xl font-medium text-ink dark:text-paper">Documents</h1>
      <p className="mt-1 text-sm text-ink/55 dark:text-paper/55">
        Upload PDFs, DOCX, TXT, or Markdown files. They're chunked and indexed automatically.
      </p>

      {/* Upload center */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragActive(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => fileInputRef.current?.click()}
        className={`mt-6 flex cursor-pointer flex-col items-center justify-center rounded-card border-2 border-dashed px-6 py-12 text-center transition-colors ${
          dragActive ? "border-highlighter-dark bg-highlighter-soft/40" : "border-ink/15 dark:border-ink-border hover:border-ink/25 dark:hover:border-ink-border"
        }`}
      >
        <Upload className="mb-3 h-6 w-6 text-ink/40 dark:text-paper/40" />
        <p className="text-sm text-ink/70 dark:text-paper/70">
          <span className="font-medium text-ink dark:text-paper">Click to upload</span> or drag and drop
        </p>
        <p className="mt-1 text-[12px] text-ink/40 dark:text-paper/40">PDF, DOCX, TXT, or Markdown — up to 25MB</p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.md,.markdown"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      {/* Search */}
      <div className="mt-8 flex items-center justify-between">
        <Input
          placeholder="Search documents…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
        <p className="text-sm text-ink/45 dark:text-paper/45">{data?.total ?? 0} documents</p>
      </div>

      {/* Library table */}
      <div className="mt-4 overflow-hidden rounded-card border border-ink/10 dark:border-ink-border">
        <table className="w-full table-fixed text-left text-sm">
          <thead>
            <tr className="border-b border-ink/10 dark:border-ink-border bg-ink/[0.03] dark:bg-paper/[0.03] text-[12px] uppercase tracking-wide text-ink/45 dark:text-paper/45">
              <th className="px-4 py-3 font-medium">Filename</th>
              <th className="w-28 px-4 py-3 font-medium">Status</th>
              <th className="w-24 px-4 py-3 font-medium">Size</th>
              <th className="w-32 px-4 py-3 font-medium">Uploaded</th>
              <th className="w-[180px] px-4 py-3 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-ink/40 dark:text-paper/40">
                  Loading…
                </td>
              </tr>
            )}
            {data?.documents.length === 0 && !isLoading && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-ink/40 dark:text-paper/40">
                  No documents yet — upload your first one above.
                </td>
              </tr>
            )}
            {data?.documents.map((doc) => {
              const isEditing = editingId === doc.id;
              return (
                <tr key={doc.id} className="border-b border-ink/6 dark:border-ink-border last:border-0">
                  <td className="max-w-0 px-4 py-3 font-medium text-ink dark:text-paper">
                    {isEditing ? (
                      <div className="flex items-center gap-1.5">
                        <input
                          autoFocus
                          value={editingName}
                          onChange={(e) => setEditingName(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") commitRename();
                            if (e.key === "Escape") cancelEditing();
                          }}
                          className="min-w-0 flex-1 rounded-sheet border border-ink/20 dark:border-ink-border bg-paper-card dark:bg-ink-card px-2 py-1 text-sm text-ink dark:text-paper outline-none focus-visible:border-highlighter-dark"
                        />
                        <button
                          onClick={commitRename}
                          className="shrink-0 text-sage-dark hover:text-sage"
                          aria-label="Save name"
                        >
                          <Check className="h-4 w-4" />
                        </button>
                        <button
                          onClick={cancelEditing}
                          className="shrink-0 text-ink/40 dark:text-paper/40 hover:text-ink dark:hover:text-paper"
                          aria-label="Cancel"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ) : (
                      <span className="block truncate" title={doc.filename}>
                        {doc.filename}
                      </span>
                    )}
                  </td>
                  <td className="min-w-0 max-w-0 px-4 py-3">
                    <Badge variant={STATUS_VARIANT[doc.status]}>{doc.status}</Badge>
                  </td>
                  <td className="px-4 py-3 text-ink/60 dark:text-paper/60">{formatBytes(doc.file_size_bytes)}</td>
                  <td className="px-4 py-3 text-ink/60 dark:text-paper/60">{formatDate(doc.created_at)}</td>
                  <td className="w-[180px] shrink-0 whitespace-nowrap px-4 py-3">
                    <div className="flex justify-end gap-1">
                      <DownloadButton documentId={doc.id} />
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => startEditing(doc.id, doc.filename)}
                        aria-label="Rename document"
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => reindex.mutate(doc.id)}
                        aria-label="Re-index document"
                      >
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => deleteDocument.mutate(doc.id)}
                        aria-label="Delete document"
                      >
                        <Trash2 className="h-4 w-4 text-danger" />
                      </Button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function DownloadButton({ documentId }: { documentId: string }) {
  const token = useAuthStore((s) => s.accessToken);
  const href = `${API_BASE_URL}/documents/${documentId}/download`;

  const handleClick = async () => {
    const response = await fetch(href, { headers: { Authorization: `Bearer ${token}` } });
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "";
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <Button variant="ghost" size="icon" onClick={handleClick} aria-label="Download document">
      <Download className="h-4 w-4" />
    </Button>
  );
}
