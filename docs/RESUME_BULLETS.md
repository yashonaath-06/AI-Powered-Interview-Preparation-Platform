# 📝 Resume Bullet Points — AI-Powered Interview Preparation Platform

> Drop these straight into the **Projects** section of your resume. They're impact-focused, quantified where possible, and use action verbs. Pick **3-5** that best match the role you're applying for.

---

## One-line tagline (top of the project)

> **AI-Powered Interview Preparation Platform** · Full-stack (Next.js + FastAPI) · 9,000 LoC · 40 automated tests · CI/CD on GitHub Actions · live at [your-frontend.vercel.app] · github.com/yashonaath-06/AI-Powered-Interview-Preparation-Platform

---

## Strong all-rounder bullets (use 3-5)

- **Designed and shipped** an end-to-end AI mock-interview platform combining **OpenAI Whisper** (speech-to-text), **sentence-transformers** (NLP scoring), and **MediaPipe FaceMesh** (computer-vision body-language analysis), giving candidates a 4-dimensional performance score in under 5 seconds per answer.

- **Architected** a modular monorepo (Next.js 14 + TypeScript frontend, Python FastAPI backend, PostgreSQL) with **capability-flag fallback** so every AI module degrades gracefully when its heavy dependency is absent — letting the platform run on a 4 GB laptop with zero ML installs.

- **Implemented** a state-machine-driven interview engine that generates company- and role-specific questions via Groq LLaMA-3 (free tier) with a **curated 67-question fallback bank**, persisting full session history including per-answer NLP and vision metrics in normalised SQL.

- **Built** a real-time webcam analysis pipeline using MediaPipe FaceMesh's 468 facial landmarks and OpenCV's `solvePnP` to compute head yaw/pitch/roll, iris-relative gaze direction, and smile scores at 1 fps with **<50 ms / frame on CPU**.

- **Designed** a baseline NLP scorer that blends sentence-transformer cosine similarity, paraphrase-tolerant keyword coverage, Flesch reading-ease, vocabulary type-token ratio, and filler-word penalties into 4 interpretable sub-scores (technical, communication, confidence, engagement).

- **Engineered** a resume analyzer that parses uploaded PDFs with `pypdf`, matches against a curated **100+ skill taxonomy** spanning 11 categories, computes a 0-100 match score against 10 standard role profiles, and produces LLM-written improvement feedback.

- **Implemented** a paginated admin panel (user CRUD + role-based access + question-bank curation + recurring-weakness analytics) gated by JWT + bcrypt + `require_admin` FastAPI dependency, with a CLI bootstrap utility (`python -m app.cli make-admin`) for the first-admin path.

- **Built** a performance-analytics dashboard with Recharts: chronological score trend (line chart), latest-vs-average dimension breakdown (radar chart), grouped averages by interview type (bar chart), automatic weakness theme bucketization, and side-by-side session comparison modal.

- **Wrote** 40 automated pytest tests (auth, interview lifecycle, admin RBAC, resume analysis, scoring, vision aggregation) and a GitHub Actions CI pipeline that runs both backend tests and a `next build` on every push and pull request.

- **Configured** one-click deployment via a Render blueprint (`render.yaml`) provisioning a FastAPI service plus managed PostgreSQL with auto-generated `JWT_SECRET`, plus a Vercel front-end with security headers, total monthly cost: **$0** on free tiers.

---

## Targeted variants

### 🔧 If applying for a **frontend** role

- **Built** a 14-route Next.js 14 application using TypeScript, Tailwind, Framer Motion, TanStack Query, Zustand, and Recharts; live MediaRecorder + getUserMedia integration for in-browser audio recording and webcam frame capture; reusable UI primitives (Button, Input, Card, ScoreRing) following accessibility best practices.

- **Engineered** a real-time interview studio with progressive disclosure: voice / text mode toggle, live mic-level waveform animation, per-frame webcam analysis with overlay signals, automatic transition to text mode on backend STT-unavailable 503 — all without page navigation.

### 🐍 If applying for a **backend / Python** role

- **Designed** 30+ FastAPI endpoints organised into 8 routers (auth, users, interviews, questions, resume, analytics, admin, health) with full OpenAPI documentation, Pydantic v2 request/response validation, and SQLAlchemy 2.0 typed models.

- **Implemented** secure JWT auth with bcrypt cost-12 hashing, `Depends(get_current_user)` and `require_admin` gating; auto-cascading user deletion via SQLAlchemy relationships; cross-tenant resource access prevented at every endpoint with 404 responses (verified by automated tests).

### 🤖 If applying for an **ML / AI** role

- **Combined** five AI modules (Whisper STT, sentence-transformer semantic similarity, textstat readability, MediaPipe FaceMesh vision, Groq LLaMA-3 question generation) into a coherent pipeline producing 4-dimensional candidate scores with deterministic fallbacks for every external dependency.

- **Designed** a multi-modal scoring function that fuses lexical signals (keyword coverage, fluency, length sweetspot) with neural signals (cosine similarity in 384-dim embedding space) and visual signals (face presence %, eye contact %, head pose) into per-question and session-level interpretable scores.

### ☁️ If applying for a **DevOps / SRE** role

- **Authored** docker-compose stack (Postgres + FastAPI + Next.js), multi-stage Dockerfile with `ffmpeg` and `libgl1` for ML runtime, GitHub Actions CI matrix (backend pytest + frontend type-check & build), Render Blueprint for one-click cloud provisioning, and a 3-path deployment guide (Vercel+Render / Docker VPS / manual).

---

## Phrasing tips

- Lead each bullet with an **action verb in past tense**: Designed, Built, Implemented, Engineered, Architected, Configured, Authored.
- **Quantify** wherever possible: number of routes, lines of code, latency, accuracy, test count, CPU/memory budget.
- Mention **named technologies** (Whisper, sentence-transformers, MediaPipe) — recruiters search for them.
- End each bullet with a **business outcome** when you can ("running on a 4 GB laptop", "$0 monthly cost", "4-dim score in <5 s").
- Keep each bullet **on one line** in your final PDF (use a small enough font / margin).
