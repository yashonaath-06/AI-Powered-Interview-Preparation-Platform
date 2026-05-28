# 🎓 Viva Q&A Prep — AI-Powered Interview Preparation Platform

> 30 questions an examination panel is likely to ask, with crisp answers you can rehearse. Grouped by theme.

---

## A. Conceptual Foundations

**Q1. What problem does your project solve?**
> Students preparing for placements lack a 24/7 mock-interview environment that gives objective, multi-dimensional feedback. Live mocks need a peer; coaching institutes are expensive; existing online tools test only trivia. My platform combines AI components into a single browser experience that fills that gap.

**Q2. Why a full-stack approach instead of a desktop app?**
> Web is the lowest-friction install path (zero install for the user), enables responsive design, and lets us deploy a single instance to thousands of students. The backend keeps the heavy ML dependencies off the client.

**Q3. Who are the target users?**
> Engineering students, MBA students, freshers, job seekers and career-coaching institutes. The admin panel makes it usable for institutes that want to curate their own question bank.

---

## B. Architecture & Tech Choices

**Q4. Why FastAPI for the backend?**
> Three reasons: (1) it auto-generates Swagger / OpenAPI docs which makes the API self-documenting; (2) async request handling out of the box for I/O-bound AI work; (3) Pydantic gives us strict request/response validation with very little code.

**Q5. Why Next.js + Tailwind on the frontend?**
> Next.js gives me the App Router for clean route nesting, server components for landing-page SEO, and Vercel-native deployment. Tailwind keeps styles co-located with markup and removes the need for a separate CSS pipeline.

**Q6. Why SQLAlchemy 2.0 with typed `Mapped[...]` columns?**
> The 2.0-style API gives me static type checking on every column and relationship, which catches schema mistakes at IDE time rather than runtime.

**Q7. Why JWT instead of session cookies?**
> JWTs are stateless — the backend doesn't need to store sessions, and the same token works across multiple instances behind a load balancer. The trade-off is that you can't easily invalidate tokens, but for a 60-minute access window that's acceptable.

---

## C. AI Modules

**Q8. Why Whisper, and why faster-whisper specifically?**
> Whisper is the state-of-the-art open-source STT model. The `faster-whisper` runtime uses CTranslate2 to give 4× speedup on CPU with the same accuracy. Importantly, it runs locally — the audio never leaves the user's server, which is privacy-friendly.

**Q9. How does the NLP scorer work?**
> An answer is scored across 4 dimensions: technical, communication, confidence, engagement. Each is a weighted blend of heuristics (length, filler-word penalty) and ML signals (sentence-transformer cosine similarity vs. the sample answer, soft keyword coverage that's paraphrase-tolerant, Flesch reading-ease, vocabulary diversity).

**Q10. What is "semantic similarity" here?**
> Each piece of text is encoded into a 384-dimensional vector by the `all-MiniLM-L6-v2` sentence-transformer. The cosine of the angle between two vectors is the similarity, in [0, 1]. Two paraphrases of the same answer cluster close; an off-topic answer scores low.

**Q11. Walk me through the computer-vision pipeline.**
> Browser captures one 320×240 JPEG every 2 s. Backend MediaPipe FaceMesh produces 468 + 10 iris landmarks. From those: head pose via `cv2.solvePnP` on 6 anchors gives yaw/pitch/roll; gaze direction from iris position relative to eye-corner midpoints; smile score from mouth-corner upward curvature. The per-frame metrics are aggregated per question and fed back into the engagement and confidence sub-scores.

**Q12. How are the dimension weights chosen?**
> Empirically, with sanity tests in `tests/test_scoring.py`. They verify ordering: a substantive technical answer must beat a dismissive one; an answer dense with filler words must score lower on confidence than the same content without fillers. The weights make those orderings hold.

**Q13. What if the LLM API key is not configured?**
> Every AI service follows the *capability-flag* pattern: it tries to load its dependency at import time, sets `is_available()` accordingly, and the caller falls back to a deterministic baseline. The platform stays usable without LLM, Whisper, sentence-transformers, or MediaPipe.

---

## D. Database & Models

**Q14. Walk me through your schema.**
> Five tables: `users` (auth), `questions` (bank), `interview_sessions` (with `planned_question_ids` JSON), `answers` (joins session + question, stores `nlp_scores` and `vision_scores` as JSON), `resumes` (parsed text + analysis JSON). Foreign keys cascade on delete.

**Q15. Why store JSON blobs in `nlp_scores` and `vision_scores` instead of normalizing?**
> The set of sub-scores evolves between phases (e.g. Phase 9 added `semantic_similarity`, Phase 10 added `vision_engagement`). Storing them as JSON keeps the schema stable while letting the scorer add new components without migrations.

**Q16. How would you handle concurrent users?**
> The FastAPI app is stateless apart from the DB. Two strategies: (1) horizontal scaling — run multiple Uvicorn workers behind a load balancer, share a Postgres instance; (2) for ML model loading, the lazy singleton avoids loading the model in every worker — we'd switch to a pre-fork worker model where models load once and copy-on-write.

---

## E. Security

**Q17. How are passwords stored?**
> bcrypt with cost factor 12. The hash is salted, slow, and irreversible. Even if the DB leaks, brute-forcing one password takes years.

**Q18. How do you prevent unauthorized access to admin routes?**
> Two layers: (1) `Depends(get_current_user)` resolves the JWT to a user record; (2) `Depends(require_admin)` 403s if `user.role != "admin"`. The frontend additionally has a client-side guard that redirects non-admins to `/dashboard`.

**Q19. What about SQL injection / XSS?**
> All DB queries go through SQLAlchemy with parameterised statements — no raw SQL anywhere. React escapes HTML by default; we never use `dangerouslySetInnerHTML`. CORS is restricted to known frontend origins.

**Q20. Can a user access another user's session?**
> No. Every interview / resume route loads the row by ID and asserts `row.user_id == current_user.id`, otherwise 404 (we don't even confirm the row exists). There's an automated test for this exact scenario.

---

## F. Engineering Practice

**Q21. How is the code tested?**
> 40 pytest tests covering auth, interview lifecycle, admin RBAC, resume analysis, scoring. Each test gets a fresh SQLite via FastAPI `dependency_overrides`. Frontend is type-checked + production-built on every CI run.

**Q22. What CI/CD do you have?**
> GitHub Actions runs the pytest suite and `next build` on every push and PR to `main`. Failed builds block merging. Render auto-deploys the backend on every merge to main; Vercel does the same for the frontend.

**Q23. How is this deployed?**
> Two services on free tiers: Render hosts the FastAPI app + managed Postgres (`render.yaml` blueprint provisions both with one click); Vercel hosts the Next.js frontend. CORS is restricted to the Vercel URL. Total cost: $0.

**Q24. How do you handle ML model size for deployment?**
> Whisper `tiny.en` is 75 MB; sentence-transformer is 80 MB; MediaPipe ships its own model. Together, less than 250 MB which fits Render's 1 GB build. For paid tiers we'd switch to `small.en` Whisper for higher accuracy.

---

## G. Edge Cases & Trade-offs

**Q25. What happens if the user's mic is muted?**
> Whisper returns an empty transcript. The endpoint returns 422 with the message *"Whisper produced an empty transcript — your microphone may have been muted, or the answer was inaudible. Please try again."* The frontend shows a toast with the same message; the candidate stays on the same question.

**Q26. What if MediaPipe finds no face?**
> The per-frame metrics endpoint returns `face_detected: false`. The frontend's live signal panel shows "Face: Missing" in amber. The session-level aggregate counts those frames against `face_present_pct`, which lowers the engagement score.

**Q27. What if the LLM produces JSON that doesn't parse?**
> The `llm_service.chat_json()` wrapper catches the parse error, logs a warning, and returns `None`. The caller falls back to its non-LLM path (e.g. random sampling from the curated bank).

**Q28. What if Whisper transcribes a non-English answer?**
> Currently we set `language="en"` for speed. To support multilingual interviews we'd remove that hint and pick a multilingual sentence-transformer model.

**Q29. How do you stop people gaming the scorer?**
> The scorer combines four uncorrelated signals (semantic, fluency, length, vision). Maximising any one is hard without tanking another. A long answer dense with keywords still loses on filler-word penalty if read with hesitation, and vision catches you if you stare at notes.

**Q30. Why didn't you use deepfake detection / advanced emotion classifiers?**
> Both add 200-500 MB of model weight for marginal demo value at this scope. The current vision pipeline is interpretable (head pose, eye contact) which is exactly what users want feedback on. Adding DeepFace was prototyped but rejected for this trade-off.
