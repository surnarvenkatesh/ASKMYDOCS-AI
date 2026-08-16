"use client";

import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  Briefcase,
  FileSearch,
  FileStack,
  HeartHandshake,
  Layers,
  MessageSquare,
  Scale,
  ShieldCheck,
  Sparkles,
  Users,
  Zap,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/lib/auth-store";

const QUICK_ACTIONS = [
  {
    href: "/documents",
    icon: FileStack,
    title: "Upload a document",
    description: "Add a PDF, DOCX, TXT, or Markdown file to your library.",
    accent: "highlighter",
  },
  {
    href: "/chat",
    icon: MessageSquare,
    title: "Start a conversation",
    description: "Ask a question and get a cited, streamed answer.",
    accent: "sky",
  },
  {
    href: "/analytics",
    icon: BarChart3,
    title: "View your analytics",
    description: "See usage, retrieval accuracy, and cost at a glance.",
    accent: "sage",
  },
];

const FEATURES = [
  {
    icon: FileSearch,
    title: "Hybrid retrieval",
    description: "Keyword and semantic search, fused and re-ranked before anything reaches the model.",
    accent: "highlighter",
  },
  {
    icon: ShieldCheck,
    title: "Every claim, cited",
    description: "Answers are checked against retrieved excerpts — uncited claims get flagged, not hidden.",
    accent: "sage",
  },
  {
    icon: Zap,
    title: "Streamed answers",
    description: "Responses render as they're generated, citations attached the moment they're verified.",
    accent: "sky",
  },
  {
    icon: Layers,
    title: "Any format",
    description: "PDF, DOCX, TXT, and Markdown, chunked recursively or semantically depending on content.",
    accent: "violet",
  },
];

const USE_CASES = [
  {
    icon: Scale,
    title: "Legal & Contracts",
    description: "Pull the exact clause or date from a contract, with the page number attached.",
    accent: "violet",
  },
  {
    icon: BarChart3,
    title: "Finance & Reporting",
    description: "Ask board decks and reports direct questions instead of hunting through slides.",
    accent: "sage",
  },
  {
    icon: Briefcase,
    title: "Sales & Proposals",
    description: "Search past proposals for the exact language that won a similar deal before.",
    accent: "highlighter",
  },
  {
    icon: HeartHandshake,
    title: "Customer Support",
    description: "Turn product docs into an assistant that answers with the same excerpt a human would quote.",
    accent: "sky",
  },
  {
    icon: Users,
    title: "HR & Onboarding",
    description: "Let new hires ask policy questions directly instead of paging through a handbook.",
    accent: "violet",
  },
  {
    icon: Sparkles,
    title: "Research",
    description: "Query a library of papers at once, grounded in the specific study that supports the answer.",
    accent: "sage",
  },
];

const ACCENT_STYLES: Record<string, { bg: string; text: string }> = {
  highlighter: { bg: "bg-highlighter-soft", text: "text-highlighter-dark" },
  sage: { bg: "bg-sage-soft", text: "text-sage-dark" },
  sky: { bg: "bg-sky-soft", text: "text-sky-dark" },
  violet: { bg: "bg-violet-soft", text: "text-violet-dark" },
};

export default function HomePage() {
  const user = useAuthStore((s) => s.user);
  const firstName = user?.full_name?.split(" ")[0];

  return (
    <div className="mx-auto max-w-5xl px-8 py-10">
      {/* Welcome banner */}
      <div className="relative overflow-hidden rounded-card border border-ink/10 dark:border-ink-border bg-paper-card dark:bg-ink-card p-8">
        <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-highlighter/20 blur-2xl" />
        <div className="pointer-events-none absolute -bottom-10 right-24 h-32 w-32 rounded-full bg-sky/20 blur-2xl" />
        <p className="relative mb-2 inline-flex items-center gap-1.5 rounded-full bg-violet-soft px-3 py-1 font-mono text-[11px] uppercase tracking-widest text-violet-dark">
          <Sparkles className="h-3 w-3" /> Retrieval-augmented Q&amp;A
        </p>
        <h1 className="relative font-display text-3xl font-medium text-ink dark:text-paper">
          Welcome back{firstName ? `, ${firstName}` : ""}.
        </h1>
        <p className="relative mt-2 max-w-xl text-[15px] leading-relaxed text-ink/60 dark:text-paper/60">
          AskMyDocs AI turns your documents into an assistant that answers questions with cited,
          page-accurate excerpts — never from anywhere else.
        </p>
      </div>

      {/* Quick actions */}
      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        {QUICK_ACTIONS.map((action) => {
          const accent = ACCENT_STYLES[action.accent];
          return (
            <Link key={action.href} href={action.href}>
              <Card className="h-full p-5 transition-shadow hover:shadow-lift">
                <span className={`mb-3 flex h-9 w-9 items-center justify-center rounded-full ${accent.bg}`}>
                  <action.icon className={`h-4 w-4 ${accent.text}`} />
                </span>
                <h3 className="font-display text-base font-medium text-ink dark:text-paper">{action.title}</h3>
                <p className="mt-1 text-[13px] leading-relaxed text-ink/55 dark:text-paper/55">{action.description}</p>
                <span className="mt-3 inline-flex items-center gap-1 text-[12px] font-medium text-ink/50 dark:text-paper/50">
                  Go <ArrowRight className="h-3 w-3" />
                </span>
              </Card>
            </Link>
          );
        })}
      </div>

      {/* What it does */}
      <div className="mt-14">
        <p className="mb-2 font-mono text-[12px] uppercase tracking-widest text-highlighter-dark">
          What it does
        </p>
        <h2 className="font-display text-2xl font-medium text-ink dark:text-paper">Built so answers stay grounded.</h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {FEATURES.map((feature) => {
            const accent = ACCENT_STYLES[feature.accent];
            return (
              <Card key={feature.title} className="p-5">
                <span className={`mb-3 flex h-9 w-9 items-center justify-center rounded-full ${accent.bg}`}>
                  <feature.icon className={`h-4 w-4 ${accent.text}`} />
                </span>
                <h3 className="font-display text-base font-medium text-ink dark:text-paper">{feature.title}</h3>
                <p className="mt-1 text-[13px] leading-relaxed text-ink/55 dark:text-paper/55">{feature.description}</p>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Use cases */}
      <div className="mt-14">
        <p className="mb-2 font-mono text-[12px] uppercase tracking-widest text-sky-dark">Who it's for</p>
        <h2 className="font-display text-2xl font-medium text-ink dark:text-paper">A few ways teams use it.</h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {USE_CASES.map((useCase) => {
            const accent = ACCENT_STYLES[useCase.accent];
            return (
              <Card key={useCase.title} className="p-5">
                <span className={`mb-3 flex h-9 w-9 items-center justify-center rounded-full ${accent.bg}`}>
                  <useCase.icon className={`h-4 w-4 ${accent.text}`} />
                </span>
                <h3 className="font-display text-base font-medium text-ink dark:text-paper">{useCase.title}</h3>
                <p className="mt-1 text-[13px] leading-relaxed text-ink/55 dark:text-paper/55">{useCase.description}</p>
              </Card>
            );
          })}
        </div>
      </div>

      {/* CTA */}
      <div className="mt-14 rounded-card border border-ink/10 dark:border-ink-border bg-ink px-8 py-10 text-center">
        <h2 className="font-display text-2xl font-medium text-paper">Ready to ask something?</h2>
        <p className="mx-auto mt-2 max-w-md text-[14px] text-paper/60">
          Upload a document if you haven&apos;t yet, then start a conversation to see cited answers in action.
        </p>
        <Link href="/chat" className="mt-6 inline-block">
          <Button variant="highlighter" size="lg">
            Go to Chat <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
      </div>
    </div>
  );
}
