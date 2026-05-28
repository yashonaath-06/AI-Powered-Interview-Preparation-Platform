<div align="center">

# 🎯 AI-Powered Interview Preparation Platform

### *A 24/7 AI coach that conducts realistic mock interviews, analyses your voice and body language, and tells you exactly how to improve.*

[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=nextdotjs)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)
[![Whisper](https://img.shields.io/badge/Whisper-tiny.en-purple)](https://github.com/SYSTRAN/faster-whisper)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-FaceMesh-green)](https://developers.google.com/mediapipe)
[![Tests](https://img.shields.io/badge/tests-40%20passing-brightgreen)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[**🌐 Live demo**](#) · [**🧪 How to test**](HOW_TO_TEST.md) · [**🏛️ Architecture**](ARCHITECTURE.md) · [**🚀 Deployment**](DEPLOYMENT.md) · [**📘 Project report**](docs/PROJECT_REPORT.md)

</div>

---

## ✨ What it does

```
📺 Sign in → pick "Google · Software Engineer · Mixed · 5 questions" → start
🎙️ AI asks the question; browser reads it aloud  
🎤 Speak the answer (Whisper transcribes)  
📷 Webcam tracks face, eye contact, head pose, smile in real time  
📊 After last question — beautiful animated report:
       • overall 0-10 score
       • 4 sub-scores (technical · communication · confidence · engagement)
       • AI-written coach feedback paragraph  
       • per-question accordion with sub-scores and tips
📈 Performance dashboard tracks you across all sessions
📄 Resume analyzer rates your PDF against a target role and suggests fixes
🛠️ Admin panel manages users, questions, and platform stats
```

## 🧩 Modules

| # | Module | What it does |
|---|---|---|
| 🔐 | **Auth** | JWT + bcrypt; signup, login, /me, role-based gating |
| 🤖 | **Interview Engine** | 67-question seed bank + Groq LLaMA-3 generation + session state machine |
| 🎙️ | **Speech-to-Text** | OpenAI Whisper via `faster-whisper` runtime (CPU-only) |
| 🧠 | **NLP Scorer** | sentence-transformers semantic similarity + keyword coverage + readability + filler/hedging penalty |
| 👁️ | **Computer Vision** | MediaPipe FaceMesh (468 + 10 iris landmarks) → head pose, gaze, smile, engagement |
| 📊 | **Analytics** | trend chart, radar, by-type bars, weakness bucketizer, session compare |
| 📄 | **Resume Analyzer** | pypdf parsing + 100-skill taxonomy + role match + AI feedback |
| 👨‍💼 | **Admin Panel** | user CRUD, question bank CRUD, platform stats, recent activity |

## 🏗️ Tech stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 14 · React 18 · TypeScript · Tailwind CSS · Framer Motion · Recharts · TanStack Query · Zustand |
| **Backend** | FastAPI · SQLAlchemy 2 · Pydantic v2 · python-jose · loguru |
| **Database** | PostgreSQL 16 (prod) · SQLite (dev/tests) |
| **AI / ML** | OpenAI Whisper (faster-whisper) · sentence-transformers (`all-MiniLM-L6-v2`) · MediaPipe FaceMesh · OpenCV · pypdf · textstat · Groq LLaMA-3 |
| **DevOps** | Docker · docker-compose · GitHub Actions · Vercel · Render |

## 🚀 Quickstart

> **Brand-new to coding?** Read [`SETUP_GUIDE.md`](SETUP_GUIDE.md) instead — it walks you through every install step.
>
> **Want to test what's already deployed?** Read [`HOW_TO_TEST.md`](HOW_TO_TEST.md) — 13 numbered steps with 🟢 expected results.

```bash
# 1. Clone
git clone https://github.com/yashonaath-06/AI-Powered-Interview-Preparation-Platform.git
cd AI-Powered-Interview-Preparation-Platform

# 2. Configure
cp .env.example .env
# (edit .env: set JWT_SECRET to a random 32+ char string)

# 3. Run everything
docker compose up --build
```

Then visit:
- 🌐 **Frontend** → http://localhost:3000
- 📖 **API docs** → http://localhost:8000/docs

## 📁 Repository tour

```
.
├── backend/              FastAPI server
│   ├── app/
│   │   ├── core/         security utils, FastAPI deps (get_current_user, require_admin)
│   │   ├── models/       SQLAlchemy 2.0 typed models (User, Question, Session, Answer, Resume)
│   │   ├── schemas/      Pydantic v2 request/response shapes
│   │   ├── routers/      auth · users · interviews · questions · resume · analytics · admin · health
│   │   ├── services/     auth · interview_engine · llm · nlp · scoring · speech · vision · resume · question
│   │   ├── data/         curated question bank + skill taxonomy
│   │   └── cli.py        admin bootstrap CLI
│   ├── tests/            40 pytest tests
│   ├── main.py           app factory + lifespan
│   ├── requirements.txt  base deps
│   ├── requirements-ml.txt   optional Whisper / NLP / vision deps
│   └── Dockerfile
│
├── frontend/             Next.js 14 app
│   ├── src/app/          14 routes (App Router)
│   │   ├── (auth)/       login, signup
│   │   ├── dashboard/    overview, interview, [id], [id]/report, analytics, resume
│   │   └── admin/        overview, users, questions, sessions
│   ├── src/components/   reusable UI + landing + interview + analytics + resume + admin
│   ├── src/lib/          api, audio, webcam, utils
│   ├── src/store/        Zustand auth store
│   └── src/providers/    React-Query + toast
│
├── .github/workflows/    GitHub Actions CI
├── docs/                 Project report · presentation outline · viva Q&A · resume bullets
├── docker-compose.yml    one-command stack (db + backend + frontend)
├── render.yaml           one-click Render Blueprint
├── ARCHITECTURE.md       system design, schema, AI pipeline, deployment topology
├── SETUP_GUIDE.md        zero-knowledge installer guide
├── HOW_TO_TEST.md        13-step beginner walkthrough
├── DEPLOYMENT.md         3 deployment paths
└── README.md             you are here
```

## 🧪 Testing

```bash
# 40 backend tests
cd backend && pytest -v

# Frontend type check + production build
cd frontend && npm run type-check && npm run build
```

GitHub Actions runs both pipelines on every push/PR.

## 🛠️ Build phases

This project was built incrementally across **20 phases**, each landing as a focused PR you can read in chronological order:

| Phase | Topic | Status |
|---|---|---|
| 1-2 | Architecture, folder structure, beginner setup guide | ✅ |
| 3-6 | Frontend foundation, backend skeleton, DB models, JWT auth | ✅ |
| 7 | AI interview engine | ✅ |
| 8 | Whisper speech-to-text | ✅ |
| 9 | NLP answer evaluation | ✅ |
| 10 | Computer vision (face, eye, pose, smile) | ✅ |
| 11 | Analytics dashboard | ✅ |
| 12 | Admin panel | ✅ |
| 13 | Resume analyzer | ✅ |
| 14 | 40-test pytest suite + GitHub Actions CI | ✅ |
| 15 | Render Blueprint + Vercel config + DEPLOYMENT guide | ✅ |
| 16 | README polish | ✅ |
| 17 | Technical project report | ✅ |
| 18 | Presentation deck outline | ✅ |
| 19 | Viva Q&A prep | ✅ |
| 20 | Resume bullet points | ✅ |

## 📜 License

MIT — see [`LICENSE`](LICENSE).

---

<div align="center">

**Built for placements. Open-sourced for everyone.** ⭐

[Open the docs](docs/) · [Run a mock interview](HOW_TO_TEST.md) · [Deploy in 3 minutes](DEPLOYMENT.md)

</div>
