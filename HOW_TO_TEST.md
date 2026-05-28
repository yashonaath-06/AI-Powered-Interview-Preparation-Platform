# 🧪 How to Test the Platform — Step by Step

You don't need to know any coding. Follow this exactly. Each section has a 🟢 **expected result** so you know it worked.

---

## ⚡ Easiest path: just text answers (5 min, zero AI installs)

This proves auth, the interview engine, scoring, charts, and the report all work end-to-end. Voice + webcam are optional and covered later.

### 1. Get the latest code

The work so far lives on **6 pull requests** on your GitHub. Make sure you have the latest branch checked out. The simplest is to go to the PR list and **merge them in order** (1 → 2 → 3 → 4 → 5 → 6) into `main`, then clone fresh:

```bash
cd ~/Documents
git clone https://github.com/yashonaath-06/AI-Powered-Interview-Preparation-Platform.git
cd AI-Powered-Interview-Preparation-Platform
```

🟢 You should see folders `backend/`, `frontend/`, and files `README.md`, `docker-compose.yml`, etc.

> **If you haven't merged the PRs yet,** clone the branch directly instead:
> ```bash
> git clone -b feat/phase-10-vision https://github.com/yashonaath-06/AI-Powered-Interview-Preparation-Platform.git
> cd AI-Powered-Interview-Preparation-Platform
> ```

### 2. Start the backend

Open a terminal:

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate            # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

🟢 Last log lines should look like:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ Seeded 67 questions into the question bank.
```

**Verify the API is alive** — open http://localhost:8000/docs in your browser.
🟢 You should see Swagger UI listing every endpoint (auth, interviews, questions, resume, vision, etc.).

### 3. Start the frontend

Open a **second** terminal:

```bash
cd frontend
cp .env.local.example .env.local     # Windows: Copy-Item .env.local.example .env.local
npm install
npm run dev
```

🟢 You should see:
```
- Local:        http://localhost:3000
✓ Ready in 2.1s
```

### 4. Walk through the product

Open http://localhost:3000 in your browser:

| Step | What to do | Expected result |
|---|---|---|
| 1 | You should see the landing page (hero + features + steps + footer) | Animated landing page renders |
| 2 | Click **Get started** | Goes to `/signup` |
| 3 | Sign up — name `Test User`, email `test@x.com`, password `testpass123` | Toast: "Welcome, Test!"  → redirects to `/dashboard` |
| 4 | Dashboard shows three stat cards (all `—`), big purple CTA card, empty "Recent sessions" message | All loaded from real backend |
| 5 | Click **Start interview** | Goes to `/dashboard/interview` (Setup Studio) |
| 6 | Click the **Google** quick preset → click **Start Interview** | Browser navigates to `/dashboard/interview/{id}` |
| 7 | A question appears. Click **Read it aloud** | Browser speaks it via free TTS |
| 8 | At the top right of the answer mode bar, click **Text** (since voice mode is what we test later) | Textarea appears |
| 9 | Type a real answer (50+ words, with relevant keywords for the question) and click **Submit & Next** | Toast: "Scored: X.X/10" — next question loads |
| 10 | Answer the remaining questions (try one with **just** "I dont know" to see the difference) | Score discriminates: substantive answers ≈ 7+, dismissive ones ≈ 3 |
| 11 | After last submission you auto-redirect to the **Report** page | Animated score ring, dimension bars, AI feedback paragraph, per-question accordion |
| 12 | Go back to **Dashboard** | The session appears in the table; stat cards now show real numbers |
| 13 | Click **Logout** in the sidebar, then **Sign in** with the same email | You land back on the dashboard with state preserved |

🟢 **If all 13 steps worked, Phases 1-7 are good.**

### 5. (Optional) Verify the API directly

Open http://localhost:8000/docs and click **Authorize**:
- Click any "POST /api/auth/signup" or login → "Try it out" → fill in data → "Execute"
- For protected endpoints: copy the `access_token` from the login response, click 🔒 **Authorize** at the top, paste `<token>` (no `Bearer ` prefix needed)

🟢 Every endpoint shows real responses with the data you just created.

---

## 🎙️ Optional: enable real voice answers (Phase 8)

This makes the **Voice** mode work — Whisper transcribes what you say.

### 1. Install ffmpeg system-wide

| OS | Command |
|---|---|
| macOS | `brew install ffmpeg` |
| Ubuntu/Debian | `sudo apt install ffmpeg` |
| Windows | Download from https://ffmpeg.org and add it to your PATH |

### 2. Install the heavy ML deps in the backend venv

```bash
cd backend
source .venv/bin/activate           # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements-ml.txt
```

This downloads ~500 MB. Be patient on the first install.

### 3. Restart the backend (Ctrl+C in its terminal, then `uvicorn main:app --reload --port 8000`).

### 4. Test it

1. In the browser, start a new interview and stay in **Voice** mode (the default).
2. Click **Record** → grant microphone permission.
3. Speak your answer for ~20 seconds. Click **Stop**.
4. The button shows "Transcribing..." — Whisper is working.

🟢 After ~3-10 seconds, a **Last transcript** card appears with what you said. The score toast shows your answer's overall score.

🟢 The first time only, the backend logs `Loading Whisper model 'tiny.en' (one-time, may take a moment)…` and downloads ~75 MB.

---

## 📷 Optional: enable webcam analysis (Phase 10)

This activates the live webcam panel above each question — it shows **face detected**, **eye contact**, **head yaw**, **smile %** in real time, and folds the metrics into your engagement score.

If you already installed `requirements-ml.txt` in the previous section, the webcam analysis works automatically on macOS / Windows. On Linux you may need one extra system library:

```bash
# Linux only
sudo apt install -y libgl1 libglib2.0-0
# Amazon Linux / Fedora / RHEL: dnf install -y mesa-libGL
```

Restart the backend, refresh the interview page, click **Allow** on the camera permission dialog.

🟢 You should see a **LIVE** badge over your face preview, and the four signal rows update once every 2 seconds.

🟢 In the report, the per-question accordion now includes vision components like `vision_face_present_pct` and `vision_eye_contact_pct`.

---

## 🧰 Even quicker: run everything with Docker (one command)

If you have Docker Desktop:

```bash
cd AI-Powered-Interview-Preparation-Platform
cp .env.example .env
docker compose up --build
```

🟢 First run takes ~5-10 minutes (downloads images, installs every Python + Node dep, including the ML libraries). After that, just open http://localhost:3000 — voice and webcam work out of the box.

To stop: `Ctrl+C`, then `docker compose down`.

---

## 🐛 Common problems

| Problem | Cause | Fix |
|---|---|---|
| `python3.11: command not found` | Python not installed | Install Python 3.11 from python.org. On Windows tick "Add to PATH" |
| `pip install` fails on `psycopg2` | Postgres dev headers missing | Either run via Docker (Section above) or comment-out the line and use SQLite (default) |
| Frontend says "Network Error" calling backend | CORS or backend not running | Make sure `uvicorn` is running on port 8000 and `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local` |
| "Mic blocked" toast | Browser mic permission | Click 🔒 in the URL bar → Allow microphone, refresh |
| Webcam shows but no signals | Server CV not enabled | Install `requirements-ml.txt` (and `libgl1` on Linux) |
| Whisper takes 10+ seconds the first time | Model is downloading | Just wait once. Subsequent runs are ~1-3 seconds |
| `port 3000/8000 already in use` | Something else has the port | `npx kill-port 3000` or change the port |
| Scores look weird after I changed the code | Old DB has stale schema | `rm backend/interview_prep.db` and restart |

---

## ✅ What you've actually tested

If you completed Section 1 (text-only):
- **Phase 1-2**: Project boots, all docs render, Docker works
- **Phase 3**: Landing, signup, login, dashboard pages all render
- **Phase 4**: All 8 backend routers respond
- **Phase 5**: SQLite DB schema is created, sessions persist
- **Phase 6**: JWT auth — signup, login, logout, token refresh, protected routes
- **Phase 7**: Question bank seeded (67 questions), interview state machine starts → answers → scores → completes → reports

If you also did Section 2 (voice):
- **Phase 8**: Whisper STT transcribes audio in real time
- **Phase 9**: NLP scorer (sentence-transformers + textstat) discriminates good vs. bad answers semantically

If you also did Section 3 (webcam):
- **Phase 10**: MediaPipe FaceMesh analyses webcam frames; engagement + confidence dimensions update with vision data

That's a real, working AI-powered product 🚀

---

## 📍 Where things live (cheat sheet)

| Where | What |
|---|---|
| http://localhost:3000 | Frontend website |
| http://localhost:8000/docs | Interactive API docs (Swagger) |
| http://localhost:8000/api/health | Quick "is the backend up" check |
| `backend/interview_prep.db` | Your local SQLite database (delete to reset) |
| `backend/app/data/question_bank.json` | The 67-question seed file |

Happy testing!
