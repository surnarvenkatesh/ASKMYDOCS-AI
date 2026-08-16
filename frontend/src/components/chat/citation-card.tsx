import { FileText } from "lucide-react";
import { ConfidenceBadge } from "@/components/ui/card";
import type { Citation } from "@/types/api";

export function CitationCard({ citation }: { citation: Citation }) {
  return (
    <div className="w-64 shrink-0 rounded-card border border-ink/10 dark:border-ink-border bg-paper-card dark:bg-ink-card p-3.5">
      <div className="mb-2 flex items-center gap-2">
        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-highlighter font-mono text-[10px] font-bold text-ink dark:text-paper">
          {citation.ref_id}
        </span>
        <FileText className="h-3.5 w-3.5 text-ink/40 dark:text-paper/40" />
        <span className="truncate text-[12px] font-medium text-ink/80 dark:text-paper/80">{citation.document_filename}</span>
      </div>
      <p className="mb-3 line-clamp-3 text-[12px] leading-relaxed text-ink/55 dark:text-paper/55">{citation.snippet}</p>
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] text-ink/40 dark:text-paper/40">
          {citation.page_number ? `page ${citation.page_number}` : "no page ref"}
        </span>
        <ConfidenceBadge score={citation.confidence_score} />
      </div>
    </div>
  );
}
