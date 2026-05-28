# 🏛️ System Architecture

This document explains *how* the AI Interview Platform is designed, why each piece exists, and how data flows from a user's microphone all the way to a final score.

---

## 1. High-Level Architecture

```
┌────────────────────────┐         HTTPS / JSON         ┌────────────────────────┐
│      BROWSER           │ ◄──────────────────────────► │   FastAPI Backend      │
│   (Next.js + React)    │                              │   (Python)             │
│                        │      WebSocket (audio/       │                        │
│  • Landing page        │       video frame stream)    │  ┌──────────────────┐  │
│  • Auth pages          │ ◄──────────────────────────► │  │  Auth Router     │  │
│  • Interview Studio    │                              │  │  Interview Router│  │
│  • Dashboard / Charts  │                              │  │  Resume Router   │  │
│  • Resume Analyzer     │                              │  │  Admin Router    │  │
│  • Admin Panel         │                              │  └──────────────────┘  │
└────────────────────────┘                              │  ┌──────────────────┐  │
                                                        │  │  AI SERVICES     │  │
                                                        │  │  • Whisper STT   │  │
                                                        │  │  • NLP Scorer    │  │
                                                        │  │  • CV Analyzer   │  │
                                                        │  │  • Resume AI     │  │
                                                        │  │  • LLM Q-Gen     │  │
                                                        │  └──────────────────┘  │
                                                        └──────────┬─────────────┘
                                                                   │ SQL
                                                                   ▼
                                                        ┌────────────────────────┐
                                                        │  PostgreSQL Database   │
                                                        └────────────────────────┘
```

---

## 2. End-to-End Interview Flow

```
1. User clicks "Start Interview"  ──►  POST /interviews
                                       creates a session row in DB
                                       returns session_id + first question

2. Frontend speaks the question (browser SpeechSynthesis)
   Frontend turns ON webcam + mic

3. Every 1 second:
   • snapshot of webcam frame  ──►  POST /interviews/{id}/vision
                                    (face / emotion / pose analysis)

4. When user finishes answering:
   • audio blob   ──►  POST /interviews/{id}/answer
                       Whisper transcribes
                       NLP evaluates content
                       Vision aggregates session-so-far metrics
                       returns score + next question

5. After last question:
   • GET /interviews/{id}/report
     returns final scores + AI-written feedback
```

---

## 3. Database Schema (overview)

```
users                    interview_sessions             questions
─────                    ──────────────────             ─────────
id (PK)                  id (PK)                        id (PK)
email (unique)           user_id (FK → users)           text
hashed_password          company                        category   (HR/Tech/Behavioral)
full_name                role                           difficulty
role  (user/admin)       interview_type                 company    (nullable)
created_at               status                         role       (nullable)
                         started_at                     expected_keywords (JSON)
                         ended_at
                         overall_score
                         scores_json   (per-dim)

answers                                                  resumes
───────                                                  ───────
id (PK)                                                  id (PK)
session_id (FK)                                          user_id (FK)
question_id (FK)                                         filename
transcript                                               raw_text
duration_seconds                                         parsed_skills (JSON)
nlp_scores  (JSON)                                       target_role
vision_scores (JSON)                                     match_score
combined_score                                           ai_feedback
created_at                                               created_at
```

---

## 4. AI Pipeline

### 4a. Question Generation
1. If `GROQ_API_KEY` is set → call LLaMA-3 with prompt
   *"Generate 8 X-style interview questions for a Y role at company Z."*
2. Otherwise → load curated **`backend/app/data/question_bank.json`** and filter.

### 4b. Speech-to-Text (Whisper)
- Accept WebM/Opus audio blob
- Decode with `ffmpeg` → 16-kHz mono WAV
- Whisper `base` model → transcript

### 4c. NLP Evaluation
| Sub-score | Library | Method |
|---|---|---|
| Technical accuracy | `sentence-transformers` | cosine similarity vs. expected answer |
| Grammar | `language_tool_python` | error count → score |
| Fluency | regex + WPM | filler words + words/min |
| Confidence | acoustic features + hedging words | composite |
| Communication clarity | combination | weighted average |

### 4d. Computer Vision Analysis
| Signal | Library | What it measures |
|---|---|---|
| Face presence | MediaPipe FaceDetection | "Was your face on screen?" |
| Emotion | DeepFace | happy / neutral / nervous / sad |
| Eye contact | MediaPipe FaceMesh (iris landmarks) | gaze direction vs. camera |
| Head pose | MediaPipe FaceMesh | yaw / pitch — head turning away |
| Posture | MediaPipe Pose | shoulder line, slouching |
| Engagement | composite | aggregated signal |

### 4e. Final Report
- Each per-question vector is averaged.
- LLM (Groq/OpenAI) is given the JSON of scores and asked to write a
  *human-friendly* paragraph of strengths, weaknesses, study tips.
- Stored on the session row.

---

## 5. Security

- Passwords hashed with **bcrypt** (cost 12).
- JWTs signed with HS256, `JWT_SECRET` from env.
- All `/api/*` routes (except `/auth/*`) require `Authorization: Bearer <token>`.
- Admin routes additionally check `user.role == "admin"`.
- CORS limited to `CORS_ORIGINS` env list.
- File uploads scanned for size & extension; resumes stored outside web root.

---

## 6. Deployment Topology

```
                      ┌────────────────┐
                      │   Vercel       │  (Next.js static + edge)
                      │   frontend     │
                      └───────┬────────┘
                              │ HTTPS
                              ▼
                      ┌────────────────┐
                      │   Render.com   │  (FastAPI container)
                      │   backend      │
                      └───────┬────────┘
                              │
                              ▼
                      ┌────────────────┐
                      │  Render Postgres│
                      └────────────────┘
```

Both services have free tiers sufficient for a college demo.

---

## 7. Build Phases (Roadmap)

| Phase | Deliverable |
|---|---|
| 1 | Architecture & tech selection ✅ |
| 2 | Folder structure & setup guide ✅ |
| 3 | Frontend foundation |
| 4 | Backend foundation |
| 5 | Database & migrations |
| 6 | Authentication |
| 7 | AI interview engine |
| 8 | Speech-to-text |
| 9 | NLP evaluation |
| 10 | Computer vision |
| 11 | Analytics dashboard |
| 12 | Admin panel |
| 13 | Resume analyzer |
| 14 | Testing |
| 15 | Deployment |
| 16-20 | Docs, PPT, viva, resume bullets |
