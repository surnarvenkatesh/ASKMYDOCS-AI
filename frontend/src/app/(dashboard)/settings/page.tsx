"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { apiClient } from "@/lib/api-client";
import { useAuthStore } from "@/lib/auth-store";
import { useCurrentUser } from "@/hooks/use-auth";

const schema = z.object({
  full_name: z.string().min(1, "Enter your name"),
  password: z.string().min(8, "Password must be at least 8 characters").optional().or(z.literal("")),
});

type FormValues = z.infer<typeof schema>;

export default function SettingsPage() {
  const { data: user } = useCurrentUser();
  const setUser = useAuthStore((s) => s.setUser);
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
    reset,
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    values: { full_name: user?.full_name ?? "", password: "" },
  });

  const updateProfile = useMutation({
    mutationFn: async (values: FormValues) => {
      const payload: Record<string, string> = { full_name: values.full_name };
      if (values.password) payload.password = values.password;
      const { data } = await apiClient.patch("/users/me", payload);
      return data;
    },
    onSuccess: (data) => {
      setUser(data);
      queryClient.invalidateQueries({ queryKey: ["me"] });
      reset({ full_name: data.full_name, password: "" });
    },
  });

  return (
    <div className="mx-auto max-w-xl px-8 py-10">
      <h1 className="font-display text-2xl font-medium text-ink dark:text-paper">Settings</h1>
      <p className="mt-1 text-sm text-ink/55 dark:text-paper/55">Manage your profile details.</p>

      <form
        onSubmit={handleSubmit((values) => updateProfile.mutate(values))}
        className="mt-8 space-y-5 rounded-card border border-ink/10 dark:border-ink-border bg-paper-card dark:bg-ink-card p-6"
      >
        <div>
          <Label htmlFor="email">Email</Label>
          <Input id="email" value={user?.email ?? ""} disabled />
        </div>
        <div>
          <Label htmlFor="full_name">Full name</Label>
          <Input id="full_name" {...register("full_name")} />
          {errors.full_name && <p className="mt-1 text-[12px] text-danger">{errors.full_name.message}</p>}
        </div>
        <div>
          <Label htmlFor="password">New password</Label>
          <Input id="password" type="password" placeholder="Leave blank to keep current password" {...register("password")} />
          {errors.password && <p className="mt-1 text-[12px] text-danger">{errors.password.message}</p>}
        </div>
        <div className="flex items-center gap-3">
          <Button type="submit" disabled={!isDirty || updateProfile.isPending}>
            {updateProfile.isPending ? "Saving…" : "Save changes"}
          </Button>
          {updateProfile.isSuccess && <span className="text-[13px] text-sage-dark">Saved</span>}
        </div>
      </form>
    </div>
  );
}
