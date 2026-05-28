"use client";
import { useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { UploadCloud, FileText, Trash2 } from "lucide-react";
import toast from "react-hot-toast";

import { api } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";
import { ResumeReport, ResumeAnalysis } from "@/components/resume/ResumeReport";

export default function ResumePage() {
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [uploading, setUploading] = useState(false);
  const [latest, setLatest] = useState<ResumeAnalysis | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const list = useQuery<any[]>({
    queryKey: ["resumes"],
    queryFn: async () => (await api.get("/api/resume")).data,
  });

  const refresh = () => qc.invalidateQueries({ queryKey: ["resumes"] });

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f && f.type === "application/pdf") setFile(f);
    else toast.error("Only PDF files are supported.");
  };

  const upload = async () => {
    if (!file) {
      toast.error("Please choose a PDF first.");
      return;
    }
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("resume", file, file.name);
      if (targetRole.trim()) fd.append("target_role", targetRole.trim());
      const { data } = await api.post("/api/resume/analyze", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setLatest(data);
      setFile(null);
      if (fileRef.current) fileRef.current.value = "";
      toast.success(`Match score: ${data.match_score}/100`);
      refresh();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Analysis failed");
    } finally {
      setUploading(false);
    }
  };

  const openPast = async (id: number) => {
    const { data } = await api.get(`/api/resume/${id}`);
    setLatest(data);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const deletePast = async (id: number) => {
    if (!confirm("Delete this resume analysis?")) return;
    try {
      await api.delete(`/api/resume/${id}`);
      toast.success("Deleted");
      refresh();
      if (latest?.id === id) setLatest(null);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Delete failed");
    }
  };

  return (
    <div className="p-6 lg:p-10 max-w-4xl mx-auto">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">Resume Analyzer</h1>
        <p className="text-slate-500 text-sm mt-1">
          Upload your PDF resume — we&apos;ll extract skills, match them against your
          target role, and give you AI-generated improvement tips.
        </p>
      </header>

      <Card>
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          onClick={() => fileRef.current?.click()}
          className={`cursor-pointer border-2 border-dashed rounded-xl p-8 text-center transition ${
            dragOver ? "border-brand-500 bg-brand-50" : "border-slate-200 hover:border-slate-300"
          }`}
        >
          <UploadCloud size={28} className="mx-auto text-slate-400 mb-3" />
          {file ? (
            <p className="text-sm">
              <span className="font-medium">{file.name}</span>
              <span className="text-slate-400"> ({Math.round(file.size / 1024)} KB)</span>
            </p>
          ) : (
            <>
              <p className="text-sm font-medium">Drop your resume here, or click to browse</p>
              <p className="text-xs text-slate-400 mt-1">PDF only · max 8 MB</p>
            </>
          )}
          <input
            ref={fileRef}
            type="file"
            accept="application/pdf"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </div>

        <div className="mt-4 grid grid-cols-1 sm:grid-cols-[1fr_auto] gap-3">
          <Input
            label="Target role (optional)"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g. Software Engineer"
          />
          <div className="flex items-end">
            <Button onClick={upload} loading={uploading} disabled={!file}>
              Analyze resume
            </Button>
          </div>
        </div>
      </Card>

      {latest && (
        <div className="mt-8">
          <ResumeReport analysis={latest} />
        </div>
      )}

      {/* Past resumes */}
      <section className="mt-10">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <FileText size={16} /> Past analyses
        </h2>
        {list.isLoading ? (
          <p className="text-slate-500 text-sm">Loading…</p>
        ) : (list.data?.length ?? 0) === 0 ? (
          <p className="text-slate-500 text-sm">No past analyses yet.</p>
        ) : (
          <Card className="p-0 overflow-hidden">
            <ul className="divide-y divide-slate-100">
              {list.data!.map((r) => (
                <li key={r.id} className="p-4 flex items-center gap-3 hover:bg-slate-50">
                  <FileText size={16} className="text-slate-400 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{r.filename}</p>
                    <p className="text-xs text-slate-500">
                      {r.target_role || "Generic"} · {new Date(r.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className="px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 text-xs font-medium tabular-nums">
                    {r.match_score?.toFixed(1) ?? "—"} / 100
                  </span>
                  <button
                    onClick={() => openPast(r.id)}
                    className="text-xs text-slate-600 hover:text-slate-900"
                  >
                    View
                  </button>
                  <button
                    onClick={() => deletePast(r.id)}
                    className="p-1.5 text-red-500 hover:bg-red-50 rounded"
                  >
                    <Trash2 size={14} />
                  </button>
                </li>
              ))}
            </ul>
          </Card>
        )}
      </section>
    </div>
  );
}
