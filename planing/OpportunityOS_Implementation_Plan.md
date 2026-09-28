**OpportunityOS**

**Implementation Plan**

_10-day build plan for a 4-person team_

| **Document** | OpportunityOS_Implementation_Plan.docx                                                       |
| ------------ | -------------------------------------------------------------------------------------------- |
| **Product**  | OpportunityOS — AI Career & Opportunity Agent                                                |
| **Tagline**  | Discover opportunities. Understand the gap. Take the next step.                              |
| **Version**  | v1.0 (Hackathon baseline)                                                                    |
| **Date**     | 27 September 2026                                                                            |
| **Team**     | 4 members — Frontend (M1), Backend (M2), AI + SerpApi (M3), Database + Integration + QA (M4) |
| **Status**   | Approved for build                                                                           |

# Contents

1\. Team & Ownership

2\. Scope Guardrails

3\. 10-Day Plan

4\. Git Strategy

5\. Branch Naming

6\. Commit Convention

7\. Repository Structure

8\. Environment Setup

9\. .env.example

10\. Testing Strategy

11\. Deployment Checklist

12\. Final Integration Checklist

13\. Hackathon Demo Checklist

# 1\. Team & Ownership

| **Member** | **Role**                    | **Owns**                                                                                                        | **Backup for**           |
| ---------- | --------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------ |
| M1         | Frontend Developer          | React, Tailwind, component library, all screens, responsive design, dashboard                                   | M4 (integration UI bugs) |
| M2         | Backend Developer           | FastAPI, REST APIs, JWT auth, services, validation, error handling, rate limits                                 | M4 (DB models)           |
| M3         | AI + SerpApi Developer      | Agent orchestrator, prompts, SerpApi client, normalizer, skill extraction, matching, skill gap, roadmap         | M2 (agent endpoints)     |
| M4         | Database + Integration + QA | PostgreSQL, Alembic, seeds, CI, deployment, integration testing, Postman collection, documentation, demo script | M1 / M2                  |

Critical path: **M3's agent pipeline**. Everything visible in the demo depends on it. M3 must start SerpApi exploration on Day 1 (not Day 5) and capture real fixtures early so M1/M2 can build against real data shapes.

# 2\. Scope Guardrails

| **In MVP (must ship)**                                                                                                            | **Cut first if behind**                                                                                                               |
| --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Auth, onboarding, agent run with progress, dashboard, results, detail + match explanation, skill gap, roadmap, save, tracker list | YouTube resources, dark mode, drag-and-drop tracker, search history page polish, LLM skill-extraction fallback (keep dictionary only) |

Decision rule: if a task is not done by its day's evening stand-up, the owner flags it and the team decides within 10 minutes to cut, simplify, or swap owners. No silent slippage.

# 3\. 10-Day Plan

Daily rhythm: 10:00 stand-up (15 min), 18:00 integration check (30 min: merge to develop, deploy, smoke test).

## 3.1 Day 1 — Architecture + repository + environment

**Goal:** Everyone can run the skeleton locally; key external risks retired.

| **Task**                                                                                                                                       | **Owner** |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| Finalize documentation read-through; freeze entity and endpoint names                                                                          | All       |
| Create monorepo, branch protection, PR template, issue board (GitHub Projects)                                                                 | M4        |
| Backend skeleton: FastAPI app, config, /health, CORS, error envelope                                                                           | M2        |
| Frontend skeleton: Vite + React + TS + Tailwind + Router + Inter font                                                                          | M1        |
| Choose LLM provider + model; verify tool/function calling and JSON output with a 20-line script                                                | M3        |
| Create SerpApi account; run 1 call each for google_jobs, google, google_news with an Ahmedabad query; save raw JSON to tests/fixtures/serpapi/ | M3        |
| Provision Postgres (Neon/Supabase/Render); create dev DB; share DATABASE_URL via password manager, not chat                                    | M4        |
| Create Render/Railway/Fly backend service and Vercel project connected to repo                                                                 | M4        |

| **Dependencies** | None                                                                                                                            |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Deliverables** | Repo with frontend/ and backend/ running locally; 3 real SerpApi fixtures committed; LLM smoke script; hosting projects created |
| **Testing**      | /health returns 200 locally; npm run dev renders; fixtures load as JSON                                                         |

## 3.2 Day 2 — Database + authentication

**Goal:** Schema migrated; users can register and log in via API.

| **Task**                                                                                   | **Owner**               |
| ------------------------------------------------------------------------------------------ | ----------------------- |
| SQLAlchemy models for all 16 tables; Alembic initial migration matching the reference DDL  | M4                      |
| Seed skills.csv (~250 skills with aliases and categories) + seed script                    | M4 (M3 reviews aliases) |
| POST /auth/register, POST /auth/login, get_current_user, bcrypt, JWT                       | M2                      |
| Rate limiting on auth (slowapi)                                                            | M2                      |
| Auth pages (Login, Signup) with validation; AuthContext; ProtectedRoute; axios interceptor | M1                      |
| SerpApiClient with cache (serp_cache), error mapping, budget check                         | M3                      |
| Deploy skeleton backend + frontend; run migrations on cloud DB                             | M4                      |

| **Dependencies** | Day 1 skeletons, DB provisioned                                                                      |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| **Deliverables** | Migrated schema (local + cloud), working auth API, auth UI, deployed skeleton                        |
| **Testing**      | pytest: register/login/duplicate/invalid password/expired token; manual signup→login on deployed URL |

## 3.3 Day 3 — Frontend foundation

**Goal:** Design system and all static screens exist with mock data typed from the API spec.

| **Task**                                                                                                   | **Owner** |
| ---------------------------------------------------------------------------------------------------------- | --------- |
| Tailwind tokens; components: Button, Card, Badge, Chip, MatchRing, GapBar, Stepper, Toast, Modal, Skeleton | M1        |
| Layouts: public, app (sidebar desktop / bottom tabs mobile)                                                | M1        |
| Onboarding wizard (4 steps) with client state                                                              | M1        |
| src/api/types.ts from the API spec; mock JSON built from real fixtures                                     | M1 + M4   |
| GET/PUT /profile, GET /skills                                                                              | M2        |
| Normalizer for google_jobs, google, google_news using fixtures; dedupe_hash                                | M3        |
| Postman/Bruno collection started; CI: lint + tests on PR (GitHub Actions)                                  | M4        |

| **Dependencies** | Auth done (Day 2)                                                                             |
| ---------------- | --------------------------------------------------------------------------------------------- |
| **Deliverables** | Clickable UI shell for all screens; profile APIs; normalizer with unit tests                  |
| **Testing**      | Vitest on MatchRing/GapBar; pytest normalizer on 3 fixtures; responsive check at 360/768/1280 |

## 3.4 Day 4 — Backend APIs

**Goal:** All non-agent endpoints implemented; API contract frozen at end of day.

| **Task**                                                                                                                           | **Owner** |
| ---------------------------------------------------------------------------------------------------------------------------------- | --------- |
| GET /opportunities, GET /opportunities/{id}, POST/DELETE /opportunities/{id}/save                                                  | M2        |
| GET/POST /applications, PUT /applications/{id}                                                                                     | M2        |
| GET /skill-gap, GET /roadmap, PATCH /roadmap/steps/{id}, GET /search/history (reading from DB)                                     | M2        |
| Seed script: create a demo user + one agent session populated from REAL fixtures through the normalizer (no hand-written listings) | M4 + M3   |
| Skill dictionary extraction (aliases, required vs preferred via highlights)                                                        | M3        |
| Wire onboarding to PUT /profile and GET /skills                                                                                    | M1        |
| **Contract freeze**: OpenAPI exported; changes after this require team approval                                                    | M4        |

| **Dependencies** | Models (Day 2), normalizer (Day 3)                                                 |
| ---------------- | ---------------------------------------------------------------------------------- |
| **Deliverables** | Complete CRUD API surface; seeded demo data from real fixtures; frozen OpenAPI     |
| **Testing**      | pytest per endpoint incl. ownership (user A cannot read user B); Postman run green |

## 3.5 Day 5 — SerpApi integration

**Goal:** Live search works end-to-end from query list to stored opportunities.

| **Task**                                                                                           | **Owner** |
| -------------------------------------------------------------------------------------------------- | --------- |
| Async parallel search (httpx.AsyncClient, max 3 concurrent), per-query logging into search_history | M3        |
| Query templates fallback (role + level + city; remote variant; news query)                         | M3        |
| POST /agent/search (202) + BackgroundTasks runner skeleton + GET /agent/sessions/{id}              | M2        |
| AgentSession stage recording helper (start/finish/warn)                                            | M2 + M3   |
| Agent Processing screen with polling and stage timeline                                            | M1        |
| SerpApi budget dashboard query (live vs cached calls today) for the team                           | M4        |

| **Dependencies** | SerpApiClient (Day 2), normalizer (Day 3), agent endpoints                                      |
| ---------------- | ----------------------------------------------------------------------------------------------- |
| **Deliverables** | Agent run (with template queries) produces opportunities in DB and live progress in UI          |
| **Testing**      | Integration test with fixtures (mock HTTP); one live run per engine; verify cache hit on repeat |

## 3.6 Day 6 — AI Career Agent

**Goal:** LLM planning and tool-based orchestration replace templates.

| **Task**                                                                                            | **Owner** |
| --------------------------------------------------------------------------------------------------- | --------- |
| LLM adapter complete_json with schema validation + 1 retry + timeout                                | M3        |
| plan_queries tool + prompt; fallback to templates on failure                                        | M3        |
| Orchestrator: stage budgets, partial status, startup sweep marking stale running sessions as failed | M3 + M2   |
| LLM skill-extraction fallback (batched) — only if dictionary pipeline is solid                      | M3        |
| Dashboard wired to real endpoints (opportunities, gap, roadmap placeholders)                        | M1        |
| Evaluation sheet: 5 test profiles (frontend, backend, data analyst, Java fresher, non-CS switcher)  | M4        |

| **Dependencies** | Day 5 pipeline                                                                         |
| ---------------- | -------------------------------------------------------------------------------------- |
| **Deliverables** | Agent run with LLM-planned queries; evaluation sheet ready                             |
| **Testing**      | Run 5 profiles; record queries, latency, result counts; malformed-LLM-output unit test |

## 3.7 Day 7 — Matching + skill gap + roadmap

**Goal:** Scores, gaps, and roadmap are correct and explainable.

| **Task**                                                                                                | **Owner** |
| ------------------------------------------------------------------------------------------------------- | --------- |
| scorer.py implementing the documented formula; breakdown JSON; low_confidence flag                      | M3        |
| gap.py (demand, uplift, priority) and roadmap generation (LLM + template fallback + validation)         | M3        |
| Detail page + Match Explanation sheet; Skill Gap page; Roadmap page                                     | M1        |
| Ensure GET endpoints return breakdown, gap, roadmap exactly per spec                                    | M2        |
| Relevance evaluation on 5 profiles: target ≥ 7/10 relevant in top 10; log issues to fix aliases/weights | M4 + M3   |

| **Dependencies** | Agent (Day 6)                                                                                                           |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Deliverables** | Full pipeline output visible in UI                                                                                      |
| **Testing**      | Unit tests: scorer determinism, weights sum = 1, points sum = score ±1, gap ranking; UI check of explanation arithmetic |

_Formula to implement (config.MATCH_WEIGHTS)_

```
match_score = round(100 × (
    0.50 × skill_score        # weighted coverage of opportunity skills
  + 0.15 × role_score         # title similarity to target role
  + 0.15 × location_score     # city match / remote acceptance
  + 0.10 × experience_score   # fresher/intern signals vs user level
  + 0.10 × type_score         # internship / full-time / etc. preference
))
```

```
skill_score = Σ(weight of matched skills) / Σ(weight of all opportunity skills)
              weight: required = 1.0, preferred = 0.5
              if opportunity has 0 extracted skills → skill_score = 0.5 and
              the card shows "Skills not listed — score is less reliable"
```

## 3.8 Day 8 — Frontend/backend integration

**Goal:** Every screen runs on real APIs; no mocks remain.

| **Task**                                                                       | **Owner** |
| ------------------------------------------------------------------------------ | --------- |
| Replace all mocks; loading/empty/error states per Flow spec                    | M1        |
| Saved, Application Tracker, Profile edit + stale banner, Settings, History     | M1        |
| Fix contract mismatches found by M4; performance pass on list endpoints        | M2        |
| Agent latency optimisation to meet ≤ 60 s p90                                  | M3        |
| End-to-end integration test script (register → profile → agent → save → track) | M4        |
| \[PHASE 2 — only if on track\] YouTube resources behind ENABLE_YOUTUBE         | M3        |

| **Dependencies** | Days 4–7                                                        |
| ---------------- | --------------------------------------------------------------- |
| **Deliverables** | Feature-complete MVP on staging                                 |
| **Testing**      | E2E script green on deployed staging; bug list triaged P0/P1/P2 |

## 3.9 Day 9 — Testing + UI polish + deployment

**Goal:** Production deployment stable; P0/P1 bugs fixed.

| **Task**                                                                                     | **Owner** |
| -------------------------------------------------------------------------------------------- | --------- |
| Production deploy: env vars, migrations, seed skills, CORS to Vercel domain                  | M4        |
| UI polish: spacing, empty states, mobile, accessibility pass (keyboard, contrast, aria-live) | M1        |
| Security pass: ownership checks, rate limits, no secrets in logs/responses                   | M2        |
| Warm cache for demo profiles with real searches; confirm SerpApi quota headroom              | M3        |
| Full demo dry run #1 (timed), record backup screen video                                     | All       |
| README final, screenshots, architecture diagram image for slides                             | M4        |

| **Dependencies** | Day 8                                                                                  |
| ---------------- | -------------------------------------------------------------------------------------- |
| **Deliverables** | Production URL, backup video, README                                                   |
| **Testing**      | Regression checklist; 3 fresh-account runs on production; mobile test on 2 real phones |

## 3.10 Day 10 — Final demo + bug fixing + submission

**Goal:** Submit on time with a confident demo.

| **Task**                                                                              | **Owner**              |
| ------------------------------------------------------------------------------------- | ---------------------- |
| Code freeze at noon (only P0 fixes after)                                             | All                    |
| Demo dry runs #2 and #3; tighten narration to time limit                              | All (presenter chosen) |
| Pitch deck: problem, solution, live demo, architecture, explainability, roadmap, team | M4 + M1                |
| Pre-judging: ping /health, re-run demo profile to warm cache, verify quota            | M3 + M4                |
| Submission: repo link, deployed URL, video, docs package, tag v1.0.0                  | M4                     |

| **Dependencies** | Day 9                                                    |
| ---------------- | -------------------------------------------------------- |
| **Deliverables** | Submitted project, tagged release                        |
| **Testing**      | Final smoke test on production 30 minutes before judging |

# 4\. Git Strategy

- Branches: main (production, protected), develop (integration, protected), short-lived feature branches from develop.
- PRs into develop require 1 review + green CI; develop → main merge at the Day 9 release and for hotfixes.
- Squash-merge feature PRs; keep PRs < 400 lines where possible.
- Tag releases: v0.1.0 (Day 5 pipeline), v0.9.0 (Day 9), v1.0.0 (submission).

# 5\. Branch Naming

| **Pattern**                     | **Example**             |
| ------------------------------- | ----------------------- |
| feat/&lt;area&gt;-&lt;short&gt; | feat/agent-plan-queries |
| fix/&lt;area&gt;-&lt;short&gt;  | fix/api-opportunity-404 |
| chore/&lt;short&gt;             | chore/ci-lint           |
| docs/&lt;short&gt;              | docs/readme-setup       |
| test/&lt;short&gt;              | test/scorer-determinism |
| hotfix/&lt;short&gt;            | hotfix/cors-prod        |

# 6\. Commit Convention

Conventional Commits: &lt;type&gt;(&lt;scope&gt;): &lt;summary&gt; — types: feat, fix, docs, style, refactor, test, chore, perf. Scopes: fe, api, auth, agent, serp, match, db, deploy.

_Examples_

```
feat(agent): add plan_queries tool with template fallback
fix(api): enforce ownership on PUT /applications/{id}
test(match): assert breakdown points sum to match_score
chore(deploy): add alembic upgrade to render start command
```

# 7\. Repository Structure

_Monorepo_

```
opportunityos/
├── frontend/                 # React + Vite + TS + Tailwind (see TRD)
├── backend/                  # FastAPI app, alembic, seeds, tests (see API spec)
├── docs/                     # this documentation package
├── postman/                  # API collection + environments
├── scripts/                  # e2e.sh, warm_cache.py, seed_demo.py
├── .github/workflows/ci.yml  # lint + tests on PR
├── .gitignore                # .env, node_modules, __pycache__, .venv
└── README.md
```

# 8\. Environment Setup

_Local setup_

```
# Prerequisites: Git, Node 20 LTS, Python 3.11, a Postgres URL (local Docker or cloud)
```

```
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # fill keys
alembic upgrade head
python -m seeds.load_skills
uvicorn app.main:app --reload --port 8000
```

```
# Frontend
cd frontend
npm install
cp .env.example .env
npm run dev                                             # http://localhost:5173
```

```
# Optional local Postgres
docker run --name oos-pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=opportunityos -p 5432:5432 -d postgres:16
```

_backend/requirements.txt (pin versions on Day 1)_

```
fastapi
uvicorn[standard]
gunicorn
sqlalchemy>=2.0
alembic
psycopg[binary]
pydantic>=2
pydantic-settings
email-validator
pyjwt
bcrypt
httpx
slowapi
pytest
python-dotenv
# + the official SDK of the chosen LLM provider
```

# 9\. .env.example

_.env.example (never commit real values)_

```
# ---------- backend/.env.example ----------
APP_ENV=development
API_PREFIX=
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/opportunityos
JWT_SECRET=replace-with-32+-random-bytes
JWT_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5173
SERPAPI_API_KEY=
SERPAPI_TIMEOUT_SECONDS=20
SERP_CACHE_TTL_HOURS=12
SERP_DAILY_BUDGET=80
ENABLE_YOUTUBE=false
LLM_PROVIDER=
LLM_MODEL=
LLM_API_KEY=
LLM_TEMPERATURE=0.2
AGENT_MAX_QUERIES=6
AGENT_TIMEOUT_SECONDS=60
GAP_TOP_N=15
LOG_LEVEL=INFO
LOG_LLM_PROMPTS=false
```

```
# ---------- frontend/.env.example ----------
VITE_API_BASE_URL=http://localhost:8000
```

# 10\. Testing Strategy

| **Level**         | **Tooling**                                                                 | **Scope**                                                           | **Owner** |
| ----------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------- | --------- |
| Unit (backend)    | pytest                                                                      | scorer, gap, normalizer, dedupe, skill extraction, security helpers | M3 / M2   |
| API               | pytest + TestClient; Postman/Bruno                                          | Every endpoint: success, validation, auth, ownership                | M2 / M4   |
| Agent integration | pytest with mocked httpx using REAL recorded fixtures; mocked LLM responses | Pipeline stages, partial failure, fallbacks                         | M3        |
| Frontend unit     | Vitest + React Testing Library                                              | MatchRing, GapBar, forms validation                                 | M1        |
| E2E               | Scripted API flow (scripts/e2e.sh) + manual UI checklist                    | Register → profile → agent → save → track                           | M4        |
| Relevance         | Evaluation sheet (5 profiles × top 10)                                      | Precision of results and sanity of gaps                             | M4 + M3   |
| Non-functional    | Timed runs, Lighthouse                                                      | Agent p90 ≤ 60 s; LCP; accessibility score                          | M4 / M1   |

Test fixtures must be real SerpApi responses captured by the team. Do not hand-write listings — it hides normalizer bugs and violates the "no fake results" rule.

# 11\. Deployment Checklist

- \[ \] Backend env vars set in host (all keys from .env.example; APP_ENV=production).
- \[ \] alembic upgrade head executed against production DB.
- \[ \] Skills seeded.
- \[ \] Start command uses gunicorn + uvicorn workers bound to \$PORT; health check /health.
- \[ \] CORS_ORIGINS = exact Vercel production URL.
- \[ \] Vercel VITE_API_BASE_URL = backend URL; SPA rewrite configured.
- \[ \] HTTPS works on both; no mixed content.
- \[ \] Logs visible; LOG_LLM_PROMPTS=false.
- \[ \] SerpApi quota checked; SERP_DAILY_BUDGET set.
- \[ \] Backend kept warm before judging (free tiers may sleep).

# 12\. Final Integration Checklist

- \[ \] Every endpoint in the API spec implemented and returns the documented shape.
- \[ \] Entity/table names identical across code and docs.
- \[ \] Agent: completed, partial (one engine disabled), and failed paths tested.
- \[ \] Scores reproducible; breakdown sums to score ±1.
- \[ \] Gap and roadmap reference only real skills/opportunities from the session.
- \[ \] No hard-coded or fabricated listings anywhere in UI or seeds.
- \[ \] Ownership: user A cannot access user B resources (tested).
- \[ \] Loading, empty, and error states present on all 18 screens.
- \[ \] Mobile layout verified.
- \[ \] README setup works on a clean machine in ≤ 15 minutes.

# 13\. Hackathon Demo Checklist

- \[ \] Demo account (Riya profile) created on production; password known to presenter.
- \[ \] Demo search run 30–60 min before judging (real results cached).
- \[ \] /health pinged 5 min before; browser tabs pre-opened (landing, login).
- \[ \] Backup: recorded video + screenshots in deck.
- \[ \] Narration script ≤ time limit; each member knows their segment.
- \[ \] Talking points: live SerpApi data, fixed tool pipeline, deterministic explainable scoring, graceful degradation.
- \[ \] Architecture slide with Mermaid-rendered diagram.
- \[ \] Honest limitations slide: listing freshness depends on source; skill extraction is dictionary-based; free-tier limits.
- \[ \] Stable internet + mobile hotspot backup.