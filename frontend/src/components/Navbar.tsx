"use client";
import Link from "next/link";
import { useAuthStore } from "@/store/authStore";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export function Navbar() {
  const { user, logout } = useAuthStore();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  // Prevent hydration mismatch (auth state is from localStorage)
  useEffect(() => setMounted(true), []);

  const onLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <header className="sticky top-0 z-30 bg-white/70 backdrop-blur border-b border-slate-100">
      <div className="container-tight flex items-center justify-between h-16">
        <Link href="/" className="flex items-center gap-2 font-semibold text-lg">
          <span className="inline-flex w-8 h-8 rounded-lg bg-brand-500 text-white items-center justify-center">
            A
          </span>
          <span>AI Interview Prep</span>
        </Link>
        <nav className="hidden md:flex items-center gap-8 text-sm text-slate-700">
          <a href="/#features" className="hover:text-slate-900">
            Features
          </a>
          <a href="/#how" className="hover:text-slate-900">
            How it works
          </a>
          {mounted && user ? (
            <>
              <Link href="/dashboard" className="hover:text-slate-900">
                Dashboard
              </Link>
              <span className="text-slate-500">Hi, {user.full_name.split(" ")[0]}</span>
              <button onClick={onLogout} className="hover:text-slate-900">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="hover:text-slate-900">
                Login
              </Link>
              <Link
                href="/signup"
                className="px-4 py-2 rounded-lg bg-brand-500 text-white hover:bg-brand-600 transition"
              >
                Get started
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
