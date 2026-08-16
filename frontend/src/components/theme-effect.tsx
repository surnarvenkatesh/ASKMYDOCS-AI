"use client";

import { useEffect } from "react";
import { useThemeStore } from "@/lib/theme-store";

/**
 * Applies the `dark` class on <html> while mounted, and removes it on
 * unmount. Deliberately mounted only inside the dashboard layout (not
 * the root layout) so dark mode never leaks onto the public landing
 * page or the login/register screens, which aren't styled for it.
 */
export function ThemeEffect() {
  const theme = useThemeStore((s) => s.theme);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    return () => {
      document.documentElement.classList.remove("dark");
    };
  }, [theme]);

  return null;
}
