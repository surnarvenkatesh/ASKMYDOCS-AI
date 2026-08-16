export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 py-1" role="status" aria-label="Generating answer">
      <span
        className="h-2 w-2 animate-bounce rounded-full bg-ink/40 dark:bg-paper/40"
        style={{ animationDelay: "0ms", animationDuration: "1s" }}
      />
      <span
        className="h-2 w-2 animate-bounce rounded-full bg-ink/40 dark:bg-paper/40"
        style={{ animationDelay: "150ms", animationDuration: "1s" }}
      />
      <span
        className="h-2 w-2 animate-bounce rounded-full bg-ink/40 dark:bg-paper/40"
        style={{ animationDelay: "300ms", animationDuration: "1s" }}
      />
    </div>
  );
}
