"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import toast from "react-hot-toast";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";

export default function SignupPage() {
  const router = useRouter();
  const setSession = useAuthStore((s) => s.setSession);
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.post("/api/auth/signup", form);
      setSession(data.access_token, data.user);
      toast.success(`Welcome, ${data.user.full_name.split(" ")[0]}!`);
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <h1 className="text-2xl font-bold">Create your account</h1>
      <p className="text-sm text-slate-500 mt-1">
        Start your AI interview practice in seconds.
      </p>

      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <Input
          label="Full name"
          name="full_name"
          required
          minLength={2}
          value={form.full_name}
          onChange={(e) => setForm({ ...form, full_name: e.target.value })}
          placeholder="Alex Johnson"
        />
        <Input
          label="Email"
          type="email"
          name="email"
          required
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          placeholder="you@example.com"
        />
        <Input
          label="Password"
          type="password"
          name="password"
          required
          minLength={8}
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          placeholder="At least 8 characters"
        />
        <Button type="submit" className="w-full" loading={loading}>
          Create account
        </Button>
      </form>

      <p className="mt-6 text-sm text-slate-600 text-center">
        Already have an account?{" "}
        <Link href="/login" className="text-brand-600 font-medium hover:underline">
          Sign in
        </Link>
      </p>
    </>
  );
}
