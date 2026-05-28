"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import {
  ShieldCheck,
  Users,
  ListTodo,
  Activity,
  LayoutDashboard,
  ArrowLeft,
} from "lucide-react";

import { useAuthStore } from "@/store/authStore";
import { cn } from "@/lib/utils";

const adminLinks = [
  { href: "/admin",            label: "Overview",      icon: LayoutDashboard },
  { href: "/admin/users",      label: "Users",         icon: Users },
  { href: "/admin/questions",  label: "Question bank", icon: ListTodo },
  { href: "/admin/sessions",   label: "Activity",      icon: Activity },
];

export function AdminShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, token } = useAuthStore();

  // Client-side guards: must be logged in AND admin.
  useEffect(() => {
    if (!token) {
      router.replace("/login");
      return;
    }
    if (user && user.role !== "admin") {
      router.replace("/dashboard");
    }
  }, [token, user, router]);

  if (!token || !user || user.role !== "admin") {
    return (
      <div className="min-h-screen flex items-center justify-center text-slate-500">
        Verifying admin access…
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="grid lg:grid-cols-[260px_1fr]">
        <aside className="hidden lg:flex flex-col bg-white border-r border-slate-100 min-h-screen">
          <div className="p-6">
            <Link href="/dashboard" className="text-xs text-slate-500 hover:text-slate-800 inline-flex items-center gap-1 mb-3">
              <ArrowLeft size={12} /> Back to user dashboard
            </Link>
            <div className="flex items-center gap-2 font-semibold">
              <span className="inline-flex w-8 h-8 rounded-lg bg-amber-500 text-white items-center justify-center">
                <ShieldCheck size={16} />
              </span>
              <span>Admin</span>
            </div>
          </div>

          <nav className="flex-1 px-4 space-y-1">
            {adminLinks.map((l) => {
              const active = pathname === l.href;
              return (
                <Link
                  key={l.href}
                  href={l.href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition",
                    active
                      ? "bg-amber-50 text-amber-700"
                      : "text-slate-600 hover:bg-slate-100",
                  )}
                >
                  <l.icon size={18} />
                  {l.label}
                </Link>
              );
            })}
          </nav>

          <div className="p-4 border-t border-slate-100 text-xs text-slate-500">
            Signed in as <strong>{user.full_name}</strong>
          </div>
        </aside>

        <main>{children}</main>
      </div>
    </div>
  );
}
