"use client";

import { Sidebar } from "@/components/dashboard/sidebar";
import { ThemeEffect } from "@/components/theme-effect";
import { useRequireAuth } from "@/hooks/use-require-auth";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { ready } = useRequireAuth();

  if (!ready) {
    return (
      <>
        <ThemeEffect />
        <div className="flex h-screen items-center justify-center bg-paper dark:bg-ink">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-ink/20 border-t-ink dark:border-paper/20 dark:border-t-paper" />
        </div>
      </>
    );
  }

  return (
    <>
      <ThemeEffect />
      <div className="flex h-screen overflow-hidden bg-paper dark:bg-ink">
        <Sidebar />
        <div className="flex-1 overflow-y-auto">{children}</div>
      </div>
    </>
  );
}
