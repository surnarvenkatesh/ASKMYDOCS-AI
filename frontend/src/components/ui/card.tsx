import { cn } from "@/lib/utils";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-card border border-ink/10 bg-paper-card shadow-paper dark:border-ink-border dark:bg-ink-card",
        className
      )}
      {...props}
    />
  );
}

export function Badge({
  className,
  variant = "neutral",
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { variant?: "neutral" | "sage" | "highlighter" | "danger" }) {
  const variants = {
    neutral: "bg-ink/5 text-ink/70 dark:bg-paper/10 dark:text-paper/70",
    sage: "bg-sage-soft text-sage-dark dark:bg-sage/20 dark:text-sage",
    highlighter: "bg-highlighter-soft text-highlighter-dark dark:bg-highlighter/20 dark:text-highlighter",
    danger: "bg-danger-soft text-danger dark:bg-danger/20 dark:text-danger",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium",
        variants[variant],
        className
      )}
      {...props}
    />
  );
}

export function ConfidenceBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const variant = pct >= 70 ? "sage" : pct >= 40 ? "highlighter" : "danger";
  return (
    <Badge variant={variant} className="font-mono">
      {pct}% match
    </Badge>
  );
}
