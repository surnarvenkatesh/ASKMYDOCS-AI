import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { useAuthStore } from "@/lib/auth-store";
import type { TokenResponse, User } from "@/types/api";

interface RegisterInput {
  email: string;
  full_name: string;
  password: string;
}

interface LoginInput {
  email: string;
  password: string;
}

export function useRegister() {
  return useMutation({
    mutationFn: async (input: RegisterInput) => {
      const { data } = await apiClient.post<User>("/auth/register", input);
      return data;
    },
  });
}

export function useLogin() {
  const setTokens = useAuthStore((s) => s.setTokens);
  const setUser = useAuthStore((s) => s.setUser);

  return useMutation({
    mutationFn: async (input: LoginInput) => {
      const { data } = await apiClient.post<TokenResponse>("/auth/login", input);
      setTokens(data.access_token, data.refresh_token);
      const me = await apiClient.get<User>("/auth/me");
      setUser(me.data);
      return me.data;
    },
  });
}

export function useCurrentUser() {
  const accessToken = useAuthStore((s) => s.accessToken);
  return useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const { data } = await apiClient.get<User>("/auth/me");
      return data;
    },
    enabled: Boolean(accessToken),
  });
}

export function useLogout() {
  const logout = useAuthStore((s) => s.logout);
  const queryClient = useQueryClient();
  return () => {
    logout();
    queryClient.clear();
  };
}
