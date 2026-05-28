import Link from "next/link";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="min-h-screen grid lg:grid-cols-2">
      {/* Left brand panel */}
      <aside className="hidden lg:flex flex-col justify-between p-10 bg-slate-900 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-hero-grid bg-[size:48px_48px] opacity-10" />
        <Link href="/" className="relative flex items-center gap-2 font-semibold">
          <span className="inline-flex w-8 h-8 rounded-lg bg-brand-500 text-white items-center justify-center">
            A
          </span>
          <span>AI Interview Prep</span>
        </Link>
        <div className="relative space-y-4">
          <h2 className="text-3xl font-bold leading-tight">
            The AI coach that helps you land your dream job.
          </h2>
          <p className="text-slate-300 max-w-md">
            Realistic mock interviews, instant feedback, and progress tracking — all
            powered by state-of-the-art AI.
          </p>
        </div>
        <p className="relative text-xs text-slate-400">
          © {new Date().getFullYear()} AI Interview Prep
        </p>
      </aside>

      {/* Right form panel */}
      <section className="flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-md">{children}</div>
      </section>
    </main>
  );
}
