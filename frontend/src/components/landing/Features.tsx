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

export function Features() {
  return (
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
  );
}
