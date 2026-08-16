import { forwardRef } from "react";
import { cn } from "@/lib/utils";

export const Input = forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "flex h-10 w-full rounded-card border border-ink/15 bg-paper-card px-3 text-sm text-ink placeholder:text-ink/40 focus-visible:border-highlighter-dark disabled:cursor-not-allowed disabled:opacity-50 dark:border-ink-border dark:bg-ink-card dark:text-paper dark:placeholder:text-paper/40",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";

export const Textarea = forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(
        "flex min-h-[44px] w-full resize-none rounded-card border border-ink/15 bg-paper-card px-3 py-2.5 text-sm text-ink placeholder:text-ink/40 focus-visible:border-highlighter-dark disabled:cursor-not-allowed disabled:opacity-50 dark:border-ink-border dark:bg-ink-card dark:text-paper dark:placeholder:text-paper/40",
        className
      )}
      {...props}
    />
  )
);
Textarea.displayName = "Textarea";

export function Label({ className, ...props }: React.LabelHTMLAttributes<HTMLLabelElement>) {
  return <label className={cn("text-[13px] font-medium text-ink/70 mb-1.5 block dark:text-paper/70", className)} {...props} />;
}
