"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuthStore } from "@/lib/auth-store";

/**
 * Guards a client component tree behind authentication. Returns `ready`
 * so callers can avoid a flash of protected content before the redirect
 * fires (auth state is persisted via zustand/localStorage and only
 * available after hydration on the client).
 */
export function useRequireAuth() {
  const router = useRouter();
  const accessToken = useAuthStore((s) => s.accessToken);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated && !accessToken) {
      router.replace("/login");
    }
  }, [hydrated, accessToken, router]);

  return { ready: hydrated && Boolean(accessToken) };
}
