/**
 * Landing page — Phase 2 baseline.
 * In Phase 3 we'll split this into <Navbar/>, <Hero/>, <Features/>,
 * <HowItWorks/>, <CTA/>, <Footer/>. For now it's a single beautiful
 * page so users have something to look at after `npm run dev`.
 */
"use client";

import { motion } from "framer-motion";
import { Brain, Camera, Mic, Sparkles, BarChart3, ShieldCheck } from "lucide-react";

const features = [
  { icon: Mic,         title: "Real Speech Analysis",   desc: "Whisper transcribes your spoken answers and we evaluate fluency, pacing, and filler words." },
  { icon: Brain,       title: "NLP Answer Scoring",     desc: "Semantic similarity, grammar, and clarity scoring on every response." },
  { icon: Camera,      title: "Computer Vision",        desc: "Face presence, emotion, eye contact, and head pose tracked through your webcam." },
  { icon: Sparkles,    title: "Company-Specific AI",    desc: "Mock rounds tailored to Google, Amazon, TCS, Infosys and many more." },
  { icon: BarChart3,   title: "Progress Dashboard",     desc: "Track scores across sessions and watch yourself improve over time." },
  { icon: ShieldCheck, title: "Private & Secure",       desc: "Your video never leaves your browser unless you choose to upload it." },
];

export default function HomePage() {
  return (
    <main className="min-h-screen">
      {/* Top nav */}
      <header className="sticky top-0 z-30 bg-white/70 backdrop-blur border-b border-slate-100">
        <div className="container-tight flex items-center justify-between h-16">
          <div className="flex items-center gap-2 font-semibold text-lg">
            <span className="inline-flex w-8 h-8 rounded-lg bg-brand-500 text-white items-center justify-center">A</span>
            <span>AI Interview Prep</span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm text-slate-700">
            <a href="#features" className="hover:text-slate-900">Features</a>
            <a href="#how" className="hover:text-slate-900">How it works</a>
            <a href="/login" className="hover:text-slate-900">Login</a>
            <a
              href="/signup"
              className="px-4 py-2 rounded-lg bg-brand-500 text-white hover:bg-brand-600 transition"
            >
              Get started
            </a>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-hero-grid bg-[size:48px_48px] opacity-40 -z-10" />
        <div className="container-tight pt-20 pb-24 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <span className="inline-block text-xs uppercase tracking-widest text-brand-600 font-semibold mb-4">
              Final-year project · AI · NLP · Computer Vision
            </span>
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
              Ace your next interview <br className="hidden md:block" />
              with <span className="gradient-text">an AI coach</span>.
            </h1>
            <p className="mt-6 text-lg text-slate-600 max-w-2xl mx-auto">
              Realistic mock interviews tailored to any company and role. Get instant
              feedback on your answers, voice, expression, and body language — backed by
              state-of-the-art AI.
            </p>
            <div className="mt-10 flex items-center justify-center gap-4">
              <a
                href="/signup"
                className="px-6 py-3 rounded-lg bg-brand-500 text-white font-medium hover:bg-brand-600 transition shadow-sm"
              >
                Start Free Mock Interview
              </a>
              <a
                href="#features"
                className="px-6 py-3 rounded-lg border border-slate-200 hover:border-slate-300 transition font-medium"
              >
                Learn more →
              </a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 bg-slate-50 border-y border-slate-100">
        <div className="container-tight">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl md:text-4xl font-bold">Everything you need to prepare</h2>
            <p className="mt-3 text-slate-600">
              Six AI-powered modules working together to give you a complete interview readiness score.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="rounded-2xl bg-white border border-slate-100 p-6 shadow-sm hover:shadow-md transition"
              >
                <div className="w-10 h-10 rounded-lg bg-brand-50 text-brand-600 flex items-center justify-center mb-4">
                  <f.icon size={20} />
                </div>
                <h3 className="font-semibold text-lg">{f.title}</h3>
                <p className="mt-2 text-sm text-slate-600">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="py-20">
        <div className="container-tight">
          <h2 className="text-3xl md:text-4xl font-bold text-center">How it works</h2>
          <ol className="mt-12 grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            {["Pick company & role", "AI asks questions", "Camera + mic analyze you", "Get a detailed report"].map((step, i) => (
              <li key={step}>
                <div className="mx-auto w-12 h-12 rounded-full bg-brand-500 text-white font-bold text-lg flex items-center justify-center">
                  {i + 1}
                </div>
                <p className="mt-4 font-medium">{step}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 border-t border-slate-100 bg-white">
        <div className="container-tight flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-slate-500">
          <p>© {new Date().getFullYear()} AI Interview Prep — Final-year project.</p>
          <p>Built with Next.js · FastAPI · Whisper · MediaPipe</p>
        </div>
      </footer>
    </main>
  );
}
