"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import {
  LayoutDashboard,
  PlayCircle,
  FileText,
  BarChart3,
  ShieldCheck,
  LogOut,
} from "lucide-react";

import { useAuthStore } from "@/store/authStore";
import { cn } from "@/lib/utils";

const navLinks = [
  { href: "/dashboard",            label: "Overview",  icon: LayoutDashboard },
  { href: "/dashboard/interview",  label: "Interview", icon: PlayCircle },
  { href: "/dashboard/resume",     label: "Resume",    icon: FileText },
  { href: "/dashboard/analytics",  label: "Analytics", icon: BarChart3 },
];

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, token, logout } = useAuthStore();

  // Client-side auth guard. (We can't use middleware easily because the
  // token lives in localStorage.)
  useEffect(() => {
    if (!token) router.replace("/login");
  }, [token, router]);

  if (!token || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center text-slate-500">
        Loading…
      </div>
    );
  }

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="grid lg:grid-cols-[260px_1fr]">
        {/* Sidebar */}
        <aside className="hidden lg:flex flex-col bg-white border-r border-slate-100 min-h-screen">
          <Link href="/" className="flex items-center gap-2 font-semibold p-6">
            <span className="inline-flex w-8 h-8 rounded-lg bg-brand-500 text-white items-center justify-center">
              A
            </span>
            <span>AI Interview Prep</span>
          </Link>

          <nav className="flex-1 px-4 space-y-1">
            {navLinks.map((l) => {
              const active = pathname === l.href;
              return (
                <Link
                  key={l.href}
                  href={l.href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition",
                    active
                      ? "bg-brand-50 text-brand-700"
                      : "text-slate-600 hover:bg-slate-100",
                  )}
                >
                  <l.icon size={18} />
                  {l.label}
                </Link>
              );
            })}
            {user.role === "admin" && (
              <Link
                href="/admin"
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition",
                  pathname.startsWith("/admin")
                    ? "bg-brand-50 text-brand-700"
                    : "text-slate-600 hover:bg-slate-100",
                )}
              >
                <ShieldCheck size={18} /> Admin
              </Link>
            )}
          </nav>

          <div className="p-4 border-t border-slate-100">
            <div className="px-3 mb-3">
              <p className="text-sm font-medium truncate">{user.full_name}</p>
              <p className="text-xs text-slate-500 truncate">{user.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100"
            >
              <LogOut size={18} /> Logout
            </button>
          </div>
        </aside>

        <main>{children}</main>
      </div>
    </div>
  );
}
