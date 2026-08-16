"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, FileStack, Home, LogOut, MessageSquare, Settings, Shield, User as UserIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/lib/auth-store";
import { useLogout } from "@/hooks/use-auth";
import { ThemeToggle } from "@/components/theme-toggle";

const NAV_ITEMS = [
  { href: "/home", label: "Home", icon: Home },
  { href: "/chat", label: "Chat", icon: MessageSquare },
  { href: "/documents", label: "Documents", icon: FileStack },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);
  const logout = useLogout();

  const navItems = user?.is_superuser
    ? [...NAV_ITEMS, { href: "/admin", label: "Admin", icon: Shield }]
    : NAV_ITEMS;

  return (
    <aside className="flex h-screen w-60 shrink-0 flex-col border-r border-ink/8 bg-paper dark:border-ink-border dark:bg-ink">
      <div className="flex items-center justify-between px-5 py-5">
        <Link href="/home" className="font-display text-lg font-semibold text-ink dark:text-paper">
          AskMyDocs AI
        </Link>
        <ThemeToggle />
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {navItems.map((item) => {
          const active = pathname?.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2.5 rounded-card px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-ink text-paper dark:bg-paper dark:text-ink"
                  : "text-ink/65 hover:bg-ink/5 hover:text-ink dark:text-paper/65 dark:hover:bg-paper/10 dark:hover:text-paper"
              )}
            >
              <item.icon className="h-4 w-4" strokeWidth={1.75} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-ink/8 p-3 dark:border-ink-border">
        <div className="mb-2 flex items-center gap-2.5 rounded-card px-3 py-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-highlighter-soft text-highlighter-dark">
            <UserIcon className="h-3.5 w-3.5" />
          </span>
          <div className="min-w-0">
            <p className="truncate text-[13px] font-medium text-ink dark:text-paper">{user?.full_name ?? "…"}</p>
            <p className="truncate text-[11px] text-ink/45 dark:text-paper/45">{user?.email ?? ""}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="flex w-full items-center gap-2.5 rounded-card px-3 py-2 text-sm text-ink/55 hover:bg-ink/5 hover:text-ink dark:text-paper/55 dark:hover:bg-paper/10 dark:hover:text-paper"
        >
          <LogOut className="h-4 w-4" strokeWidth={1.75} />
          Log out
        </button>
      </div>
    </aside>
  );
}
