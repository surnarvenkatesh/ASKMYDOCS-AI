"use client";

import { isAxiosError } from "axios";
import { ShieldOff } from "lucide-react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Badge, Card } from "@/components/ui/card";
import { useAllUsers, usePlatformStats } from "@/hooks/use-admin";
import { formatDate } from "@/lib/utils";

export default function AdminPage() {
  const { data: stats, isLoading, error } = usePlatformStats(30);
  const { data: usersData } = useAllUsers();

  if (isAxiosError(error) && error.response?.status === 403) {
    return (
      <div className="flex h-full flex-col items-center justify-center text-center">
        <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-danger-soft">
          <ShieldOff className="h-5 w-5 text-danger" />
        </span>
        <p className="font-display text-lg text-ink dark:text-paper">Admins only</p>
        <p className="mt-1 max-w-sm text-sm text-ink/50 dark:text-paper/50">
          Your account doesn&apos;t have admin access. Ask an existing admin to grant it, or run the
          <code className="mx-1 rounded bg-ink/5 dark:bg-paper/5 px-1.5 py-0.5 font-mono text-[12px]">make_superuser</code>
          script on the server.
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-8 py-10">
      <h1 className="font-display text-2xl font-medium text-ink dark:text-paper">Admin</h1>
      <p className="mt-1 text-sm text-ink/55 dark:text-paper/55">Platform-wide usage across every account.</p>

      {isLoading ? (
        <p className="mt-8 text-sm text-ink/40 dark:text-paper/40">Loading…</p>
      ) : stats ? (
        <>
          <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
            <StatCard label="Total users" value={stats.total_users.toString()} />
            <StatCard label="Active (30d)" value={stats.active_users.toString()} />
            <StatCard label="Documents" value={stats.total_documents.toString()} />
            <StatCard label="Indexed chunks" value={stats.total_embeddings.toLocaleString()} />
            <StatCard label="Conversations" value={stats.total_conversations.toString()} />
            <StatCard label="Total queries" value={stats.total_queries.toString()} />
          </div>

          <Card className="mt-8 p-6">
            <h2 className="mb-4 font-display text-lg font-medium text-ink dark:text-paper">Daily signups</h2>
            {stats.daily_signups.length === 0 ? (
              <p className="text-sm text-ink/40 dark:text-paper/40">No signups in this period yet.</p>
            ) : (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats.daily_signups}>
                    <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#0E1520AA" }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 11, fill: "#0E1520AA" }} axisLine={false} tickLine={false} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#6FA287" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </Card>

          <Card className="mt-8 overflow-hidden">
            <div className="border-b border-ink/8 dark:border-ink-border p-4">
              <h2 className="font-display text-lg font-medium text-ink dark:text-paper">All users</h2>
            </div>
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-ink/10 dark:border-ink-border bg-ink/[0.03] dark:bg-paper/[0.03] text-[12px] uppercase tracking-wide text-ink/45 dark:text-paper/45">
                  <th className="px-4 py-3 font-medium">Name</th>
                  <th className="px-4 py-3 font-medium">Email</th>
                  <th className="px-4 py-3 font-medium">Role</th>
                  <th className="px-4 py-3 font-medium">Joined</th>
                </tr>
              </thead>
              <tbody>
                {usersData?.users.map((u) => (
                  <tr key={u.id} className="border-b border-ink/6 dark:border-ink-border last:border-0">
                    <td className="px-4 py-3 font-medium text-ink dark:text-paper">{u.full_name}</td>
                    <td className="px-4 py-3 text-ink/60 dark:text-paper/60">{u.email}</td>
                    <td className="px-4 py-3">
                      {u.is_superuser ? <Badge variant="highlighter">Admin</Badge> : <Badge>Member</Badge>}
                    </td>
                    <td className="px-4 py-3 text-ink/60 dark:text-paper/60">{formatDate(u.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </>
      ) : null}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <Card className="p-4">
      <p className="text-[12px] text-ink/45 dark:text-paper/45">{label}</p>
      <p className="mt-1 font-display text-2xl font-medium text-ink dark:text-paper">{value}</p>
    </Card>
  );
}
