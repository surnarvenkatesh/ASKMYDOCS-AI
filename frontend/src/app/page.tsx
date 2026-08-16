import Link from "next/link";
import { ArrowRight, FileSearch, ShieldCheck, Zap, BarChart3, Layers, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { HeroDocument } from "@/components/marketing/hero-document";

const FEATURES = [
  {
    icon: FileSearch,
    title: "Hybrid retrieval",
    description:
      "Keyword search and semantic search run side by side, fused with reciprocal rank fusion and re-ranked by a cross-encoder before anything reaches the model.",
  },
  {
    icon: ShieldCheck,
    title: "Every claim, cited",
    description:
      "Answers are checked against the retrieved excerpts. Claims without a traceable source are flagged instead of quietly presented as fact.",
  },
  {
    icon: Zap,
    title: "Streamed answers",
    description: "Responses render token by token, with citations attached as soon as they're verified.",
  },
  {
    icon: Layers,
    title: "Any document, any format",
    description: "PDF, DOCX, TXT, and Markdown, chunked recursively or semantically depending on content.",
  },
  {
    icon: BarChart3,
    title: "Retrieval you can audit",
    description: "Track faithfulness, context recall, latency, and cost per query from one dashboard.",
  },
  {
    icon: Users,
    title: "Built for teams",
    description: "Shared document libraries, per-user access, and versioned re-indexing when files change.",
  },
];

const STATS = [
  { value: "94%", label: "avg. citation confidence" },
  { value: "<2s", label: "median first-token latency" },
  { value: "4", label: "file formats supported" },
];

const TESTIMONIALS = [
  {
    quote:
      "We stopped losing afternoons to searching through contract PDFs. Every answer points back to the exact clause.",
    name: "Head of Legal Ops",
    company: "Mid-market SaaS company",
  },
  {
    quote:
      "The confidence scores changed how our analysts trust the tool — low-confidence answers get a second look, high-confidence ones don't.",
    name: "Data Platform Lead",
    company: "Financial services firm",
  },
];

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-paper text-ink">
      <Nav />
      <Hero />
      <Stats />
      <Features />
      <Testimonials />
      <Footer />
    </main>
  );
}

function Nav() {
  return (
    <header className="border-b border-ink/8">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <span className="font-display text-lg font-semibold">AskMyDocs AI</span>
        <nav className="hidden items-center gap-8 text-sm text-ink/70 md:flex">
          <a href="#features" className="hover:text-ink">Features</a>
          <Link href="/login" className="hover:text-ink">Log in</Link>
        </nav>
        <Link href="/register">
          <Button size="sm">Start free</Button>
        </Link>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="bg-ink text-paper">
      <div className="mx-auto grid max-w-6xl items-center gap-16 px-6 py-24 md:grid-cols-2 md:py-32">
        <div>
          <p className="mb-5 font-mono text-[12px] uppercase tracking-widest text-highlighter">
            Retrieval-augmented, citation-first
          </p>
          <h1 className="font-display text-[2.75rem] font-medium leading-[1.1] tracking-tight md:text-[3.5rem]">
            Ask your documents.
            <br />
            Get <em className="italic text-highlighter">cited</em> answers.
          </h1>
          <p className="mt-6 max-w-md text-[17px] leading-relaxed text-paper/65">
            Upload your PDFs, contracts, and reports. AskMyDocs AI finds the exact passage,
            shows its confidence, and never answers from anywhere else.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-4">
            <Link href="/register">
              <Button variant="highlighter" size="lg">
                Start free <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <a href="#features" className="text-sm text-paper/60 hover:text-paper">
              See how retrieval works &rarr;
            </a>
          </div>
        </div>
        <div className="flex justify-center md:justify-end">
          <HeroDocument />
        </div>
      </div>
    </section>
  );
}

function Stats() {
  return (
    <section className="border-b border-ink/8 bg-paper">
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-8 px-6 py-14 sm:grid-cols-3">
        {STATS.map((stat) => (
          <div key={stat.label} className="text-center sm:text-left">
            <div className="font-display text-4xl font-medium">{stat.value}</div>
            <div className="mt-1 text-sm text-ink/55">{stat.label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function Features() {
  return (
    <section id="features" className="mx-auto max-w-6xl px-6 py-24">
      <div className="mb-14 max-w-xl">
        <p className="mb-3 font-mono text-[12px] uppercase tracking-widest text-highlighter-dark">
          The pipeline
        </p>
        <h2 className="font-display text-3xl font-medium leading-tight md:text-4xl">
          Built so the model can&apos;t wander off the page.
        </h2>
      </div>
      <div className="grid gap-px overflow-hidden rounded-card border border-ink/10 bg-ink/10 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((feature) => (
          <div key={feature.title} className="bg-paper p-7">
            <feature.icon className="mb-4 h-5 w-5 text-highlighter-dark" strokeWidth={1.75} />
            <h3 className="mb-2 font-display text-lg font-medium">{feature.title}</h3>
            <p className="text-sm leading-relaxed text-ink/60">{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function Testimonials() {
  return (
    <section className="bg-ink-card">
      <div className="mx-auto max-w-6xl px-6 py-24">
        <div className="grid gap-10 md:grid-cols-2">
          {TESTIMONIALS.map((t) => (
            <div key={t.name} className="rounded-card border border-ink-border p-8">
              <p className="font-display text-xl italic leading-relaxed text-paper/90">
                &ldquo;{t.quote}&rdquo;
              </p>
              <p className="mt-6 text-sm text-paper/50">
                {t.name} &middot; {t.company}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-ink/8">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-10 text-sm text-ink/50 sm:flex-row">
        <span>&copy; {new Date().getFullYear()} AskMyDocs AI</span>
        <div className="flex gap-6">
          <a href="#" className="hover:text-ink">Privacy</a>
          <a href="#" className="hover:text-ink">Terms</a>
          <a href="#" className="hover:text-ink">Contact</a>
        </div>
      </div>
    </footer>
  );
}
