"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { useLogin } from "@/hooks/use-auth";
import { isAxiosError } from "axios";

const schema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(1, "Enter your password"),
});

type FormValues = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const login = useLogin();
  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    try {
      await login.mutateAsync(values);
      router.push("/home");
    } catch (err) {
      const message = isAxiosError(err) ? err.response?.data?.detail : null;
      setError("password", { message: message ?? "Something went wrong. Try again." });
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-paper px-6">
      <div className="w-full max-w-sm">
        <Link href="/" className="mb-8 block font-display text-lg font-semibold text-ink">
          AskMyDocs AI
        </Link>
        <h1 className="mb-1 font-display text-2xl font-medium text-ink">Welcome back</h1>
        <p className="mb-8 text-sm text-ink/55">Log in to keep asking your documents questions.</p>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" autoComplete="email" {...register("email")} />
            {errors.email && <p className="mt-1 text-[12px] text-danger">{errors.email.message}</p>}
          </div>
          <div>
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" autoComplete="current-password" {...register("password")} />
            {errors.password && <p className="mt-1 text-[12px] text-danger">{errors.password.message}</p>}
          </div>
          <Button type="submit" className="w-full" disabled={login.isPending}>
            {login.isPending ? "Logging in…" : "Log in"}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-ink/55">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="font-medium text-ink hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </main>
  );
}
