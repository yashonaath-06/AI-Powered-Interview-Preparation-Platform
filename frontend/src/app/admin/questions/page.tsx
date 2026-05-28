"use client";
import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { Plus, Trash2, Edit3, X } from "lucide-react";

import { api } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

interface Question {
  id: number;
  text: string;
  category: "technical" | "hr" | "behavioral";
  difficulty: "easy" | "medium" | "hard";
  company: string | null;
  role: string | null;
  expected_keywords: string[] | null;
  sample_answer: string | null;
}

export default function AdminQuestionsPage() {
  const qc = useQueryClient();
  const [filter, setFilter] = useState<{ category?: string; company?: string; role?: string }>({});
  const [editing, setEditing] = useState<Partial<Question> | null>(null);

  const list = useQuery<Question[]>({
    queryKey: ["admin-questions", filter],
    queryFn: async () =>
      (await api.get("/api/questions", { params: { ...filter, limit: 100 } })).data,
  });

  const refresh = () => {
    qc.invalidateQueries({ queryKey: ["admin-questions"] });
    qc.invalidateQueries({ queryKey: ["question-meta"] });
  };

  const onDelete = async (q: Question) => {
    if (!confirm("Delete this question?")) return;
    try {
      await api.delete(`/api/admin/questions/${q.id}`);
      toast.success("Deleted");
      refresh();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Delete failed");
    }
  };

  return (
    <div className="p-6 lg:p-10 max-w-6xl mx-auto">
      <header className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Question bank</h1>
          <p className="text-slate-500 text-sm mt-1">
            Curate the questions used in mock interviews.
          </p>
        </div>
        <Button onClick={() => setEditing({})}>
          <Plus size={14} /> New question
        </Button>
      </header>

      {/* Filters */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <select
          value={filter.category || ""}
          onChange={(e) => setFilter({ ...filter, category: e.target.value || undefined })}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm"
        >
          <option value="">All categories</option>
          <option value="technical">Technical</option>
          <option value="hr">HR</option>
          <option value="behavioral">Behavioral</option>
        </select>
        <Input
          placeholder="Company filter…"
          value={filter.company || ""}
          onChange={(e) => setFilter({ ...filter, company: e.target.value || undefined })}
        />
        <Input
          placeholder="Role filter…"
          value={filter.role || ""}
          onChange={(e) => setFilter({ ...filter, role: e.target.value || undefined })}
        />
      </div>

      {/* List */}
      <Card className="p-0 overflow-hidden">
        {list.isLoading ? (
          <p className="p-6 text-center text-slate-400">Loading…</p>
        ) : (list.data?.length ?? 0) === 0 ? (
          <p className="p-6 text-center text-slate-400">No questions match your filters.</p>
        ) : (
          <div className="divide-y divide-slate-100">
            {list.data!.map((q) => (
              <div key={q.id} className="p-4 hover:bg-slate-50 transition flex items-start gap-3">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium">{q.text}</p>
                  <div className="flex flex-wrap gap-1.5 mt-2 text-[11px]">
                    <Pill>{q.category}</Pill>
                    <Pill>{q.difficulty}</Pill>
                    {q.company && <Pill tone="brand">{q.company}</Pill>}
                    {q.role && <Pill tone="slate">{q.role}</Pill>}
                  </div>
                </div>
                <button
                  onClick={() => setEditing(q)}
                  className="p-2 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
                >
                  <Edit3 size={14} />
                </button>
                <button
                  onClick={() => onDelete(q)}
                  className="p-2 rounded-lg text-red-500 hover:bg-red-50"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </Card>

      {editing != null && (
        <QuestionForm
          initial={editing}
          onClose={() => setEditing(null)}
          onSaved={() => { setEditing(null); refresh(); }}
        />
      )}
    </div>
  );
}

function Pill({ children, tone = "slate" }: { children: React.ReactNode; tone?: "brand" | "slate" }) {
  return (
    <span className={cn(
      "px-2 py-0.5 rounded-full font-medium",
      tone === "brand" ? "bg-brand-50 text-brand-700" : "bg-slate-100 text-slate-600",
    )}>
      {children}
    </span>
  );
}

function QuestionForm({
  initial,
  onClose,
  onSaved,
}: {
  initial: Partial<Question>;
  onClose: () => void;
  onSaved: () => void;
}) {
  const isEdit = !!initial.id;
  const [form, setForm] = useState<any>({
    text: initial.text || "",
    category: initial.category || "technical",
    difficulty: initial.difficulty || "medium",
    company: initial.company || "",
    role: initial.role || "",
    expected_keywords: (initial.expected_keywords || []).join(", "),
    sample_answer: initial.sample_answer || "",
  });
  const [saving, setSaving] = useState(false);

  const onSubmit = async () => {
    if (form.text.trim().length < 5) {
      toast.error("Question text is too short.");
      return;
    }
    setSaving(true);
    const payload: any = {
      text: form.text.trim(),
      category: form.category,
      difficulty: form.difficulty,
      company: form.company.trim() || null,
      role: form.role.trim() || null,
      expected_keywords: form.expected_keywords
        ? form.expected_keywords.split(",").map((s: string) => s.trim()).filter(Boolean)
        : null,
      sample_answer: form.sample_answer.trim() || null,
    };
    try {
      if (isEdit) {
        await api.patch(`/api/admin/questions/${initial.id}`, payload);
        toast.success("Updated");
      } else {
        await api.post("/api/admin/questions", payload);
        toast.success("Created");
      }
      onSaved();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Save failed");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-xl">
        <div className="flex items-center justify-between p-5 border-b border-slate-100">
          <h3 className="font-semibold">{isEdit ? "Edit question" : "New question"}</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700"><X size={18} /></button>
        </div>
        <div className="p-5 space-y-3">
          <label className="block">
            <span className="block text-sm font-medium text-slate-700 mb-1.5">Question text</span>
            <textarea
              rows={3}
              value={form.text}
              onChange={(e) => setForm({ ...form, text: e.target.value })}
              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200"
            />
          </label>
          <div className="grid grid-cols-2 gap-3">
            <label>
              <span className="block text-sm font-medium text-slate-700 mb-1.5">Category</span>
              <select className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                <option value="technical">Technical</option>
                <option value="hr">HR</option>
                <option value="behavioral">Behavioral</option>
              </select>
            </label>
            <label>
              <span className="block text-sm font-medium text-slate-700 mb-1.5">Difficulty</span>
              <select className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm" value={form.difficulty} onChange={(e) => setForm({ ...form, difficulty: e.target.value })}>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </label>
            <Input label="Company (optional)" value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} />
            <Input label="Role (optional)" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} />
          </div>
          <Input
            label="Expected keywords (comma separated)"
            value={form.expected_keywords}
            onChange={(e) => setForm({ ...form, expected_keywords: e.target.value })}
            placeholder="memoization, optimal substructure, knapsack"
          />
          <label className="block">
            <span className="block text-sm font-medium text-slate-700 mb-1.5">Sample answer (optional, used for semantic scoring)</span>
            <textarea
              rows={4}
              value={form.sample_answer}
              onChange={(e) => setForm({ ...form, sample_answer: e.target.value })}
              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200"
            />
          </label>
        </div>
        <div className="px-5 pb-5 flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={onSubmit} loading={saving}>
            {isEdit ? "Save changes" : "Create"}
          </Button>
        </div>
      </div>
    </div>
  );
}
