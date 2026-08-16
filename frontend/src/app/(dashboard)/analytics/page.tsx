"use client";

import { useState } from "react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import {
  BarChart3,
  CheckCircle2,
  Clock,
  Coins,
  FileStack,
  Gauge,
  Layers,
  MessageSquare,
  type LucideIcon,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { useAnalyticsSummary } from "@/hooks/use-analytics";

const RANGE_OPTIONS = [
  { label: "7d", value: 7 },
  { label: "14d", value: 14 },
  { label: "30d", value: 30 },
  { label: "90d", value: 90 },
];

const ACCENT_STYLES: Record<string, { bg: string; text: string }> = {
  highlighter: {
    bg: "bg-highlighter-soft dark:bg-highlighter/20",
    text: "text-highlighter-dark dark:text-highlighter",
  },
  sage: { bg: "bg-sage-soft dark:bg-sage/20", text: "text-sage-dark dark:text-sage" },
  sky: { bg: "bg-sky-soft dark:bg-sky/20", text: "text-sky-dark dark:text-sky" },
  violet: { bg: "bg-violet-soft dark:bg-violet/20", text: "text-violet-dark dark:text-violet" },
};

interface StatItem {
  label: string;
  value: string;
  icon: LucideIcon;
  accent: keyof typeof ACCENT_STYLES;
}

export default function AnalyticsPage() {
  const [days, setDays] = useState(14);
  const { data, isLoading } = useAnalyticsSummary(days);

  const usageStats: StatItem[] = data
    ? [
        { label: "Documents", value: data.documents_count.toString(), icon: FileStack, accent: "highlighter" },
        { label: "Indexed chunks", value: data.embeddings_count.toLocaleString(), icon: Layers, accent: "violet" },
        { label: `Queries (${days}d)`, value: data.total_queries.toString(), icon: MessageSquare, accent: "sky" },
        {
          label: "Tokens used",
          value: (data.token_usage.prompt_tokens + data.token_usage.completion_tokens).toLocaleString(),
          icon: Coins,
          accent: "sage",
        },
      ]
    : [];

  const performanceStats: StatItem[] = data
    ? [
        {
          label: "Avg. response time",
          value: data.avg_response_time_ms ? `${Math.round(data.avg_response_time_ms)}ms` : "—",
          icon: Clock,
          accent: "sky",
        },
        {
          label: "Avg. retrieval time",
          value: data.avg_retrieval_time_ms ? `${Math.round(data.avg_retrieval_time_ms)}ms` : "—",
          icon: Gauge,
          accent: "violet",
        },
        {
          label: "Retrieval accuracy",
          value: data.retrieval_accuracy !== null ? `${Math.round(data.retrieval_accuracy * 100)}%` : "—",
          icon: CheckCircle2,
          accent: "sage",
        },
      ]
    : [];

  return (
    <div className="mx-auto max-w-5xl px-8 py-10">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-medium text-ink dark:text-paper">Analytics</h1>
          <p className="mt-1 text-sm text-ink/55 dark:text-paper/55">
            Usage and retrieval quality for your account.
          </p>
        </div>
        <div className="flex gap-1 rounded-card border border-ink/10 p-1 dark:border-ink-border">
          {RANGE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setDays(opt.value)}
              className={`rounded-sheet px-3 py-1.5 text-[13px] transition-colors ${
                days === opt.value
                  ? "bg-ink text-paper dark:bg-paper dark:text-ink"
                  : "text-ink/55 hover:bg-ink/5 dark:text-paper/55 dark:hover:bg-paper/10"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <p className="mt-8 text-sm text-ink/40 dark:text-paper/40">Loading…</p>
      ) : data ? (
        <>
          <SectionLabel>Usage</SectionLabel>
          <div className="mt-3 grid grid-cols-2 gap-4 md:grid-cols-4">
            {usageStats.map((s) => (
              <StatCard key={s.label} {...s} />
            ))}
          </div>

          <SectionLabel className="mt-10">Performance &amp; quality</SectionLabel>
          <div className="mt-3 grid grid-cols-2 gap-4 md:grid-cols-3">
            {performanceStats.map((s) => (
              <StatCard key={s.label} {...s} />
            ))}
          </div>

          <Card className="mt-10 p-6">
            <h2 className="mb-4 flex items-center gap-2 font-display text-lg font-medium text-ink dark:text-paper">
              <BarChart3 className="h-4 w-4 text-highlighter-dark dark:text-highlighter" />
              Daily queries
            </h2>
            {data.daily_queries.length === 0 ? (
              <p className="text-sm text-ink/40 dark:text-paper/40">No queries in this period yet.</p>
            ) : (
              <div className="h-64 text-ink/45 dark:text-paper/45">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.daily_queries}>
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 11, fill: "currentColor" }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 11, fill: "currentColor" }}
                      axisLine={false}
                      tickLine={false}
                      allowDecimals={false}
                    />
                    <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid rgba(14,21,32,0.1)", fontSize: 13 }} />
                    <Bar dataKey="count" fill="#F5B942" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </Card>
        </>
      ) : null}
    </div>
  );
}

function SectionLabel({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <p className={`font-mono text-[11px] uppercase tracking-widest text-ink/40 dark:text-paper/40 ${className}`}>
      {children}
    </p>
  );
}

function StatCard({ label, value, icon: Icon, accent }: StatItem) {
  const styles = ACCENT_STYLES[accent];
  return (
    <Card className="p-4">
      <span className={`mb-2 flex h-8 w-8 items-center justify-center rounded-full ${styles.bg}`}>
        <Icon className={`h-4 w-4 ${styles.text}`} />
      </span>
      <p className="text-[12px] text-ink/45 dark:text-paper/45">{label}</p>
      <p className="mt-0.5 font-display text-2xl font-medium text-ink dark:text-paper">{value}</p>
    </Card>
  );
}
