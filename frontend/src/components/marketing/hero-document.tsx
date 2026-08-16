export function HeroDocument() {
  return (
    <div className="relative w-full max-w-md">
      {/* The "manuscript" card */}
      <div className="rounded-card bg-paper text-ink p-8 shadow-lift rotate-[-1.2deg]">
        <p className="font-mono text-[11px] uppercase tracking-wider text-ink/40 mb-3">
          Q3-Board-Deck.pdf &middot; p. 12
        </p>
        <p className="font-display text-[15px] leading-[1.9] text-ink/80">
          Operating margin improved for the third consecutive quarter, driven primarily by{" "}
          <span className="relative inline-block">
            <span
              className="absolute inset-x-0 bottom-0.5 h-[0.55em] bg-highlighter/70 -z-0 animate-highlight-sweep"
              aria-hidden="true"
            />
            <span className="relative">a 12% reduction in cloud infrastructure spend</span>
          </span>
          , alongside disciplined headcount growth in the second half of the year.
        </p>

        {/* Citation pin */}
        <span
          className="absolute right-6 top-[42%] inline-flex h-6 min-w-6 items-center justify-center rounded-full bg-ink px-1.5 font-mono text-[11px] font-medium text-highlighter opacity-0 animate-pin-in"
          aria-hidden="true"
        >
          1
        </span>
      </div>

      {/* Source card sliding in */}
      <div className="absolute -right-6 -bottom-8 w-64 rounded-card bg-ink-card border border-ink-border p-4 opacity-0 animate-card-slide-in shadow-lift">
        <div className="flex items-center gap-2 mb-2">
          <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-highlighter font-mono text-[10px] font-bold text-ink">
            1
          </span>
          <span className="text-[12px] font-medium text-paper/90">Q3-Board-Deck.pdf</span>
        </div>
        <p className="text-[12px] leading-relaxed text-paper/60 mb-3">
          &ldquo;...a 12% reduction in cloud infrastructure spend, achieved through the Q2
          vendor consolidation initiative...&rdquo;
        </p>
        <div className="flex items-center justify-between">
          <span className="font-mono text-[10px] text-paper/40">page 12 · chunk 4</span>
          <span className="rounded-full bg-sage/20 px-2 py-0.5 font-mono text-[10px] text-sage">
            94% match
          </span>
        </div>
      </div>
    </div>
  );
}
