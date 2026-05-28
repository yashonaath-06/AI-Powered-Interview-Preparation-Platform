# 🎯 AI-Powered Interview Preparation Platform

> A full-stack, AI-powered mock interview platform that conducts realistic interviews, analyzes answers with NLP, reads facial emotion + body language with computer vision, and gives candidates personalized improvement reports.

[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=nextdotjs)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ Highlights

- 🤖 **Dynamic AI Interviewer** — generates company- and role-specific questions (Google SDE, TCS HR, Amazon Behavioral, etc.)
- 🎙️ **Speech-to-Text** — OpenAI Whisper transcribes spoken answers in real time
- 🧠 **NLP Answer Evaluation** — semantic similarity, grammar, fluency, and confidence scoring
- 👁️ **Computer Vision** — face detection, emotion recognition, eye-contact tracking, head-pose estimation
- 📊 **Performance Dashboard** — beautiful charts, multi-session comparisons, growth analytics
- 📄 **Resume Analyzer** — uploads PDF resume, extracts skills, matches them to the target role
- 👨‍💼 **Admin Panel** — user management, question bank CRUD, platform analytics
- 🔐 **Secure Auth** — JWT-based, bcrypt password hashing, role-based access
- 🐳 **One-command setup** — `docker compose up`

---

## 🏗️ Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | Next.js 14 · React 18 · TypeScript · Tailwind CSS · Framer Motion · shadcn/ui · Recharts · Zustand |
| Backend | FastAPI · SQLAlchemy 2 · Alembic · Pydantic v2 · Uvicorn |
| Database | PostgreSQL 16 (prod) · SQLite (dev) |
| AI / ML | OpenAI Whisper · HuggingFace Transformers · sentence-transformers · MediaPipe · OpenCV · DeepFace · spaCy |
| LLM | Groq (LLaMA-3) with curated JSON fallback |
| Auth | JWT (python-jose) + bcrypt |
| DevOps | Docker · docker-compose · Vercel · Render |

---

## 🚀 Quick Start

> **Brand-new to coding?** Read [`SETUP_GUIDE.md`](SETUP_GUIDE.md) instead — it explains every single step assuming you have never installed anything before.

```bash
# 1. clone
git clone https://github.com/yashonaath-06/AI-Powered-Interview-Preparation-Platform.git
cd AI-Powered-Interview-Preparation-Platform

# 2. create your env file from the template
cp .env.example .env

# 3. start everything (DB + backend + frontend)
docker compose up --build
```

Open:
- Frontend → http://localhost:3000
- Backend API docs → http://localhost:8000/docs

> 🧪 **Want to actually test it without Docker?** Read [`HOW_TO_TEST.md`](HOW_TO_TEST.md) — a 5-minute step-by-step walkthrough with expected results at every step.

---

## 📁 Repository Structure

```
.
├── backend/        FastAPI server, AI services, DB models
├── frontend/       Next.js website
├── docker-compose.yml
├── ARCHITECTURE.md detailed system design
└── SETUP_GUIDE.md  zero-knowledge setup guide
```

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for diagrams and deep-dives.

---

## 🛣️ Roadmap

This project is built in 20 phases. Tracked in detail in [`ARCHITECTURE.md`](ARCHITECTURE.md).

- [x] Phase 1 — Architecture & tech selection
- [x] Phase 2 — Folder structure & beginner setup guide
- [x] Phase 3 — Frontend foundation
- [x] Phase 4 — Backend foundation
- [x] Phase 5 — Database & migrations
- [x] Phase 6 — Authentication
- [x] Phase 7 — AI interview engine
- [x] Phase 8 — Speech-to-text (Whisper)
- [x] Phase 9 — NLP evaluation
- [x] Phase 10 — Computer vision
- [x] Phase 11 — Analytics dashboard
- [x] Phase 12 — Admin panel
- [ ] Phase 13 — Resume analyzer
- [ ] Phase 14 — Tests
- [ ] Phase 15 — Deployment
- [ ] Phase 16-20 — Docs, PPT, viva prep, resume bullets

---

## 📜 License

MIT — see [LICENSE](LICENSE).
