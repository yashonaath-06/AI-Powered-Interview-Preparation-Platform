# 🎤 Presentation Outline — AI-Powered Interview Preparation Platform

> 12-slide deck script. Convert each section to a slide in PowerPoint / Google Slides / Canva. Every slide has a **headline**, **3-5 bullet points**, and **speaker notes**.

---

## Slide 1 — Title

**Headline:** AI-Powered Interview Preparation Platform

- Final-year B.Tech / B.E. major project
- Full-stack · AI · NLP · Computer Vision
- Built by [Your Name], [Your Roll No.], [Your Branch], [Your College]
- Guide: [Guide's Name]

**Speaker notes (30 s):** Brief intro of yourself and the title. "Today I'll show you a platform that conducts realistic AI mock interviews, evaluates answers using NLP, and analyses your body language with computer vision."

---

## Slide 2 — The Problem

**Headline:** Why interview prep is broken today

- 92% of engineering students struggle with interview confidence (placement-cell surveys)
- Mock interviews require a human — doesn't scale
- Online courses only test trivia, not real conversation
- Coaching institutes cost ₹15,000-₹40,000 per programme
- No standardised, multi-dimensional feedback

**Speaker notes:** Set up the pain. Frame the gap.

---

## Slide 3 — The Solution

**Headline:** A 24/7 AI Coach in the browser

- Pick a target company and role (Google · Amazon · TCS · ...)
- AI asks tailored questions
- You answer with **voice** (Whisper transcribes) and **camera** (MediaPipe analyses)
- Get a multi-dimensional report: technical accuracy · communication · confidence · engagement
- Track yourself improving across sessions

**Speaker notes:** Quick "what is the product" pitch. One sentence each. Mention "free, open-source, runs on a laptop."

---

## Slide 4 — Live Demo Storyboard

*(Optional — if doing a live demo, replace this slide with screen recording.)*

1. Sign up → Dashboard
2. Start interview → Pick "Google · Software Engineer · Mixed · 5 questions"
3. Speak an answer with camera on
4. See live signals (face, eye contact, head pose, smile)
5. Submit → score toast
6. After last question → animated report
7. Visit Analytics → trend, radar, weakness list
8. Visit Resume Analyzer → upload PDF → match score + AI feedback

**Speaker notes:** Aim for 2-3 minutes. Keep narration tight.

---

## Slide 5 — System Architecture

**Headline:** Modular monorepo

- **Frontend:** Next.js 14 + Tailwind + Framer Motion + Recharts
- **Backend:** Python FastAPI + SQLAlchemy 2.0 + PostgreSQL
- **AI Services:** Whisper · sentence-transformers · MediaPipe · Groq LLM
- **Infra:** Docker Compose locally · Vercel + Render in prod
- ~9,000 LoC, 40 automated tests, GitHub Actions CI

*Insert architecture diagram from `ARCHITECTURE.md`*

**Speaker notes:** Walk left-to-right through the diagram. Emphasise capability-flag fallback so it works without GPU.

---

## Slide 6 — AI Pipeline (most-asked slide)

**Headline:** From microphone to score in under 5 seconds

```
audio → Whisper → transcript
                  │
                  ▼
       sentence-transformers
       cosine vs sample answer       ┐
       + keyword coverage            │
       + Flesch readability          ├── 4-dim score
       + filler/hedging penalty      │
       + vision aggregate            │   (radar chart)
       (face %, eye contact %)       ┘
```

- Each signal has a defined weight (see Section 6 of the project report)
- Designed so the loss of any one signal degrades gracefully

**Speaker notes:** This is the slide examiners will probe. Be ready to defend each weight choice.

---

## Slide 7 — Computer Vision Module

**Headline:** Reading body language with MediaPipe FaceMesh

- 468 facial landmarks + 10 iris landmarks per frame
- **Head pose** via `cv2.solvePnP` on 6 anchor points → yaw, pitch, roll in degrees
- **Gaze direction** from iris position relative to eye corners → x,y in [-1, +1]
- **Smile score** from mouth-corner curvature heuristic
- **Engagement** composite = face% × 5 + face% × eyeContact% × 4 + headStillness × 1

*Insert screenshot of live webcam panel*

**Speaker notes:** Mention 1 fps capture rate keeps bandwidth low (~30 KB/frame) and analysis stays under 50 ms / frame on CPU.

---

## Slide 8 — Resume Analyzer

**Headline:** Skill-aware feedback in 5 seconds

- pypdf extracts text from any text-based PDF
- Curated 100+ skill taxonomy with aliases
- Compared against 10 role profiles (SDE, FE, BE, ML, DA, ...)
- 0-100 match score = 60% keyword + 20% completeness + 5% sections + ≤15% semantic
- LLM (Groq) writes coaching feedback; templated fallback if no key

*Insert screenshot of resume report card*

---

## Slide 9 — Analytics Dashboard

**Headline:** Watching yourself get better

- **Trend** line chart: overall + 4 dims chronologically
- **Radar** chart: latest vs historical average
- **By type** bar chart: technical / HR / behavioral averages
- **Top weaknesses** bucketizer: rolls per-answer notes into themed counts
- **Compare** any two sessions side by side

*Insert dashboard screenshot*

---

## Slide 10 — Engineering Highlights

**Headline:** Production-ready, not a toy

- 40 automated tests with isolated SQLite per test
- GitHub Actions CI on every push
- One-click Render Blueprint deploy
- Vercel-friendly Next.js with security headers
- Capability-flag based AI fallback (works without ML deps)
- bcrypt + JWT + role-based access control
- 67-question seeded bank ships with the repo

---

## Slide 11 — Limitations & Future Work

**Headline:** Honest gaps and a roadmap

- Whisper `tiny.en` makes occasional errors → upgrade to `small.en`
- Vision only looks at face → add MediaPipe Pose for posture
- Skill taxonomy is curated → augment with embedding-based discovery
- No realtime streaming → move to WebSocket Whisper
- No multi-tenant org → add invitation tokens for placement cells

**Speaker notes:** Showing self-awareness scores points with the panel.

---

## Slide 12 — Thank You + Q&A

**Headline:** Thank you. Questions?

- 📦 Repo: github.com/yashonaath-06/AI-Powered-Interview-Preparation-Platform
- 🌐 Live demo: [your-frontend.vercel.app]
- 📝 Project report: see `docs/PROJECT_REPORT.md`
- 📧 [Your Email]

**Speaker notes:** Close strong. Don't rush. Be ready for tough Qs (see VIVA_QA.md).

---

## Design tips

- **Theme:** clean blue (#2745f5) + white. Match the product.
- Use the same screenshots that appear in the live demo so audience can connect them.
- Embed two short videos (≤30 s each) on slide 4 — one of voice answer + report, one of webcam panel.
- Keep ≤6 bullets per slide; ≤15 words per bullet.
