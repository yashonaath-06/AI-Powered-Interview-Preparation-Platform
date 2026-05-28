"use client";
import Link from "next/link";
import { motion } from "framer-motion";

export function Hero() {
  return (
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
            <Link
              href="/signup"
              className="px-6 py-3 rounded-lg bg-brand-500 text-white font-medium hover:bg-brand-600 transition shadow-sm"
            >
              Start Free Mock Interview
            </Link>
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
  );
}
