"use client";
import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { Search, Trash2 } from "lucide-react";

import { api } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { useAuthStore } from "@/store/authStore";

interface User {
  id: number;
  email: string;
  full_name: string;
  role: "user" | "admin";
  created_at: string;
}

interface Page {
  items: User[];
  total: number;
  page: number;
  page_size: number;
}

export default function AdminUsersPage() {
  const me = useAuthStore((s) => s.user);
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const qc = useQueryClient();

  const users = useQuery<Page>({
    queryKey: ["admin-users", q, page],
    queryFn: async () => (await api.get("/api/admin/users", {
      params: { q: q || undefined, page, page_size: 20 },
    })).data,
  });

  const refresh = () => qc.invalidateQueries({ queryKey: ["admin-users"] });

  const toggleRole = async (u: User) => {
    if (u.id === me?.id) {
      toast.error("You cannot demote yourself.");
      return;
    }
    const next = u.role === "admin" ? "user" : "admin";
    try {
      await api.patch(`/api/admin/users/${u.id}/role`, { role: next });
      toast.success(`${u.email} is now ${next}.`);
      refresh();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Update failed");
    }
  };

  const deleteUser = async (u: User) => {
    if (u.id === me?.id) return;
    if (!confirm(`Delete ${u.email}? This cascades to their sessions and resumes.`)) return;
    try {
      await api.delete(`/api/admin/users/${u.id}`);
      toast.success(`Deleted ${u.email}`);
      refresh();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Delete failed");
    }
  };

  const totalPages = users.data ? Math.max(1, Math.ceil(users.data.total / users.data.page_size)) : 1;

  return (
    <div className="p-6 lg:p-10 max-w-6xl mx-auto">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">Users</h1>
        <p className="text-slate-500 text-sm mt-1">
          {users.data?.total ?? "—"} total · search by email or name
        </p>
      </header>

      <div className="flex items-center gap-2 mb-4">
        <div className="relative flex-1 max-w-sm">
          <Search size={14} className="absolute left-3 top-3 text-slate-400" />
          <Input
            value={q}
            onChange={(e) => { setQ(e.target.value); setPage(1); }}
            placeholder="Search…"
            className="pl-8"
          />
        </div>
      </div>

      <Card className="p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
            <tr>
              <th className="p-3">User</th>
              <th className="p-3">Role</th>
              <th className="p-3">Joined</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.isLoading ? (
              <tr><td className="p-6 text-center text-slate-400" colSpan={4}>Loading…</td></tr>
            ) : (users.data?.items.length ?? 0) === 0 ? (
              <tr><td className="p-6 text-center text-slate-400" colSpan={4}>No users match your search.</td></tr>
            ) : users.data!.items.map((u) => (
              <tr key={u.id} className="border-t border-slate-100">
                <td className="p-3">
                  <p className="font-medium">{u.full_name}</p>
                  <p className="text-xs text-slate-500">{u.email}</p>
                </td>
                <td className="p-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    u.role === "admin"
                      ? "bg-amber-50 text-amber-700"
                      : "bg-slate-100 text-slate-600"
                  }`}>
                    {u.role}
                  </span>
                </td>
                <td className="p-3 text-slate-500">
                  {new Date(u.created_at).toLocaleDateString()}
                </td>
                <td className="p-3 text-right">
                  <Button variant="outline" size="sm" onClick={() => toggleRole(u)}
                          disabled={u.id === me?.id}>
                    {u.role === "admin" ? "Demote" : "Promote"}
                  </Button>
                  <button
                    onClick={() => deleteUser(u)}
                    disabled={u.id === me?.id}
                    className="ml-2 p-2 rounded-lg text-red-500 hover:bg-red-50 disabled:opacity-30 disabled:cursor-not-allowed"
                    title="Delete user"
                  >
                    <Trash2 size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 text-sm">
          <span className="text-slate-500">Page {page} of {totalPages}</span>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>← Prev</Button>
            <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next →</Button>
          </div>
        </div>
      )}
    </div>
  );
}
