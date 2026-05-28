# 📘 Project Report — AI-Powered Interview Preparation Platform

> A submission-ready technical document. Use this as the body of your final-year project report; copy sections into your university's template as needed.

---

## 1. Abstract

The AI-Powered Interview Preparation Platform is a full-stack web application that conducts realistic mock interviews tailored to a target company and role. During each session the platform records the candidate's spoken answers, transcribes them with **OpenAI Whisper**, evaluates content quality using a **sentence-transformer NLP scorer**, and analyses webcam frames in real time with **MediaPipe FaceMesh** to estimate face presence, head pose, eye contact and engagement. The candidate receives a multi-dimensional report covering technical accuracy, communication, confidence and engagement, plus an LLM-generated coaching paragraph. A separate **resume analyzer** parses uploaded PDFs, extracts skills against a curated 100+ skill taxonomy, and produces a 0-100 match score against the target role. Personal performance trends are visualised in a dedicated analytics dashboard, and an admin panel provides user / question-bank management.

**Keywords:** Mock interview, NLP, Speech-to-Text, Computer Vision, Sentence Transformers, MediaPipe, Whisper, Resume Analysis, FastAPI, Next.js.

---

## 2. Problem Statement

Engineering and MBA students preparing for placements have **two recurring pain points**:

1. **No realistic practice environment.** Live mocks need a peer or mentor and rarely scale.
2. **No objective, multi-dimensional feedback.** Friends provide opinions; standardised evaluation across content, communication and body-language is missing.

This project addresses both by combining modern AI components into a single platform that any student can run at home.

---

## 3. Objectives

- **O1.** Provide an interactive AI interviewer that asks role- and company-specific questions.
- **O2.** Transcribe spoken answers locally (privacy-friendly) using OpenAI Whisper.
- **O3.** Evaluate answer quality with sentence-transformer semantic similarity, keyword coverage, fluency and readability metrics.
- **O4.** Analyse webcam frames for face presence, head pose, eye gaze and smile.
- **O5.** Aggregate the multi-modal signals into four interpretable scores: technical, communication, confidence, engagement.
- **O6.** Track candidate progress across sessions with a charting dashboard.
- **O7.** Analyse uploaded resumes against a target role and produce a match score with AI feedback.
- **O8.** Provide admin tooling for question-bank curation and user management.

---

## 4. Literature & Tech Survey

| Domain | Selected technique | Why |
|---|---|---|
| Speech-to-Text | **Whisper (faster-whisper runtime)** | State-of-the-art accuracy, free, runs on CPU; CTranslate2 backend gives 4× speedup over OpenAI's reference implementation |
| NLP semantic scoring | **sentence-transformers `all-MiniLM-L6-v2`** | 80 MB, ~10 ms / answer on CPU; produces 384-dim embeddings whose cosine similarity correlates well with human paraphrase judgements |
| Readability | **textstat (Flesch reading-ease)** | Pure-Python; well-known proxy for spoken-clarity |
| Computer vision | **MediaPipe FaceMesh** + OpenCV `solvePnP` | 468 facial landmarks + 10 iris landmarks; head pose via PnP from 6 anchors; iris-relative gaze estimation |
| Question generation | **Groq LLaMA-3 (free tier)** with curated bank fallback | Cost-free generation; deterministic fallback so the platform works offline |
| Resume parsing | **pypdf** + curated 100-skill taxonomy + sentence-transformers | No system deps; both literal and semantic match |
| Auth | **JWT + bcrypt** | Industry standard; stateless tokens; passwords salted |

---

## 5. System Architecture

```
┌────────────────────────┐      HTTPS/JSON       ┌────────────────────────┐
│      BROWSER           │ ◄───────────────────► │   FastAPI Backend      │
│   (Next.js + React)    │                       │                        │
│                        │   webcam frame upload │  ┌──────────────────┐  │
│  Landing / Auth /      │ ◄───────────────────► │  │  Auth · Users    │  │
│  Interview Studio /    │                       │  │  Interviews · Q  │  │
│  Dashboard /           │   audio blob upload   │  │  Resume · Admin  │  │
│  Analytics /           │ ◄───────────────────► │  │  Analytics       │  │
│  Resume / Admin        │                       │  └──────────────────┘  │
└────────────────────────┘                       │  ┌──────────────────┐  │
                                                 │  │  AI Services     │  │
                                                 │  │  • Whisper STT   │  │
                                                 │  │  • NLP Scorer    │  │
                                                 │  │  • Vision        │  │
                                                 │  │  • Resume        │  │
                                                 │  │  • LLM (Groq)    │  │
                                                 │  └──────────────────┘  │
                                                 └──────────┬─────────────┘
                                                            ▼ SQL
                                                 ┌────────────────────────┐
                                                 │  PostgreSQL Database   │
                                                 └────────────────────────┘
```

For a full schema, the AI pipeline diagram, and per-route documentation see [`ARCHITECTURE.md`](../ARCHITECTURE.md).

---

## 6. Implementation Modules

### 6.1 Authentication
- bcrypt cost-12 hashing on signup; verification on login; JWT with HS256 signature; FastAPI `Depends(get_current_user)` for route gating; `require_admin` for admin gating.

### 6.2 AI Interview Engine
- Curated **67-question bank** (HR, Technical, Behavioral) with company- and role-specific entries for Google, Amazon, Microsoft, TCS, Infosys, Wipro and several roles. Optional Groq LLM produces tailored questions on demand. Session state machine: start → answer → ... → complete → report.

### 6.3 Speech-to-Text (Whisper)
- Browser `MediaRecorder` captures Opus audio; backend `pypdf-free` pipeline saves to a temp file, runs `faster_whisper.transcribe(...)` with `vad_filter=True`, returns transcript + duration. Lazy-load singleton model.

### 6.4 NLP Scoring
- 4 dimensions composed from heuristics + ML signals. Filler-word detection, length sweet-spot, semantic similarity vs sample answer, soft keyword coverage (paraphrase-tolerant), Flesch readability, vocabulary type-token ratio.

### 6.5 Computer Vision
- 1 frame every 2 s, 320×240 JPEG (~30 KB). Backend FaceMesh extracts 468+10 landmarks; head pose from `cv2.solvePnP` on 6 anchors; gaze from iris-vs-corner displacement; smile heuristic from mouth geometry. Aggregated metrics fold into engagement & confidence sub-scores.

### 6.6 Resume Analyzer
- `pypdf` text extraction → 8-section regex detection → 100-skill taxonomy alias matching → optional semantic match against role description → 0-100 score (60% coverage + 20% completeness + 5% sections + ≤15% semantic) → LLM coaching feedback.

### 6.7 Analytics Dashboard
- 6 endpoints feed: stat cards, line trend (overall + 4 dims), bar by interview type, radar (latest vs historical avg), top-weakness bucketizer, side-by-side session compare modal.

### 6.8 Admin Panel
- Paginated user table with promote/demote/delete (cannot self-modify); question CRUD with category/company/role filters; recent activity feed; platform-wide stat cards. Bootstrapped via `ADMIN_EMAILS` env or `python -m app.cli make-admin <email>`.

---

## 7. Tech Stack Summary

| Layer | Technologies |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS, Framer Motion, Recharts, Zustand, TanStack Query, axios |
| Backend  | FastAPI, SQLAlchemy 2, Pydantic v2, python-jose, passlib/bcrypt, loguru |
| Database | PostgreSQL 16 (prod), SQLite (dev/tests) |
| AI / ML  | OpenAI Whisper (faster-whisper), HuggingFace sentence-transformers (`all-MiniLM-L6-v2`), MediaPipe FaceMesh, OpenCV, pypdf, textstat, Groq LLaMA-3 |
| DevOps   | Docker, docker-compose, GitHub Actions, Vercel, Render |

---

## 8. Testing & Quality

- **40 backend tests** (pytest) cover auth, interview lifecycle, admin RBAC, resume analysis, scoring with/without ML, vision aggregation, OpenAPI surface.
- **Frontend** is statically type-checked (`tsc --noEmit`) and built (`next build`) on every push.
- CI: GitHub Actions runs both pipelines on every push/PR.

---

## 9. Limitations & Future Work

| Limitation | Mitigation / Future work |
|---|---|
| Tiny Whisper model (`tiny.en`) makes occasional transcription errors | Switch to `small.en` or `medium.en` in production (config-driven) |
| Vision detector only looks at face; no full-body posture | Add MediaPipe Pose (33 body landmarks) |
| Skill taxonomy is curated — won't recognise niche tools | Augment with embedding-based skill discovery |
| No realtime streaming (responses arrive after each question) | Move to WebSocket-based streaming Whisper + token-by-token LLM |
| Single-user demo focus — no multi-tenant org features | Add organisations + invitation tokens for the placement-cell use case |

---

## 10. Conclusion

The platform demonstrates that a small, free open-source AI stack — Whisper, sentence-transformers, MediaPipe — can be combined into a coherent, deployable mock-interview product with genuine multi-dimensional feedback. Thanks to careful capability-flag fallbacks, the application runs on a developer laptop with zero ML dependencies installed, while still upgrading transparently to full AI when those packages are present. The codebase ships with 40 passing automated tests, a CI pipeline, deployment manifests for both Vercel and Render, and beginner-grade onboarding documentation.
