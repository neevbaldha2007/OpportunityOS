**OpportunityOS**

**Product Requirements Document**

_What we are building, for whom, and how we will know it works_

| **Document** | OpportunityOS_PRD.docx                                                                       |
| ------------ | -------------------------------------------------------------------------------------------- |
| **Product**  | OpportunityOS — AI Career & Opportunity Agent                                                |
| **Tagline**  | Discover opportunities. Understand the gap. Take the next step.                              |
| **Version**  | v1.0 (Hackathon baseline)                                                                    |
| **Date**     | 27 September 2026                                                                            |
| **Team**     | 4 members — Frontend (M1), Backend (M2), AI + SerpApi (M3), Database + Integration + QA (M4) |
| **Status**   | Approved for build                                                                           |

# Contents

1\. Executive Summary

2\. Product Vision

3\. Problem Statement

4\. Problem Background

5\. Target Users

6\. User Personas

7\. User Pain Points

8\. Proposed Solution

9\. Value Proposition

10\. Product Goals

11\. Non-Goals

12\. Core Features

13\. MVP Features

14\. Phase 2 Features

15\. Future Features

16\. Functional Requirements

17\. Non-Functional Requirements

18\. User Stories

19\. User Journey

20\. AI Agent Requirements

21\. SerpApi Requirements

22\. Opportunity Matching

23\. Skill Gap Analysis

24\. Personalized Roadmap

25\. Dashboard

26\. Opportunity Details

27\. Saved Opportunities

28\. Application Tracking

29\. Error Handling

30\. Security

31\. Privacy

32\. Success Metrics

33\. Hackathon Demo Scenario

34\. Future Scope

# 1\. Executive Summary

OpportunityOS is an AI Career & Opportunity Agent for students and freshers. A user describes who they are (education, skills, experience level, location) and where they want to go (target role, career goal, preferred opportunity type). An AI Career Agent then plans search queries, discovers **live** opportunities through **SerpApi** (Google Jobs, Google Search, Google News, optionally YouTube), normalizes and de-duplicates them, scores each against the profile with a **transparent, explainable match percentage**, identifies missing skills, and produces a personalized learning roadmap with concrete next actions.

The product answers three questions a fresher repeatedly asks: **What is out there for me? How far am I from it? What should I do next?** That maps directly to the tagline: Discover opportunities. Understand the gap. Take the next step.

**Design stance.** The match percentage is computed by deterministic Python code, not by the LLM. The LLM plans queries, extracts skills where the dictionary fails, and writes roadmap text. This keeps scores reproducible, auditable, and defensible in front of judges.

| **Dimension**  | **Summary**                                                                                           |
| -------------- | ----------------------------------------------------------------------------------------------------- |
| Users          | Students (final year), recent graduates, early freshers (0–1 yr)                                      |
| Core loop      | Profile → Agent search → Ranked matches → Skill gap → Roadmap → Save / Apply / Track                  |
| Differentiator | Explains every score and converts the gap into a sequenced plan                                       |
| MVP scope      | Auth, profile, agent search (Jobs + Search + News), matching, skill gap, roadmap, save, basic tracker |
| Team / time    | 4 students, 10 days                                                                                   |

# 2\. Product Vision

Become the default first stop for an Indian student deciding what to apply for and what to learn next — a personal opportunity analyst that is honest about fit.

- **Short term (hackathon):** a working, demoable agent that turns a profile into ranked real opportunities with an explained gap and roadmap.
- **Medium term:** continuous monitoring, alerts, resume-aware matching, and progress tracking against the roadmap.
- **Long term:** a career graph linking skills, roles, employers, and learning resources, powering guidance for colleges and placement cells.

# 3\. Problem Statement

Students and freshers cannot efficiently discover relevant opportunities or understand why they do or do not qualify for them. Listings are scattered across job boards, company pages, and news; descriptions are long and inconsistent; and generic advice ("learn more skills") does not tell a student which skill, in which order, for which role.

# 4\. Problem Background

- Opportunity information is fragmented across aggregators, company career pages, and social posts. Students check several sites manually and repeatedly.
- Job descriptions mix required and "nice-to-have" skills without structure, so students either under-apply (self-reject) or over-apply (spray and pray).
- College placement cells cover a limited set of recruiters; off-campus discovery is left to the student.
- Existing job boards rank by recency or sponsorship, not by the student's fit, and do not explain skill gaps.
- Learning platforms recommend courses without linking them to specific live openings the student wants.

Assumption to validate during the hackathon: we have not run user research. Treat pain points below as hypotheses; collect 10–15 quick student responses (Google Form) on Day 1–2 and cite them in the pitch if possible.

# 5\. Target Users

| **Segment**               | **Description**                                                       | **Priority** |
| ------------------------- | --------------------------------------------------------------------- | ------------ |
| Final-year students       | Looking for internships and first full-time roles, on- and off-campus | Primary      |
| Recent graduates (0–1 yr) | Actively job hunting, often after campus placements ended             | Primary      |
| Pre-final-year students   | Looking for internships, hackathons, and learning direction           | Secondary    |
| Career switchers (early)  | Non-CS graduates moving into tech roles                               | Secondary    |
| Placement cells / mentors | Guide batches of students                                             | Future       |

# 6\. User Personas

| **Persona**                                 | **Profile**                                              | **Goal**                                           | **Frustration**                                                                      |
| ------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Riya — Final-year B.Tech (CSE), Ahmedabad   | HTML, CSS, JavaScript, basic Python; one college project | Frontend Developer internship, Ahmedabad or remote | Does not know whether to learn React or Angular first; sees listings she "might" fit |
| Arjun — BCA graduate, Surat                 | Java, SQL, some Spring tutorials                         | Backend Developer full-time role                   | Applied to 60 roles, few responses; unsure what is missing                           |
| Meera — B.Sc. Statistics, Pune              | Excel, Python (pandas), statistics                       | Data Analyst internship                            | Does not know which tools employers actually ask for (SQL? Power BI? Tableau?)       |
| Kabir — Mechanical Engg., switching to tech | Python basics, AutoCAD                                   | Any entry-level software role                      | No clear starting point; overwhelmed by options                                      |

# 7\. User Pain Points

| **#** | **Pain point**                             | **Consequence**                       | **OpportunityOS response**                      |
| ----- | ------------------------------------------ | ------------------------------------- | ----------------------------------------------- |
| P1    | Searching many sites manually              | Hours lost, missed openings           | One agent run searches multiple sources         |
| P2    | Cannot judge fit from long descriptions    | Self-rejection or wasted applications | Explained match % with skill checklist          |
| P3    | Unclear what to learn next                 | Random course hopping                 | Skill gap ranked by demand across matched roles |
| P4    | No link between learning and real openings | Low motivation                        | Roadmap tied to specific saved opportunities    |
| P5    | Losing track of applications               | Missed follow-ups                     | Simple application tracker                      |

# 8\. Proposed Solution

A web app with an AI Career Agent at its core. The agent runs a fixed, tool-based pipeline: understand goal → plan queries → search SerpApi → normalize → de-duplicate → extract skills → score → aggregate gap → generate roadmap → recommend actions. Results are persisted so the dashboard, saved list, roadmap, and tracker work without re-searching.

_Illustrative output format (not a real listing)_

```
Frontend Developer Internship
Ahmedabad / Remote
```

```
Match: 87%
```

```
Skills Match:
✓ HTML
✓ CSS
✓ JavaScript
✗ React
✗ REST API
```

```
Recommended Action:
Learn React → Build project → Learn REST API → Apply
```

# 9\. Value Proposition

| **For**                            | **Value**                                                                                           |
| ---------------------------------- | --------------------------------------------------------------------------------------------------- |
| Students / freshers                | Know where you stand and exactly what to do next, based on real openings rather than generic advice |
| Mentors / placement cells (future) | Batch-level view of skill gaps against live market demand                                           |
| Hackathon judges                   | Visible agentic workflow, real SerpApi data, explainable AI, polished UX                            |

# 10\. Product Goals

1. Deliver a ranked list of real, relevant opportunities within 60 seconds of starting a search.
2. Make every match percentage explainable in one screen (weights + matched/missing skills).
3. Convert the top missing skills into a sequenced roadmap with at least one concrete action per step.
4. Let the user save opportunities and track application status.
5. Ship a stable, deployed demo by Day 10.

# 11\. Non-Goals

- Auto-applying to jobs on the user's behalf.
- Resume parsing or resume generation (Phase 2 / Future).
- Scraping job boards directly; all discovery goes through SerpApi.
- Guaranteeing that a listing is still open — we show source and posted date and link out.
- Mobile native apps (responsive web only).
- Paid courses marketplace or monetization.

# 12\. Core Features

Each major feature below lists description, user value, inputs, outputs, acceptance criteria, and priority.

### F1. Account & Authentication

| **Label**               | **\[MVP\]**                                                                                                                                                                                           |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Description**         | Email + password registration and login with JWT access tokens.                                                                                                                                       |
| **User value**          | Persists profile, searches, saved items, and tracker across sessions.                                                                                                                                 |
| **Inputs**              | Full name, email, password                                                                                                                                                                            |
| **Outputs**             | JWT access token, user object                                                                                                                                                                         |
| **Acceptance criteria** | AC1. Password ≥ 8 chars, hashed with bcrypt<br><br>AC2. Duplicate email returns 409<br><br>AC3. Protected routes reject missing/expired token with 401<br><br>AC4. Token expiry 60 min (configurable) |
| **Priority**            | P0                                                                                                                                                                                                    |

### F2. Profile & Career Goal Setup

| **Label**               | **\[MVP\]**                                                                                                                                                                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Description**         | Multi-step onboarding capturing education, skills (with proficiency), target role, location, experience level, career goal, preferred opportunity types.                                                                                                |
| **User value**          | Gives the agent enough signal to search and score.                                                                                                                                                                                                      |
| **Inputs**              | Education level, degree, field, graduation year, institution (optional), skills\[\], target_role, location, open_to_remote, experience_level, goal_statement, opportunity_types\[\]                                                                     |
| **Outputs**             | Saved UserProfile, UserSkill rows, active CareerGoal                                                                                                                                                                                                    |
| **Acceptance criteria** | AC1. Cannot start agent without target_role, ≥1 skill, location or remote flag<br><br>AC2. Skills selected from catalog via autocomplete; free-text skill allowed and normalized<br><br>AC3. Profile editable later; editing marks last results "stale" |
| **Priority**            | P0                                                                                                                                                                                                                                                      |

### F3. AI Career Agent Search

| **Label**               | **\[MVP\]**                                                                                                                                                                                                                                                                    |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Description**         | Runs the tool-based pipeline and returns ranked opportunities, skill gap, and roadmap in one session.                                                                                                                                                                          |
| **User value**          | One click replaces manual multi-site searching.                                                                                                                                                                                                                                |
| **Inputs**              | Active profile + career goal; optional overrides (location, types)                                                                                                                                                                                                             |
| **Outputs**             | AgentSession with stage log; opportunities with matches; skill gap; roadmap                                                                                                                                                                                                    |
| **Acceptance criteria** | AC1. Completes in ≤ 60 s for 3–6 queries (p90 target)<br><br>AC2. Shows live stage progress in UI<br><br>AC3. If one SerpApi engine fails, returns partial results with a warning instead of failing the whole run<br><br>AC4. Every query executed is logged in SearchHistory |
| **Priority**            | P0                                                                                                                                                                                                                                                                             |

### F4. Opportunity Matching

| **Label**               | **\[MVP\]**                                                                                                                                                                      |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Description**         | Deterministic weighted scoring of each opportunity against the profile.                                                                                                          |
| **User value**          | Students see fit at a glance and can trust the number.                                                                                                                           |
| **Inputs**              | Normalized Opportunity, OpportunitySkill, UserSkill, profile preferences                                                                                                         |
| **Outputs**             | OpportunityMatch with match_score 0–100 and breakdown JSON                                                                                                                       |
| **Acceptance criteria** | AC1. Same inputs always yield the same score<br><br>AC2. Breakdown shows each component and weight<br><br>AC3. Opportunities with no extracted skills are flagged low-confidence |
| **Priority**            | P0                                                                                                                                                                               |

### F5. Skill Gap Analysis

| **Label**               | **\[MVP\]**                                                                                                                                                                            |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Description**         | Aggregates missing skills across the top-N matched opportunities, ranked by demand and impact on score.                                                                                |
| **User value**          | Tells the student which skill to learn first and why.                                                                                                                                  |
| **Inputs**              | OpportunityMatch rows for the session, OpportunitySkill, UserSkill                                                                                                                     |
| **Outputs**             | SkillGap rows: skill, demand_count, demand_pct, avg_score_uplift, priority                                                                                                             |
| **Acceptance criteria** | AC1. Top 5 gaps shown with "appears in X of Y top matches"<br><br>AC2. Priority = high/medium/low from a documented rule<br><br>AC3. Clicking a gap filters opportunities that need it |
| **Priority**            | P0                                                                                                                                                                                     |

### F6. Personalized Roadmap

| **Label**               | **\[MVP\]**                                                                                                                                                                                                                                    |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Description**         | LLM-generated ordered plan for the top missing skills, grounded in the gap data, ending in "Apply" actions for specific saved/top opportunities.                                                                                               |
| **User value**          | Converts analysis into next steps.                                                                                                                                                                                                             |
| **Inputs**              | SkillGap, profile, top opportunities                                                                                                                                                                                                           |
| **Outputs**             | Roadmap with 4–8 RoadmapStep rows (title, type, skill, est. hours, action, resource query)                                                                                                                                                     |
| **Acceptance criteria** | AC1. Every step references a skill from the gap or an application action<br><br>AC2. Estimated effort shown per step<br><br>AC3. User can mark steps done<br><br>AC4. No invented URLs; resources are either SerpApi results or search queries |
| **Priority**            | P0                                                                                                                                                                                                                                             |

### F7. Dashboard

| **Label**               | **\[MVP\]**                                                                                  |
| ----------------------- | -------------------------------------------------------------------------------------------- |
| **Description**         | Home view summarizing target role, top matches, gap bars, roadmap progress, and saved count. |
| **User value**          | Single place to resume work.                                                                 |
| **Inputs**              | Latest completed AgentSession                                                                |
| **Outputs**             | Aggregated dashboard view                                                                    |
| **Acceptance criteria** | AC1. Loads in < 2 s from DB (no live search)<br><br>AC2. Empty state prompts first search    |
| **Priority**            | P0                                                                                           |

### F8. Opportunity Details & Match Explanation

| **Label**               | **\[MVP\]**                                                                                                                     |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Description**         | Detail page with source, company, location, posted date, description extract, skill checklist, score breakdown, and apply link. |
| **User value**          | Decide to apply or learn with full context.                                                                                     |
| **Inputs**              | opportunity_id                                                                                                                  |
| **Outputs**             | Opportunity + OpportunityMatch + related gap skills                                                                             |
| **Acceptance criteria** | AC1. Apply link opens original source in new tab<br><br>AC2. Breakdown components sum to the displayed score (±1 rounding)      |
| **Priority**            | P0                                                                                                                              |

### F9. Saved Opportunities

| **Label**               | **\[MVP\]**                                                                    |
| ----------------------- | ------------------------------------------------------------------------------ |
| **Description**         | Bookmark and list opportunities.                                               |
| **User value**          | Shortlist for applying.                                                        |
| **Inputs**              | opportunity_id                                                                 |
| **Outputs**             | SavedOpportunity                                                               |
| **Acceptance criteria** | AC1. Save/unsave is idempotent<br><br>AC2. Saved list persists across searches |
| **Priority**            | P1                                                                             |

### F10. Application Tracking

| **Label**               | **\[MVP\]**                                                                                       |
| ----------------------- | ------------------------------------------------------------------------------------------------- |
| **Description**         | Kanban-lite tracker with statuses: planned, applied, interviewing, offer, rejected, withdrawn.    |
| **User value**          | Avoid losing track of applications.                                                               |
| **Inputs**              | opportunity_id, status, applied_on, notes                                                         |
| **Outputs**             | Application                                                                                       |
| **Acceptance criteria** | AC1. Status transitions saved with timestamp<br><br>AC2. One application per user per opportunity |
| **Priority**            | P1                                                                                                |

### F11. Search History

| **Label**               | **\[MVP\]**                                                     |
| ----------------------- | --------------------------------------------------------------- |
| **Description**         | List of previous agent sessions and the exact queries executed. |
| **User value**          | Transparency and re-use.                                        |
| **Inputs**              | user                                                            |
| **Outputs**             | SearchHistory grouped by AgentSession                           |
| **Acceptance criteria** | AC1. Shows engine, query, location, result count, cached flag   |
| **Priority**            | P2                                                              |

### F12. Learning Resources via YouTube

| **Label**               | **\[PHASE 2\]**                                                                |
| ----------------------- | ------------------------------------------------------------------------------ |
| **Description**         | Attach top YouTube tutorial results (SerpApi youtube engine) to roadmap steps. |
| **User value**          | Immediate starting material.                                                   |
| **Inputs**              | Roadmap step skill                                                             |
| **Outputs**             | Up to 3 video links per step                                                   |
| **Acceptance criteria** | AC1. Only real SerpApi results shown<br><br>AC2. Feature flag ENABLE_YOUTUBE   |
| **Priority**            | P2 — build only if Day 8 is on track                                           |

# 13\. MVP Features

| **Feature**                                         | **Label**   | **Owner** |
| --------------------------------------------------- | ----------- | --------- |
| F1 Auth (register/login, JWT)                       | **\[MVP\]** | M2        |
| F2 Profile + career goal onboarding                 | **\[MVP\]** | M1 / M2   |
| F3 Agent search: google_jobs + google + google_news | **\[MVP\]** | M3        |
| F4 Deterministic matching                           | **\[MVP\]** | M3        |
| F5 Skill gap                                        | **\[MVP\]** | M3        |
| F6 Roadmap (LLM)                                    | **\[MVP\]** | M3        |
| F7 Dashboard                                        | **\[MVP\]** | M1        |
| F8 Detail + match explanation                       | **\[MVP\]** | M1 / M2   |
| F9 Saved opportunities                              | **\[MVP\]** | M2 / M1   |
| F10 Application tracker (list + status)             | **\[MVP\]** | M2 / M1   |
| F11 Search history                                  | **\[MVP\]** | M2        |

# 14\. Phase 2 Features

- **\[PHASE 2\]** YouTube learning resources on roadmap steps.
- **\[PHASE 2\]** Resume upload (PDF) → skill extraction to pre-fill profile.
- **\[PHASE 2\]** Scheduled re-search with email alerts for new high-match opportunities.
- **\[PHASE 2\]** Drag-and-drop Kanban tracker with reminders.
- **\[PHASE 2\]** Google OAuth sign-in.
- **\[PHASE 2\]** Roadmap progress feeds back into re-scoring ("if you learn React, +12%").

# 15\. Future Features

- **\[FUTURE\]** Placement-cell dashboard: batch-level skill gaps vs market demand.
- **\[FUTURE\]** Mock interview question generation per opportunity.
- **\[FUTURE\]** Hackathon / scholarship / fellowship discovery as first-class types.
- **\[FUTURE\]** Regional language UI (Hindi, Gujarati).
- **\[FUTURE\]** Career graph: skills ↔ roles ↔ employers ↔ resources.
- **\[FUTURE\]** Mobile PWA with push notifications.

# 16\. Functional Requirements

| **ID** | **Requirement**                                                                              | **Label**       |
| ------ | -------------------------------------------------------------------------------------------- | --------------- |
| FR-01  | Users can register and log in with email and password; receive a JWT.                        | **\[MVP\]**     |
| FR-02  | Users can create/update profile, skills (with proficiency 1–5), and one active career goal.  | **\[MVP\]**     |
| FR-03  | System generates 3–6 search queries from the profile via LLM, bounded by a config limit.     | **\[MVP\]**     |
| FR-04  | System queries SerpApi engines google_jobs, google, google_news; youtube behind a flag.      | **\[MVP\]**     |
| FR-05  | System caches SerpApi responses by (engine, q, location, params) for SERP_CACHE_TTL_HOURS.   | **\[MVP\]**     |
| FR-06  | System normalizes all results into the Opportunity schema and de-duplicates via dedupe_hash. | **\[MVP\]**     |
| FR-07  | System extracts skills per opportunity (dictionary match first, LLM fallback for unknowns).  | **\[MVP\]**     |
| FR-08  | System computes match_score with the documented formula and stores the breakdown.            | **\[MVP\]**     |
| FR-09  | System aggregates SkillGap across top N (default 15) matches.                                | **\[MVP\]**     |
| FR-10  | System generates a roadmap of 4–8 steps grounded in the gap.                                 | **\[MVP\]**     |
| FR-11  | Users can list, filter (type, location, min score), and sort opportunities.                  | **\[MVP\]**     |
| FR-12  | Users can save/unsave opportunities and create/update applications.                          | **\[MVP\]**     |
| FR-13  | Users can view search history and past agent sessions.                                       | **\[MVP\]**     |
| FR-14  | News results are shown as "Market signals", never as applyable opportunities.                | **\[MVP\]**     |
| FR-15  | YouTube resources attached to roadmap steps.                                                 | **\[PHASE 2\]** |

# 17\. Non-Functional Requirements

| **Category**    | **Requirement**                                                                         |
| --------------- | --------------------------------------------------------------------------------------- |
| Performance     | Agent run p90 ≤ 60 s; cached run ≤ 15 s; non-agent API p95 ≤ 500 ms                     |
| Availability    | Demo environment up during judging; backend kept warm (free tiers sleep)                |
| Cost            | SerpApi calls per agent run ≤ 6; per-user limit 5 runs/hour, 15 runs/day                |
| Security        | bcrypt hashing, JWT HS256, secrets only in env vars, CORS restricted to frontend origin |
| Privacy         | Minimal PII (name, email); no data sold or shared; delete-account path documented       |
| Accessibility   | WCAG 2.1 AA contrast, keyboard navigation, labels on all inputs                         |
| Responsiveness  | Usable at 360 px, 768 px, 1280 px widths                                                |
| Explainability  | Every score has a visible breakdown; every roadmap step has a reason                    |
| Maintainability | Typed API contracts (Pydantic / TypeScript), Alembic migrations, README setup ≤ 15 min  |

# 18\. User Stories

| **ID** | **As a…** | **I want to…**                           | **So that…**                     | **Label**       |
| ------ | --------- | ---------------------------------------- | -------------------------------- | --------------- |
| US-01  | student   | sign up with email                       | my data is saved                 | **\[MVP\]**     |
| US-02  | student   | enter my skills and target role once     | the agent can search for me      | **\[MVP\]**     |
| US-03  | student   | start a search and see progress          | I know the agent is working      | **\[MVP\]**     |
| US-04  | student   | see opportunities ranked by match %      | I apply where I fit best         | **\[MVP\]**     |
| US-05  | student   | see why a score is 72%                   | I trust the result               | **\[MVP\]**     |
| US-06  | student   | see which skills I am missing most often | I learn the right thing first    | **\[MVP\]**     |
| US-07  | student   | get a step-by-step roadmap               | I know what to do this week      | **\[MVP\]**     |
| US-08  | student   | save opportunities                       | I can apply later                | **\[MVP\]**     |
| US-09  | student   | track application status                 | I follow up on time              | **\[MVP\]**     |
| US-10  | student   | see industry news for my role            | I understand hiring trends       | **\[MVP\]**     |
| US-11  | student   | get tutorial videos per step             | I can start learning immediately | **\[PHASE 2\]** |
| US-12  | student   | upload my resume                         | my profile fills itself          | **\[PHASE 2\]** |

# 19\. User Journey

| **Stage** | **User action**                        | **System response**                                           | **Emotion target** |
| --------- | -------------------------------------- | ------------------------------------------------------------- | ------------------ |
| Discover  | Lands on homepage                      | Clear promise + sample output                                 | Curious            |
| Onboard   | Signs up, 4-step profile               | Autocomplete skills, progress bar                             | In control         |
| Search    | Clicks "Find my opportunities"         | Live agent stages (planning → searching → matching → roadmap) | Anticipation       |
| Evaluate  | Browses ranked cards, opens detail     | Match breakdown, skill checklist                              | Clarity            |
| Plan      | Opens skill gap + roadmap              | Prioritized skills, sequenced steps                           | Direction          |
| Act       | Saves, applies via source link, tracks | Tracker updates                                               | Momentum           |
| Return    | Comes back later                       | Dashboard shows last results + progress                       | Continuity         |

# 20\. AI Agent Requirements

- **Architecture:** tool/function-calling LLM inside a **fixed orchestration plan** (planner → tools in defined order). The LLM does not decide whether to run matching; code does. This is deliberate for demo reliability.
- **Tools exposed:** plan_queries, serp_search, normalize_results, extract_skills, compute_matches, analyze_skill_gap, generate_roadmap.
- **LLM responsibilities:** query planning (JSON), skill extraction fallback (JSON), roadmap writing (JSON). All outputs validated with Pydantic; one retry on invalid JSON, then deterministic fallback.
- **Provider-agnostic:** any LLM with tool/function calling and JSON output (configured via LLM_PROVIDER, LLM_MODEL, LLM_API_KEY). Pick one on Day 1 and do not switch.
- **Guardrails:** max 6 queries, max 2 LLM retries per step, 60 s overall timeout, no URLs generated by the LLM, temperature ≤ 0.3 for extraction.
- **Execution:** POST /agent/search returns 202 with a session_id; the run executes as an in-process background task and the UI polls GET /agent/sessions/{id} for stage progress.
- **Transparency:** each stage logged to AgentSession.stages with timings; surfaced in UI.

# 21\. SerpApi Requirements

| **Engine (SerpApi \`engine\`)** | **Purpose**                                                        | **Key fields used**                                                                                                                                                      | **Label**       |
| ------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| google_jobs                     | Primary source of opportunities                                    | jobs_results\[\]: title, company_name, location, via, description, job_highlights, detected_extensions (posted_at, schedule_type, work_from_home), apply_options, job_id | **\[MVP\]**     |
| google                          | Company career pages, internship programs, hackathons, fellowships | organic_results\[\]: title, link, snippet, source                                                                                                                        | **\[MVP\]**     |
| google_news                     | Hiring trends / market signals for the target role                 | news_results\[\]: title, link, source, date, snippet                                                                                                                     | **\[MVP\]**     |
| youtube                         | Learning resources for roadmap steps                               | video_results\[\]: title, link, channel, length                                                                                                                          | **\[PHASE 2\]** |

- Endpoint: GET <https://serpapi.com/search.json> with engine, q (youtube uses search_query), location, gl=in, hl=en, api_key.
- Google Jobs pagination uses next_page_token; MVP fetches only the first page per query to conserve quota.
- Never display fabricated listings. Demo fallback may only replay **real** responses previously captured into serp_cache and must be labeled "cached".
- Respect SerpApi plan quota; the free plan is small — verify current monthly limits on serpapi.com/pricing before the demo and budget accordingly.
- Google Search results are classified as career_page / program opportunity types and scored with lower confidence because they rarely list skills.

# 22\. Opportunity Matching

The match score is a transparent weighted sum computed in Python. Weights are constants in config.py and displayed in the UI.

_Match formula (identical in TRD and API spec)_

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

| **Component**    | **Rule**                                                                                                               |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------- |
| role_score       | 1.0 if normalized title contains target role tokens; 0.6 if related-role synonym list matches; else 0.2                |
| location_score   | 1.0 exact city match; 1.0 remote when user open_to_remote; 0.6 same state; 0.3 otherwise                               |
| experience_score | 1.0 if title/description has intern/fresher/entry/0-1 years and user level matches; 0.4 if 3+ years required; else 0.7 |
| type_score       | 1.0 if opportunity_type ∈ user opportunity_types; else 0.3                                                             |

# 23\. Skill Gap Analysis

For the top N (default 15) matches of a session, collect skills the opportunity lists that the user does not have.

_Skill gap rule_

```
demand_count   = number of top-N opportunities listing the skill
demand_pct     = demand_count / N
avg_uplift     = mean score increase if the skill were added (recomputed per opportunity)
priority_score = 0.6 × demand_pct + 0.4 × (avg_uplift / max_uplift)
priority       = high (≥ 0.5) | medium (≥ 0.25) | low
```

# 24\. Personalized Roadmap

Input: top 3–5 SkillGap rows, profile, top 3 opportunities. Output: 4–8 ordered steps of type learn, build, apply. Each step has title, description, skill, estimated_hours, action, and a resource_query (a search string, not a fabricated link). Final steps reference real opportunity IDs to apply to.

_Illustrative roadmap shape_

```
1. [learn] React fundamentals (~20 h) — gap in 9/15 top matches
2. [build] Build a React portfolio app consuming a public REST API (~12 h)
3. [learn] REST API basics: fetch, status codes, JSON (~8 h)
4. [apply] Apply to the top 3 saved frontend internships
```

# 25\. Dashboard

- Header: greeting, target role, last search time, "Run new search".
- KPI tiles: opportunities found, best match %, saved count, roadmap progress %.
- Top 6 recommended opportunity cards.
- Skill gap bars (top 5).
- Roadmap preview (next 2 steps).
- Market signals (up to 3 news items).

# 26\. Opportunity Details

- Title, company, location, remote flag, type, source (via), posted date, fetched date.
- Match score ring + breakdown table.
- Skill checklist: matched (✓) and missing (✗), required vs preferred.
- Description extract (highlights first) with "View original" link.
- Actions: Save, Track application, Apply on source.

# 27\. Saved Opportunities

List of SavedOpportunity with score, status badge if tracked, and quick actions (unsave, track). Sorted by saved date; filter by type.

# 28\. Application Tracking

Statuses: planned → applied → interviewing → offer | rejected | withdrawn. MVP: list grouped by status with a status dropdown and notes. Phase 2: drag-and-drop Kanban and reminders.

# 29\. Error Handling

| **Scenario**                  | **User-facing behaviour**                                                                     |
| ----------------------------- | --------------------------------------------------------------------------------------------- |
| SerpApi quota exhausted / 429 | Use cache if available; else show "Search limit reached, try later" and keep previous results |
| One engine fails              | Continue with other engines; warning banner lists skipped sources                             |
| LLM returns invalid JSON      | Retry once; then fall back to template queries / template roadmap                             |
| Zero results                  | Suggest broadening: remote, related roles, fewer filters                                      |
| Agent timeout (> 60 s)        | Return whatever is complete, mark session partial                                             |
| Expired JWT                   | Redirect to login, preserve intended route                                                    |
| Network loss                  | Toast + retry button                                                                          |

# 30\. Security

- Passwords hashed with bcrypt (cost 12); never logged.
- JWT HS256, 60-minute expiry, secret ≥ 32 random bytes in env.
- All user-scoped queries filter by user_id from the token (no IDOR).
- CORS restricted to the deployed frontend origin.
- SerpApi and LLM keys only on backend; never shipped to the browser.
- Rate limits on auth and agent endpoints.
- Input validation via Pydantic; SQL via SQLAlchemy ORM (parameterized).
- External descriptions rendered as plain text (no raw HTML) to prevent XSS.

# 31\. Privacy

- Collect only what matching needs; institution name optional.
- Profile data sent to the LLM excludes email and name.
- Search queries sent to SerpApi contain role, skills, and location only — no personal identifiers.
- Users can delete their account and data (manual script in MVP, endpoint in Phase 2).
- Privacy note on signup: which third parties (LLM provider, SerpApi) receive what.

# 32\. Success Metrics

| **Metric**                   | **Target (hackathon)**                               | **How measured**                |
| ---------------------------- | ---------------------------------------------------- | ------------------------------- |
| Time to first ranked results | ≤ 60 s p90                                           | AgentSession.duration_ms        |
| Relevant results in top 10   | ≥ 7 of 10 judged relevant by team on 5 test profiles | Manual evaluation sheet         |
| Score explainability         | 100% of cards have breakdown                         | UI check                        |
| Onboarding completion        | ≥ 80% of testers finish setup                        | Tester observation (10 testers) |
| SerpApi calls per run        | ≤ 6                                                  | SearchHistory count             |
| Demo success                 | End-to-end flow with no manual intervention          | Dry runs on Day 9 and Day 10    |

# 33\. Hackathon Demo Scenario

1. Open landing page (10 s): problem + promise.
2. Log in as pre-created demo user "Riya" (Final-year B.Tech, HTML/CSS/JS, Ahmedabad, Frontend Developer internship, open to remote).
3. Click "Find my opportunities": narrate agent stages as they appear (planning queries, searching Google Jobs/Search/News, matching, gap, roadmap).
4. Dashboard: point at best match %, skill gap bars (e.g., React appearing in most top matches — actual numbers depend on live data).
5. Open one opportunity: show breakdown adds up; show ✓/✗ skills; open original source.
6. Open roadmap: learn → build → apply steps; mark one step done.
7. Save and track one application.
8. Close with architecture slide and "every number is explainable".

Demo risk control: run the same demo query 30–60 min before judging so responses are in serp_cache (real data). Keep the backend warm. Have a screen recording as last resort.

# 34\. Future Scope

- Institutional edition for colleges (batch analytics).
- Continuous opportunity monitoring and alerts.
- Resume ↔ opportunity tailoring suggestions.
- Verified-skill signals via project/GitHub analysis.
- Partnerships with learning platforms for mapped courses.
- Expansion beyond tech roles (design, finance, core engineering).