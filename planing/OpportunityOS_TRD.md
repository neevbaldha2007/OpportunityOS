**OpportunityOS**

**Technical Requirements Document**

_How OpportunityOS is built, deployed, and kept reliable_

| **Document** | OpportunityOS_TRD.docx                                                                       |
| ------------ | -------------------------------------------------------------------------------------------- |
| **Product**  | OpportunityOS — AI Career & Opportunity Agent                                                |
| **Tagline**  | Discover opportunities. Understand the gap. Take the next step.                              |
| **Version**  | v1.0 (Hackathon baseline)                                                                    |
| **Date**     | 27 September 2026                                                                            |
| **Team**     | 4 members — Frontend (M1), Backend (M2), AI + SerpApi (M3), Database + Integration + QA (M4) |
| **Status**   | Approved for build                                                                           |

# Contents

1\. Technical Overview

2\. Technology Stack

3\. System Architecture

4\. Frontend Architecture

5\. Backend Architecture

6\. AI Agent Architecture

7\. SerpApi Architecture

8\. Database Architecture

9\. Authentication Architecture

10\. API Architecture

11\. Data Flow

12\. AI Agent Workflow

13\. Search Workflow

14\. Opportunity Matching Workflow

15\. Skill Gap Workflow

16\. Roadmap Generation Workflow

17\. Error Handling

18\. Logging

19\. Security

20\. Rate Limiting

21\. Caching

22\. Performance

23\. Scalability

24\. Deployment

25\. Environment Variables

26\. Third-Party Services

27\. Technical Risks

28\. Technical Trade-offs

# 1\. Technical Overview

OpportunityOS is a three-tier web application: a React single-page app (Vercel), a FastAPI backend (Render, Railway, or Fly.io), and a managed PostgreSQL database. The backend hosts an AI Career Agent that orchestrates an LLM (tool/function calling) and SerpApi, plus a deterministic matching engine. The design optimizes for a 4-person student team shipping in 10 days: few moving parts, no message queue, no vector database, no microservices.

**Key architectural decision:** the agent runs in-process using FastAPI BackgroundTasks. POST /agent/search creates an agent_sessions row, schedules the run, and returns 202 with the session_id; the frontend polls GET /agent/sessions/{id} for real stage progress. This avoids proxy/request timeouts on hosting platforms without adding Redis or a worker. A proper queue (Celery/RQ/Arq + Redis) is deferred to Phase 2. Known limitation: a server restart mid-run loses that run (session is marked failed by a startup sweep).

# 2\. Technology Stack

| **Layer**        | **Choice**                                                | **Notes**                                                     |
| ---------------- | --------------------------------------------------------- | ------------------------------------------------------------- |
| Frontend         | React 18 + Vite + TypeScript                              | TypeScript recommended for API contract safety; JS acceptable |
| Styling          | Tailwind CSS 3                                            | Utility-first; design tokens in tailwind.config               |
| Frontend data    | TanStack Query + Axios                                    | Caching, retries, loading states                              |
| Routing          | React Router v6                                           | Protected routes via auth context                             |
| Charts           | Recharts (optional)                                       | Gap bars can be plain Tailwind divs                           |
| Backend          | Python 3.11 + FastAPI                                     | Uvicorn (dev) / Gunicorn + Uvicorn workers (prod)             |
| Validation       | Pydantic v2                                               | Request/response and LLM output schemas                       |
| ORM / migrations | SQLAlchemy 2.0 + Alembic                                  | Sync engine + psycopg (v3) is sufficient                      |
| Auth             | PyJWT + bcrypt (via passlib or bcrypt package)            | HS256 access tokens                                           |
| HTTP client      | httpx                                                     | Direct calls to serpapi.com/search.json (no SDK dependency)   |
| LLM              | Provider-agnostic adapter (tool/function calling + JSON)  | Choose one provider on Day 1                                  |
| Rate limiting    | slowapi                                                   | Per-user and per-IP limits                                    |
| Database         | PostgreSQL 15+                                            | Neon, Supabase, or Render Postgres                            |
| Testing          | pytest + httpx TestClient; Vitest + React Testing Library | Plus Postman/Bruno collection                                 |
| Deployment       | Vercel (FE), Render/Railway/Fly.io (BE), managed Postgres | GitHub-connected auto deploys                                 |

# 3\. System Architecture

_Mermaid diagram — System Architecture (paste into mermaid.live, GitHub, or Notion to render)_

```
flowchart LR
  U[Student / Fresher<br/>Browser] --> FE[React + Tailwind SPA<br/>Vercel]
  FE -- HTTPS + JWT --> API[FastAPI Backend<br/>Render / Railway / Fly.io]
  API --> AUTH[Auth Module<br/>JWT + bcrypt]
  API --> AG[AI Career Agent<br/>Orchestrator]
  AG --> LLM[LLM Provider<br/>tool / function calling]
  AG --> SERP[SerpApi Client]
  SERP --> SA[(SerpApi<br/>google_jobs / google /<br/>google_news / youtube)]
  AG --> MATCH[Matching Engine<br/>deterministic Python]
  AG --> GAP[Skill Gap + Roadmap]
  API --> DB[(PostgreSQL<br/>Neon / Supabase / Render)]
  AG --> DB
  SERP --> CACHE[(serp_cache table)]
```

| **Component**   | **Responsibility**                                                         |
| --------------- | -------------------------------------------------------------------------- |
| React SPA       | UI, routing, auth token storage, API calls, progress UI                    |
| FastAPI         | REST API, auth, validation, rate limiting, orchestration entrypoint        |
| AI Career Agent | Runs the fixed tool pipeline; records stages                               |
| SerpApi Client  | Builds params, cache lookup, HTTP call, error mapping                      |
| Matching Engine | Pure-Python scoring, gap aggregation                                       |
| LLM Adapter     | Single interface complete_json(prompt, schema, tools) over chosen provider |
| PostgreSQL      | All persistent state including SerpApi cache                               |

# 4\. Frontend Architecture

_Frontend folder structure_

```
frontend/
├── src/
│   ├── api/            # axios instance, endpoint functions, types.ts (mirrors Pydantic)
│   ├── auth/           # AuthContext, ProtectedRoute, token helpers
│   ├── components/     # Button, Card, Badge, MatchRing, SkillChip, GapBar, Toast, Modal
│   ├── features/
│   │   ├── onboarding/ # ProfileStep, GoalStep, SkillsStep, PreferencesStep
│   │   ├── agent/      # AgentRunPage, StageTimeline
│   │   ├── dashboard/
│   │   ├── opportunities/  # List, Card, Detail, MatchExplanation
│   │   ├── skillgap/
│   │   ├── roadmap/
│   │   ├── saved/
│   │   └── applications/
│   ├── pages/          # Landing, Login, Signup, Profile, Settings, NotFound
│   ├── hooks/          # useProfile, useOpportunities, useAgentSearch
│   ├── lib/            # formatters, constants (MATCH_WEIGHTS)
│   ├── App.tsx         # routes
│   └── main.tsx
├── index.html
├── tailwind.config.js
└── vite.config.ts
```

- **State:** server state in TanStack Query; auth in React context; form state local (React Hook Form optional).
- **Token storage:** access token in memory + localStorage for refresh-on-reload (acceptable for hackathon; see Security trade-off).
- **Agent progress:** POST /agent/search returns 202 Accepted with a session_id immediately; the UI then polls GET /agent/sessions/{id} every 1.5 s and renders the real stages array until status is completed, partial, or failed. See AI Agent Workflow.
- **API types:** src/api/types.ts hand-maintained from OpenAPI (/openapi.json); optionally generated with openapi-typescript.

# 5\. Backend Architecture

_Backend folder structure_

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, routers, exception handlers
│   ├── config.py            # pydantic-settings; MATCH_WEIGHTS; limits
│   ├── db.py                # engine, SessionLocal, get_db dependency
│   ├── models/              # SQLAlchemy models (one file per aggregate)
│   ├── schemas/             # Pydantic request/response models
│   ├── api/
│   │   ├── deps.py          # get_current_user
│   │   └── routes/          # auth.py, profile.py, skills.py, agent.py,
│   │                        # opportunities.py, skill_gap.py, roadmap.py,
│   │                        # applications.py, search_history.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── profile_service.py
│   │   └── opportunity_service.py
│   ├── agent/
│   │   ├── orchestrator.py  # run_agent(session, user)
│   │   ├── tools.py         # tool implementations + JSON schemas
│   │   ├── prompts.py
│   │   └── llm.py           # provider adapter
│   ├── search/
│   │   ├── serpapi_client.py
│   │   ├── normalizer.py
│   │   └── dedupe.py
│   ├── matching/
│   │   ├── skills.py        # dictionary extraction, synonyms
│   │   ├── scorer.py        # match formula
│   │   ├── gap.py
│   │   └── roadmap.py
│   └── core/                # security.py (JWT, hashing), errors.py, logging.py, ratelimit.py
├── alembic/
├── seeds/skills.csv         # ~250 canonical skills + aliases
├── tests/
└── requirements.txt
```

- Routes are thin; business logic lives in services/agent/matching (unit-testable without HTTP).
- A request-scoped DB session via dependency injection.
- Global exception handler converts AppError(code, message, status) into the standard error format.

# 6\. AI Agent Architecture

The agent is an **orchestrated tool pipeline** rather than an open-ended autonomous loop. The LLM is invoked with function/tool schemas at three points; everything else is code. This gives agentic behaviour (planning, tool selection of engines/queries, structured reasoning) with predictable latency and cost.

| **Tool**          | **Type**            | **Input**                                                  | **Output**                                             |
| ----------------- | ------------------- | ---------------------------------------------------------- | ------------------------------------------------------ |
| plan_queries      | LLM                 | profile summary, career goal, allowed engines, max_queries | \[{engine, q, location, purpose}\]                     |
| serp_search       | Code                | engine, q, location                                        | raw JSON + cached flag                                 |
| normalize_results | Code                | raw JSON, engine                                           | Opportunity\[\] (unsaved)                              |
| extract_skills    | Code + LLM fallback | opportunity text                                           | \[{skill_id\|name, requirement: required\|preferred}\] |
| compute_matches   | Code                | opportunities, user skills, profile                        | OpportunityMatch\[\]                                   |
| analyze_skill_gap | Code                | matches (top N)                                            | SkillGap\[\]                                           |
| generate_roadmap  | LLM                 | gap, profile, top opportunities                            | Roadmap + RoadmapStep\[\]                              |

_Tool schema: plan_queries_

```
{
  "name": "plan_queries",
  "description": "Plan SerpApi searches for a student's career goal.",
  "parameters": {
    "type": "object",
    "properties": {
      "queries": {
        "type": "array", "maxItems": 6,
        "items": {
          "type": "object",
          "properties": {
            "engine":   {"type": "string", "enum": ["google_jobs", "google", "google_news"]},
            "q":        {"type": "string", "maxLength": 120},
            "location": {"type": "string"},
            "purpose":  {"type": "string", "enum": ["jobs", "programs", "market_signal"]}
          },
          "required": ["engine", "q", "purpose"]
        }
      }
    },
    "required": ["queries"]
  }
}
```

_Prompt skeleton: query planner_

```
SYSTEM: You plan job-search queries for Indian students and freshers.
Return ONLY a call to plan_queries. Rules:
- 2-3 google_jobs queries (role + level + city; one remote variant if open_to_remote)
- 1-2 google queries for internship programs / career pages (no site: operators to job boards)
- 1 google_news query about hiring trends for the role in India
- Never include the user's name, email, or institution.
USER: {"target_role":"Frontend Developer","level":"fresher","types":["internship"],
       "location":"Ahmedabad, Gujarat, India","remote":true,
       "skills":["HTML","CSS","JavaScript"]}
```

# 7\. SerpApi Architecture

| **Parameter** | **google_jobs**                              | **google**                    | **google_news** | **youtube \[PHASE 2\]** |
| ------------- | -------------------------------------------- | ----------------------------- | --------------- | ----------------------- |
| engine        | google_jobs                                  | google                        | google_news     | youtube                 |
| query param   | q                                            | q                             | q               | search_query            |
| location      | location (e.g., "Ahmedabad, Gujarat, India") | location                      | n/a (use gl)    | n/a                     |
| gl / hl       | in / en                                      | in / en                       | in / en         | gl=in, hl=en            |
| Pagination    | next_page_token (MVP: first page only)       | start / num (MVP: first page) | first page      | first page              |
| Results key   | jobs_results                                 | organic_results               | news_results    | video_results           |

- All calls go through SerpApiClient.search(engine, params) which: builds a canonical param dict (sorted, api_key excluded), computes cache_key = sha256(json), checks serp_cache, calls SerpApi with a 20 s timeout, and stores the raw response.
- Error mapping: HTTP 401 → SERPAPI_AUTH, 429 or "run out of searches" message → SERPAPI_QUOTA, timeout → SERPAPI_TIMEOUT, JSON with error key → SERPAPI_ERROR.
- Concurrency: queries for one session executed with asyncio.gather (httpx.AsyncClient), bounded to 3 concurrent.
- Field names follow SerpApi's documented JSON; normalizer must use .get() defensively since fields vary per listing.

_Mermaid diagram — SerpApi Search Flow (paste into mermaid.live, GitHub, or Notion to render)_

```
sequenceDiagram
  participant AG as Agent
  participant SC as SerpApi Client
  participant DB as serp_cache
  participant SA as SerpApi
  AG->>SC: search(engine, q, location, params)
  SC->>DB: lookup cache_key (sha256)
  alt fresh cache hit (< TTL)
    DB-->>SC: raw_json
  else miss or expired
    SC->>SA: GET https://serpapi.com/search.json
    SA-->>SC: JSON (jobs_results / organic_results / news_results / video_results)
    SC->>DB: upsert raw_json, fetched_at
  end
  SC-->>AG: raw results + metadata
  AG->>AG: normalize → Opportunity[]
```

_Normalization mapping_

```
# Normalization map (google_jobs → Opportunity)
title            ← job.title
company_name     ← job.company_name
location         ← job.location
is_remote        ← job.detected_extensions.work_from_home (bool) OR "remote" in location/title
schedule_type    ← job.detected_extensions.schedule_type
posted_at_text   ← job.detected_extensions.posted_at      (e.g. "3 days ago"; kept as text)
source_via       ← job.via
description      ← job.description (truncated to 8,000 chars)
highlights       ← job.job_highlights (JSON)
apply_url        ← job.apply_options[0].link  (fallback: job.share_link / related_links[0].link)
external_id      ← job.job_id
opportunity_type ← infer from title/schedule_type: internship | full_time | part_time | contract
```

```
# google organic_results → Opportunity (type = career_page | program)
title ← r.title, apply_url ← r.link, description ← r.snippet, source_via ← r.source or domain
```

```
# google_news news_results → NOT an Opportunity; stored as market signal in agent_sessions.result_summary.news
```

# 8\. Database Architecture

Single PostgreSQL schema, UUID primary keys (gen_random_uuid() via pgcrypto), timestamptz everywhere, JSONB for semi-structured payloads (breakdowns, highlights, stages). Opportunities are global and shared across users (deduplicated); user-specific scoring lives in opportunity_matches.

| **Entity**       | **Table**           | **Purpose**                                                 |
| ---------------- | ------------------- | ----------------------------------------------------------- |
| User             | users               | Account and credentials                                     |
| UserProfile      | user_profiles       | Education, location, experience level, preferences          |
| Skill            | skills              | Canonical skill catalog (taxonomy)                          |
| UserSkill        | user_skills         | Skills a user claims, with self-rated proficiency           |
| CareerGoal       | career_goals        | Target role, goal statement, preferred opportunity types    |
| Opportunity      | opportunities       | Normalized, de-duplicated opportunity from SerpApi          |
| OpportunitySkill | opportunity_skills  | Skills extracted from an opportunity (required / preferred) |
| OpportunityMatch | opportunity_matches | Per-user match score + transparent breakdown (added)        |
| SavedOpportunity | saved_opportunities | User bookmarks                                              |
| Application      | applications        | Application tracker entries and status                      |
| SearchHistory    | search_history      | Each executed SerpApi query and its result count            |
| SkillGap         | skill_gaps          | Missing skills with priority, per agent session             |
| Roadmap          | roadmaps            | Personalized learning roadmap header                        |
| RoadmapStep      | roadmap_steps       | Ordered steps inside a roadmap                              |
| AgentSession     | agent_sessions      | One AI Career Agent run: status, stages, timings            |
| SerpCache        | serp_cache          | Cached raw SerpApi responses to protect quota (added)       |

_Mermaid diagram — Database Architecture (ER) (paste into mermaid.live, GitHub, or Notion to render)_

```
erDiagram
  users ||--|| user_profiles : has
  users ||--o{ user_skills : claims
  skills ||--o{ user_skills : referenced_by
  users ||--o{ career_goals : sets
  opportunities ||--o{ opportunity_skills : requires
  skills ||--o{ opportunity_skills : referenced_by
  users ||--o{ opportunity_matches : receives
  opportunities ||--o{ opportunity_matches : scored_in
  agent_sessions ||--o{ opportunity_matches : produced
  users ||--o{ saved_opportunities : saves
  opportunities ||--o{ saved_opportunities : saved_as
  users ||--o{ applications : tracks
  opportunities ||--o{ applications : applied_to
  users ||--o{ agent_sessions : runs
  career_goals ||--o{ agent_sessions : drives
  agent_sessions ||--o{ search_history : executes
  agent_sessions ||--o{ skill_gaps : yields
  skills ||--o{ skill_gaps : missing
  agent_sessions ||--|| roadmaps : generates
  roadmaps ||--o{ roadmap_steps : contains
  skills ||--o{ roadmap_steps : teaches
```

Full column-level definitions are in OpportunityOS_Backend_Schema_API.docx (the source of truth for DDL).

# 9\. Authentication Architecture

- Register: validate → bcrypt hash → insert users → issue JWT.
- Login: fetch by lower(email) → bcrypt verify → issue JWT; constant-time failure response.
- JWT claims: sub (user UUID), email, iat, exp, type: "access". HS256 with JWT_SECRET.
- Dependency get_current_user decodes, verifies expiry, loads user, rejects inactive users.
- Refresh tokens: **\[PHASE 2\]**. MVP uses 60-minute tokens and re-login.

# 10\. API Architecture

REST over JSON, versionless for the hackathon (prefix /api optional via API_PREFIX). OpenAPI docs at /docs. All list endpoints paginate with page and page_size (max 50).

| **Method** | **Path**                 | **Auth** | **Purpose**                                            | **Status** |
| ---------- | ------------------------ | -------- | ------------------------------------------------------ | ---------- |
| POST       | /auth/register           | Public   | Create account, return JWT                             | Core       |
| POST       | /auth/login              | Public   | Authenticate, return JWT                               | Core       |
| GET        | /profile                 | JWT      | Get profile, skills and career goal                    | Core       |
| PUT        | /profile                 | JWT      | Create/update profile, skills and career goal          | Core       |
| GET        | /skills                  | JWT      | Search the skill catalog (autocomplete)                | Added      |
| POST       | /agent/search            | JWT      | Run the AI Career Agent end-to-end                     | Core       |
| GET        | /agent/sessions/{id}     | JWT      | Fetch a past or running agent session                  | Added      |
| GET        | /opportunities           | JWT      | List matched opportunities (filters, sort, pagination) | Core       |
| GET        | /opportunities/{id}      | JWT      | Opportunity detail + match explanation                 | Core       |
| POST       | /opportunities/{id}/save | JWT      | Save opportunity                                       | Core       |
| DELETE     | /opportunities/{id}/save | JWT      | Unsave opportunity                                     | Core       |
| GET        | /skill-gap               | JWT      | Aggregated missing skills for latest session           | Core       |
| GET        | /roadmap                 | JWT      | Personalized roadmap for latest session                | Core       |
| PATCH      | /roadmap/steps/{id}      | JWT      | Mark a roadmap step done / not done                    | Added      |
| GET        | /applications            | JWT      | List tracked applications                              | Added      |
| POST       | /applications            | JWT      | Start tracking an application                          | Core       |
| PUT        | /applications/{id}       | JWT      | Update application status / notes                      | Core       |
| GET        | /search/history          | JWT      | List previous agent searches and queries               | Core       |

"Added" endpoints were not in the original brief but are required for the screens to work (skill autocomplete, tracker list, session retrieval). They are documented identically in the API specification.

# 11\. Data Flow

1. User completes onboarding → PUT /profile writes user_profiles, user_skills, career_goals.
2. POST /agent/search creates agent_sessions (status queued), returns 202, and schedules the run; the run sets running.
3. Planner LLM returns queries → each query logged to search_history.
4. SerpApi client returns raw JSON (cache or live) → serp_cache.
5. Normalizer upserts opportunities by dedupe_hash; skill extraction writes opportunity_skills.
6. Scorer writes opportunity_matches (user, opportunity, session).
7. Gap aggregator writes skill_gaps; roadmap LLM writes roadmaps + roadmap_steps.
8. Session marked completed (or partial); polling client receives the result summary and navigates to the dashboard.
9. Subsequent GETs (/opportunities, /skill-gap, /roadmap) read the latest completed session.

# 12\. AI Agent Workflow

_Mermaid diagram — AI Agent Workflow (paste into mermaid.live, GitHub, or Notion to render)_

```
flowchart TD
  A[POST /agent/search] --> C[Create AgentSession status=queued<br/>return 202 + session_id]
  C --> B[BackgroundTask: load UserProfile, UserSkill, CareerGoal<br/>status=running]
  B --> D[LLM tool: plan_queries<br/>3-6 queries across engines]
  D --> E[Tool: serp_search per query<br/>cache first]
  E --> F[Normalize to Opportunity schema]
  F --> G[De-duplicate via dedupe_hash]
  G --> H[Tool: extract_skills<br/>dictionary first, LLM fallback]
  H --> I[Deterministic match scoring]
  I --> J[Aggregate SkillGap]
  J --> K[LLM tool: generate_roadmap]
  K --> L[Persist + AgentSession status=completed]
  L --> M[Client polling GET /agent/sessions/id<br/>receives result_summary]
  E -. SerpApi error .-> X[Partial results + warning]
  X --> F
```

| **Stage key**    | **Budget**   | **Failure policy**                                                      |
| ---------------- | ------------ | ----------------------------------------------------------------------- |
| plan_queries     | ≤ 8 s        | Retry once → template queries from role/location                        |
| search           | ≤ 25 s total | Per-query failure tolerated; fail session only if all fail and no cache |
| normalize_dedupe | ≤ 2 s        | Skip malformed items                                                    |
| extract_skills   | ≤ 10 s       | Dictionary only if LLM fails                                            |
| match            | ≤ 1 s        | Must not fail (pure code)                                               |
| skill_gap        | ≤ 1 s        | Must not fail                                                           |
| roadmap          | ≤ 12 s       | Retry once → template roadmap from top gaps                             |

# 13\. Search Workflow

1. Build queries from planner output; enforce max 6 and dedupe identical (engine, q, location).
2. Check per-user daily run limit and global SERP_DAILY_BUDGET.
3. For each query: cache lookup → live call if needed → record search_history (engine, q, location, result_count, cached, latency_ms, error_code).
4. Collect results; engines that failed are listed in session.warnings.
5. Pass all raw results to the normalizer.

# 14\. Opportunity Matching Workflow

_Mermaid diagram — Opportunity Matching Flow (paste into mermaid.live, GitHub, or Notion to render)_

```
flowchart TD
  A[Normalized Opportunity] --> B{Skills extracted?}
  B -- yes --> C[Compare with UserSkill set<br/>via canonical skill_id]
  B -- no --> C2[skill_score = 0.5<br/>low-confidence flag]
  C --> D[skill_score]
  A --> E[role_score: token overlap<br/>title vs target role]
  A --> F[location_score: city / remote]
  A --> G[experience_score: fresher signals]
  A --> H[type_score: preferred type]
  D & C2 & E & F & G & H --> I[Weighted sum → match_score 0-100]
  I --> J[Store OpportunityMatch with breakdown JSON]
  J --> K[Rank: score desc, posted_at desc]
```

_Formula_

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

_De-duplication key_

```
def dedupe_hash(title, company, location):
    norm = lambda s: re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()
    return sha256(f"{norm(title)}|{norm(company)}|{norm(location)}".encode()).hexdigest()
```

- Skill extraction: tokenize description + highlights; match against skills.name and skills.aliases (e.g., "ReactJS", "React.js" → React). Phrases under a "Qualifications" highlight are required; under "Benefits"/"nice to have" → preferred.
- LLM fallback only when dictionary finds &lt; 2 skills and description &gt; 300 chars; batched 5 opportunities per call.
- Unknown skills returned by the LLM are inserted into skills with is_verified = false.

# 15\. Skill Gap Workflow

1. Select top N (config GAP_TOP_N = 15) matches of the session by score.
2. For each, missing = opportunity_skills − user_skills.
3. Aggregate per skill: demand_count, demand_pct, avg_uplift (re-score opportunity with skill added).
4. priority_score = 0.6 × demand_pct + 0.4 × normalized uplift; bucket high/medium/low.
5. Persist top 10 to skill_gaps with rank.

# 16\. Roadmap Generation Workflow

1. Input: top 3–5 skill_gaps, user level, weekly_hours (profile, default 10), top 3 opportunities (id, title, company).
2. LLM returns JSON: {title, summary, total_weeks, steps:\[{order, step_type, title, description, skill_name, estimated_hours, action, resource_query, opportunity_id?}\]}.
3. Validate: 4–8 steps; every learn/build step references a gap skill; apply steps reference provided opportunity IDs only; no URLs in text.
4. Persist roadmap + steps; mark previous roadmap for the user is_active = false.

# 17\. Error Handling

_Standard error envelope (all endpoints)_

```
{
  "error": {
    "code": "SERPAPI_QUOTA",
    "message": "Search limit reached. Showing your last results.",
    "details": {"engine": "google_jobs"},
    "request_id": "8f1c2a0e-..."
  }
}
```

| **Code**           | **HTTP** | **Meaning**                                           |
| ------------------ | -------- | ----------------------------------------------------- |
| VALIDATION_ERROR   | 422      | Pydantic validation failed                            |
| UNAUTHORIZED       | 401      | Missing/invalid/expired token                         |
| FORBIDDEN          | 403      | Resource not owned by user                            |
| NOT_FOUND          | 404      | Entity missing                                        |
| CONFLICT           | 409      | Duplicate email / duplicate application               |
| RATE_LIMITED       | 429      | Per-user or per-IP limit exceeded                     |
| PROFILE_INCOMPLETE | 400      | Agent run without required profile fields             |
| SERPAPI_QUOTA      | 503      | Quota exhausted and no cache                          |
| SERPAPI_ERROR      | 502      | Upstream error                                        |
| LLM_ERROR          | 502      | LLM failed after retry and no fallback                |
| AGENT_TIMEOUT      | 504      | Exceeded AGENT_TIMEOUT_SECONDS with nothing to return |
| INTERNAL_ERROR     | 500      | Unhandled                                             |

# 18\. Logging

- Structured JSON logs (python logging + a JSON formatter) with request_id, user_id, route, latency_ms.
- Agent logs per stage: session_id, stage, duration_ms, status, counts.
- Never log passwords, JWTs, API keys, or full LLM prompts containing profile data in production (LOG_LLM_PROMPTS=false).
- Platform log viewer (Render/Railway/Fly) is sufficient for MVP.

# 19\. Security

- OWASP basics: parameterized queries (ORM), output encoding in React (no dangerouslySetInnerHTML for descriptions), CORS allowlist.
- Ownership checks in every service function (WHERE user_id = :current_user).
- Secrets via environment variables; .env git-ignored; .env.example committed.
- HTTPS enforced by hosting providers.
- Prompt-injection hygiene: job descriptions are data; the extraction prompt instructs the model to ignore instructions inside descriptions and outputs are schema-validated.
- Dependency pinning in requirements.txt and package-lock.json.

# 20\. Rate Limiting

| **Endpoint**            | **Limit**                                   | **Key**                   |
| ----------------------- | ------------------------------------------- | ------------------------- |
| POST /auth/login        | 10 / minute                                 | IP                        |
| POST /auth/register     | 5 / minute                                  | IP                        |
| POST /agent/search      | 5 / hour and 15 / day                       | user_id                   |
| All other authenticated | 120 / minute                                | user_id                   |
| Global SerpApi budget   | SERP_DAILY_BUDGET (e.g., 80 live calls/day) | server-wide counter in DB |

# 21\. Caching

- serp_cache table: cache_key, engine, params JSONB, raw_json JSONB, result_count, fetched_at, expires_at. TTL SERP_CACHE_TTL_HOURS (default 12).
- Cache is shared across users: two students searching the same role + city reuse one SerpApi call.
- LLM skill extraction results are cached implicitly via opportunity_skills (extract once per opportunity).
- Frontend: TanStack Query staleTime 60 s for lists; dashboard invalidated after an agent run.
- Pre-demo warm-up: run demo profiles before judging to populate cache with real results.

# 22\. Performance

- Parallel SerpApi calls (max 3 concurrent) — biggest latency win.
- Batch LLM skill extraction (5 opportunities per call) and skip it when dictionary is sufficient.
- Indexes: opportunities(dedupe_hash) unique, opportunity_matches(user_id, agent_session_id, match_score desc), search_history(user_id, created_at desc), serp_cache(cache_key) unique.
- Descriptions truncated to 8,000 chars before storage and 3,000 chars before LLM.
- List endpoints return card-sized payloads; detail endpoint returns full description.

# 23\. Scalability

Hackathon load is tens of users. The design scales to low thousands by adding: (1) a durable job queue so agent runs survive restarts and scale across machines, (2) a Redis cache in front of serp_cache, (3) read replicas are unnecessary before ~10k DAU. The first real bottleneck is SerpApi cost per run, not compute — shared caching and scheduled batch searches per (role, city) are the scaling lever.

# 24\. Deployment

| **Component** | **Target**                               | **Notes**                                                                                             |
| ------------- | ---------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Frontend      | Vercel                                   | Env: VITE_API_BASE_URL; SPA rewrites to index.html                                                    |
| Backend       | Render Web Service (or Railway / Fly.io) | Start: gunicorn -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:\$PORT; health check /health |
| Database      | Neon / Supabase / Render Postgres        | Run alembic upgrade head on deploy; seed skills once                                                  |
| Secrets       | Platform env settings                    | Never in repo                                                                                         |

Free tiers of some backend hosts sleep after inactivity and take a while to wake. Ping /health before the demo, or use a paid/always-on instance for judging day. Verify the free-tier behaviour of whichever host you pick on Day 1.

# 25\. Environment Variables

_.env.example_

```
# backend/.env.example
APP_ENV=development
API_PREFIX=
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/opportunityos
JWT_SECRET=change-me-32-bytes-min
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
# frontend/.env.example
VITE_API_BASE_URL=http://localhost:8000
```

# 26\. Third-Party Services

| **Service**                       | **Use**                                | **Risk**                             | **Mitigation**                              |
| --------------------------------- | -------------------------------------- | ------------------------------------ | ------------------------------------------- |
| SerpApi                           | Live search data                       | Quota / cost, response shape changes | Cache, budget counter, defensive normalizer |
| LLM provider                      | Planning, extraction fallback, roadmap | Latency, invalid JSON, cost          | Timeouts, schema validation, templates      |
| Vercel                            | Frontend hosting                       | Low                                  | —                                           |
| Render / Railway / Fly.io         | Backend hosting                        | Cold starts, request limits          | Warm-up, keep runs < 60 s                   |
| Neon / Supabase / Render Postgres | Database                               | Connection limits on free tiers      | Small pool (pool_size=5), pool_pre_ping     |

# 27\. Technical Risks

| **Risk**                              | **Likelihood** | **Impact** | **Mitigation**                                                           | **Owner** |
| ------------------------------------- | -------------- | ---------- | ------------------------------------------------------------------------ | --------- |
| SerpApi quota exhausted before demo   | High           | High       | Budget counter, cache, dev uses cached fixtures captured from real calls | M3        |
| Skill extraction noisy → wrong scores | Medium         | High       | Curated alias dictionary; manual eval on 5 profiles                      | M3        |
| Agent latency > 60 s                  | Medium         | Medium     | Parallel search, batch extraction, stage budgets                         | M3        |
| Frontend/backend contract drift       | Medium         | Medium     | Freeze schemas Day 4; shared types.ts; Postman collection                | M4        |
| Deployment surprises on Day 9         | Medium         | High       | Deploy skeleton on Day 2 and continuously                                | M4        |
| Google Jobs sparse for small cities   | Medium         | Medium     | Add state-level and remote queries                                       | M3        |

# 28\. Technical Trade-offs

| **Decision**   | **Chosen**                           | **Rejected**                         | **Why**                                               |
| -------------- | ------------------------------------ | ------------------------------------ | ----------------------------------------------------- |
| Agent style    | Fixed tool pipeline                  | Autonomous ReAct loop                | Predictable latency/cost; easier to debug and demo    |
| Scoring        | Deterministic Python                 | LLM-assigned %                       | Reproducible and explainable                          |
| Execution      | In-process BackgroundTasks + polling | Synchronous request / queue + worker | Real progress, no request timeouts, no extra services |
| Skill matching | Alias dictionary + LLM fallback      | Embeddings / vector DB               | No extra infra; good enough for top ~250 skills       |
| Token storage  | localStorage                         | httpOnly cookie + refresh            | Simpler cross-origin setup; revisit in Phase 2        |
| Cache          | Postgres table                       | Redis                                | One less service                                      |
| SerpApi access | Raw HTTP via httpx                   | SDK                                  | Transparent params, async, no package ambiguity       |