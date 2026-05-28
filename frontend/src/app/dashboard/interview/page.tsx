"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { Sparkles, Building2, Briefcase } from "lucide-react";

import { api } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";

interface Meta {
  companies: string[];
  roles: string[];
  counts: Record<string, number>;
}

const TYPES = [
  { id: "mixed",      label: "Mixed",     description: "HR + Technical + Behavioral" },
  { id: "technical",  label: "Technical", description: "Role-specific deep dive" },
  { id: "hr",         label: "HR",        description: "Fit, motivation, soft skills" },
  { id: "behavioral", label: "Behavioral", description: "STAR-style situational" },
] as const;

const PRESETS = [
  { company: "Google",    role: "Software Engineer", type: "mixed" },
  { company: "Amazon",    role: "Software Engineer", type: "behavioral" },
  { company: "Microsoft", role: "Software Engineer", type: "technical" },
  { company: "TCS",       role: "Software Engineer", type: "hr" },
];

export default function InterviewSetupPage() {
  const router = useRouter();
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [type, setType] = useState<typeof TYPES[number]["id"]>("mixed");
  const [count, setCount] = useState(5);
  const [starting, setStarting] = useState(false);

  const meta = useQuery<Meta>({
    queryKey: ["question-meta"],
    queryFn: async () => (await api.get("/api/questions/meta")).data,
  });

  const start = async () => {
    setStarting(true);
    try {
      const { data } = await api.post("/api/interviews", {
        company: company || null,
        role: role || null,
        interview_type: type,
        num_questions: count,
      });
      router.push(`/dashboard/interview/${data.session_id}`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Failed to start interview");
    } finally {
      setStarting(false);
    }
  };

  const applyPreset = (p: typeof PRESETS[number]) => {
    setCompany(p.company);
    setRole(p.role);
    setType(p.type as any);
  };

  return (
    <div className="p-6 lg:p-10 max-w-4xl mx-auto">
      <header className="mb-8">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Sparkles className="text-brand-500" size={22} /> Mock Interview Studio
        </h1>
        <p className="text-slate-500 mt-1">
          Pick your target and we&apos;ll generate a tailored interview.
        </p>
      </header>

      {/* Quick presets */}
      <Card className="mb-6">
        <p className="text-sm font-medium mb-3 text-slate-700">Quick presets</p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {PRESETS.map((p) => (
            <button
              key={p.company}
              onClick={() => applyPreset(p)}
              className={cn(
                "rounded-lg border border-slate-200 p-3 text-left text-sm hover:border-brand-300 hover:bg-brand-50 transition",
                company === p.company && role === p.role && "border-brand-400 bg-brand-50",
              )}
            >
              <div className="font-medium">{p.company}</div>
              <div className="text-xs text-slate-500 capitalize">{p.role} · {p.type}</div>
            </button>
          ))}
        </div>
      </Card>

      <Card>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="relative">
            <Input
              label="Target company (optional)"
              list="company-suggestions"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g. Google"
            />
            <datalist id="company-suggestions">
              {meta.data?.companies.map((c) => <option key={c} value={c} />)}
            </datalist>
            <Building2 className="absolute right-3 top-9 text-slate-400" size={16} />
          </div>

          <div className="relative">
            <Input
              label="Target role (optional)"
              list="role-suggestions"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g. Software Engineer"
            />
            <datalist id="role-suggestions">
              {meta.data?.roles.map((r) => <option key={r} value={r} />)}
            </datalist>
            <Briefcase className="absolute right-3 top-9 text-slate-400" size={16} />
          </div>
        </div>

        <div className="mt-6">
          <p className="text-sm font-medium mb-2 text-slate-700">Interview type</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {TYPES.map((t) => (
              <button
                key={t.id}
                onClick={() => setType(t.id)}
                className={cn(
                  "rounded-lg border p-3 text-left text-sm transition",
                  type === t.id
                    ? "border-brand-500 bg-brand-50"
                    : "border-slate-200 hover:border-brand-300",
                )}
              >
                <div className="font-medium">{t.label}</div>
                <div className="text-xs text-slate-500">{t.description}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="mt-6">
          <p className="text-sm font-medium mb-2 text-slate-700">
            Number of questions: <span className="text-brand-600">{count}</span>
          </p>
          <input
            type="range"
            min={3} max={10} step={1}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
            className="w-full accent-brand-500"
          />
          <div className="flex justify-between text-xs text-slate-400 mt-1">
            <span>3</span><span>10</span>
          </div>
        </div>

        <div className="mt-8 flex justify-end">
          <Button onClick={start} loading={starting} size="lg">
            Start Interview
          </Button>
        </div>
      </Card>

      <p className="text-xs text-slate-400 mt-4 text-center">
        Tip: Set GROQ_API_KEY in your .env for AI-generated questions tailored exactly to your company &amp; role.
      </p>
    </div>
  );
}
