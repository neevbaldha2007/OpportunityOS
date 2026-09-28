**OpportunityOS**

**Backend Database & API Specification**

_FastAPI + PostgreSQL — schema, endpoints, contracts_

| **Document** | OpportunityOS_Backend_Schema_API.docx                                                        |
| ------------ | -------------------------------------------------------------------------------------------- |
| **Product**  | OpportunityOS — AI Career & Opportunity Agent                                                |
| **Tagline**  | Discover opportunities. Understand the gap. Take the next step.                              |
| **Version**  | v1.0 (Hackathon baseline)                                                                    |
| **Date**     | 27 September 2026                                                                            |
| **Team**     | 4 members — Frontend (M1), Backend (M2), AI + SerpApi (M3), Database + Integration + QA (M4) |
| **Status**   | Approved for build                                                                           |

# Contents

1\. Overview

2\. Database Design

3\. ER Diagram

4\. Reference DDL

5\. API Conventions

6\. Error Format

7\. API Reference

8\. JWT Authentication Flow

9\. Validation

10\. Rate Limiting

11\. Security

12\. API Folder Structure

# 1\. Overview

Source of truth for the PostgreSQL schema and REST API of OpportunityOS. Stack: **FastAPI + PostgreSQL** (SQLAlchemy 2.0, Alembic, Pydantic v2). All IDs are UUIDs; all timestamps are ISO-8601 UTC. Field names in JSON are snake_case and match column names wherever possible.

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

**Schema changes vs. brief:** added OpportunityMatch (user-specific scores kept separate from shared, de-duplicated opportunities) and SerpCache (quota protection). Opportunities are global so that two users searching the same role do not duplicate rows or SerpApi calls.

# 2\. Database Design

Conventions: plural snake_case table names; id UUID DEFAULT gen_random_uuid(); created_at/updated_at TIMESTAMPTZ; enumerations implemented as VARCHAR + CHECK (easier Alembic migrations than native ENUM); JSONB for flexible payloads; arrays (TEXT\[\], UUID\[\]) for small denormalized lists read together.

## 2.1 User — users

Registered accounts.

| **Column**    | **Data type** | **Req.** | **Default**       | **Key** | **Constraints** | **Description**                         |
| ------------- | ------------- | -------- | ----------------- | ------- | --------------- | --------------------------------------- |
| id            | UUID          | Yes      | gen_random_uuid() | PK      | —               | Primary key                             |
| email         | VARCHAR(255)  | Yes      | —                 | —       | UNIQUE          | Stored lower-case                       |
| password_hash | VARCHAR(255)  | Yes      | —                 | —       | —               | bcrypt hash                             |
| full_name     | VARCHAR(120)  | Yes      | —                 | —       | —               | Display name                            |
| is_active     | BOOLEAN       | Yes      | true              | —       | —               | Soft disable                            |
| last_login_at | TIMESTAMPTZ   | No       | —                 | —       | —               | Last successful login                   |
| created_at    | TIMESTAMPTZ   | Yes      | now()             | —       | —               | Creation time                           |
| updated_at    | TIMESTAMPTZ   | Yes      | now()             | —       | —               | Last update time (set by app on update) |

## 2.2 UserProfile — user_profiles

One profile per user.

| **Column**            | **Data type** | **Req.** | **Default**       | **Key**       | **Constraints**                                                                          | **Description**                         |
| --------------------- | ------------- | -------- | ----------------- | ------------- | ---------------------------------------------------------------------------------------- | --------------------------------------- |
| id                    | UUID          | Yes      | gen_random_uuid() | PK            | —                                                                                        | Primary key                             |
| user_id               | UUID          | Yes      | —                 | FK → users.id | ON DELETE CASCADE                                                                        | Owner (unique: 1:1)                     |
| education_level       | VARCHAR(30)   | Yes      | —                 | —             | CHECK (education_level IN ('high_school','diploma','bachelors','masters','phd','other')) | Highest/current level                   |
| degree                | VARCHAR(120)  | No       | —                 | —             | —                                                                                        | e.g., B.Tech                            |
| field_of_study        | VARCHAR(120)  | No       | —                 | —             | —                                                                                        | e.g., Computer Science                  |
| graduation_year       | SMALLINT      | No       | —                 | —             | CHECK (graduation_year BETWEEN 1990 AND 2040)                                            | Expected/actual                         |
| institution           | VARCHAR(200)  | No       | —                 | —             | —                                                                                        | Optional; never sent to LLM/SerpApi     |
| experience_level      | VARCHAR(20)   | Yes      | 'student'         | —             | CHECK (experience_level IN ('student','fresher','0_1_years','1_2_years'))                | Used in experience_score                |
| location_city         | VARCHAR(100)  | No       | —                 | —             | —                                                                                        | e.g., Ahmedabad                         |
| location_state        | VARCHAR(100)  | No       | —                 | —             | —                                                                                        | e.g., Gujarat                           |
| location_country      | VARCHAR(2)    | Yes      | 'IN'              | —             | —                                                                                        | ISO-2                                   |
| open_to_remote        | BOOLEAN       | Yes      | true              | —             | —                                                                                        | Remote acceptance                       |
| weekly_learning_hours | SMALLINT      | Yes      | 10                | —             | CHECK (weekly_learning_hours BETWEEN 1 AND 60)                                           | Roadmap pacing                          |
| created_at            | TIMESTAMPTZ   | Yes      | now()             | —             | —                                                                                        | Creation time                           |
| updated_at            | TIMESTAMPTZ   | Yes      | now()             | —             | —                                                                                        | Last update time (set by app on update) |

Table constraints: UNIQUE (user_id)

## 2.3 Skill — skills

Canonical skill catalog seeded from seeds/skills.csv; unverified skills can be added by extraction.

| **Column**  | **Data type** | **Req.** | **Default**       | **Key** | **Constraints** | **Description**                              |
| ----------- | ------------- | -------- | ----------------- | ------- | --------------- | -------------------------------------------- |
| id          | UUID          | Yes      | gen_random_uuid() | PK      | —               | Primary key                                  |
| name        | VARCHAR(80)   | Yes      | —                 | —       | UNIQUE          | Canonical name, e.g., React                  |
| slug        | VARCHAR(80)   | Yes      | —                 | —       | UNIQUE          | e.g., react                                  |
| category    | VARCHAR(40)   | No       | —                 | —       | —               | frontend, backend, data, devops, soft, tool… |
| aliases     | TEXT\[\]      | Yes      | '{}'              | —       | —               | e.g., {reactjs, react.js}                    |
| is_verified | BOOLEAN       | Yes      | true              | —       | —               | false if created by LLM extraction           |
| created_at  | TIMESTAMPTZ   | Yes      | now()             | —       | —               | Creation time                                |

## 2.4 UserSkill — user_skills

Skills claimed by a user.

| **Column**  | **Data type** | **Req.** | **Default**       | **Key**        | **Constraints**                     | **Description**    |
| ----------- | ------------- | -------- | ----------------- | -------------- | ----------------------------------- | ------------------ |
| id          | UUID          | Yes      | gen_random_uuid() | PK             | —                                   | Primary key        |
| user_id     | UUID          | Yes      | —                 | FK → users.id  | ON DELETE CASCADE                   |                    |
| skill_id    | UUID          | Yes      | —                 | FK → skills.id | ON DELETE RESTRICT                  |                    |
| proficiency | SMALLINT      | Yes      | 2                 | —              | CHECK (proficiency BETWEEN 1 AND 5) | 1 Aware … 5 Expert |
| created_at  | TIMESTAMPTZ   | Yes      | now()             | —              | —                                   | Creation time      |

Table constraints: UNIQUE (user_id, skill_id)

## 2.5 CareerGoal — career_goals

Career goals; exactly one active per user (partial unique index).

| **Column**        | **Data type** | **Req.** | **Default**       | **Key**       | **Constraints**                       | **Description**                                      |
| ----------------- | ------------- | -------- | ----------------- | ------------- | ------------------------------------- | ---------------------------------------------------- |
| id                | UUID          | Yes      | gen_random_uuid() | PK            | —                                     | Primary key                                          |
| user_id           | UUID          | Yes      | —                 | FK → users.id | ON DELETE CASCADE                     |                                                      |
| target_role       | VARCHAR(120)  | Yes      | —                 | —             | —                                     | e.g., Frontend Developer                             |
| goal_statement    | VARCHAR(280)  | No       | —                 | —             | —                                     | Free text                                            |
| timeline_months   | SMALLINT      | Yes      | 3                 | —             | CHECK (timeline_months IN (1,3,6,12)) | Planning horizon                                     |
| opportunity_types | TEXT\[\]      | Yes      | '{internship}'    | —             | —                                     | Subset of internship, full_time, part_time, contract |
| is_active         | BOOLEAN       | Yes      | true              | —             | —                                     | Active goal flag                                     |
| created_at        | TIMESTAMPTZ   | Yes      | now()             | —             | —                                     | Creation time                                        |
| updated_at        | TIMESTAMPTZ   | Yes      | now()             | —             | —                                     | Last update time (set by app on update)              |

## 2.6 Opportunity — opportunities

Global, de-duplicated opportunities normalized from SerpApi results.

| **Column**       | **Data type** | **Req.** | **Default**       | **Key** | **Constraints**                                                                                                 | **Description**                                    |
| ---------------- | ------------- | -------- | ----------------- | ------- | --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| id               | UUID          | Yes      | gen_random_uuid() | PK      | —                                                                                                               | Primary key                                        |
| dedupe_hash      | CHAR(64)      | Yes      | —                 | —       | UNIQUE                                                                                                          | sha256(norm(title)\|norm(company)\|norm(location)) |
| source_engine    | VARCHAR(20)   | Yes      | —                 | —       | CHECK (source_engine IN ('google_jobs','google'))                                                               | SerpApi engine that produced it                    |
| external_id      | TEXT          | No       | —                 | —       | —                                                                                                               | job_id for google_jobs                             |
| title            | VARCHAR(300)  | Yes      | —                 | —       | —                                                                                                               | Listing title                                      |
| company_name     | VARCHAR(200)  | No       | —                 | —       | —                                                                                                               | Employer                                           |
| location         | VARCHAR(200)  | No       | —                 | —       | —                                                                                                               | As provided by source                              |
| is_remote        | BOOLEAN       | Yes      | false             | —       | —                                                                                                               | Detected remote                                    |
| opportunity_type | VARCHAR(20)   | Yes      | 'unknown'         | —       | CHECK (opportunity_type IN ('internship','full_time','part_time','contract','career_page','program','unknown')) | Inferred type                                      |
| schedule_type    | VARCHAR(50)   | No       | —                 | —       | —                                                                                                               | Raw schedule_type                                  |
| description      | TEXT          | No       | —                 | —       | —                                                                                                               | Truncated to 8,000 chars                           |
| highlights       | JSONB         | No       | —                 | —       | —                                                                                                               | job_highlights from source                         |
| source_via       | VARCHAR(200)  | No       | —                 | —       | —                                                                                                               | e.g., "via LinkedIn" / domain                      |
| apply_url        | TEXT          | No       | —                 | —       | —                                                                                                               | Link to original listing                           |
| posted_at_text   | VARCHAR(50)   | No       | —                 | —       | —                                                                                                               | e.g., "3 days ago" (relative, as provided)         |
| first_seen_at    | TIMESTAMPTZ   | Yes      | now()             | —       | —                                                                                                               | First fetch                                        |
| last_seen_at     | TIMESTAMPTZ   | Yes      | now()             | —       | —                                                                                                               | Most recent fetch                                  |
| raw              | JSONB         | No       | —                 | —       | —                                                                                                               | Original item for debugging                        |
| created_at       | TIMESTAMPTZ   | Yes      | now()             | —       | —                                                                                                               | Creation time                                      |

## 2.7 OpportunitySkill — opportunity_skills

Skills extracted per opportunity.

| **Column**        | **Data type** | **Req.** | **Default**       | **Key**               | **Constraints**                                   | **Description**  |
| ----------------- | ------------- | -------- | ----------------- | --------------------- | ------------------------------------------------- | ---------------- |
| id                | UUID          | Yes      | gen_random_uuid() | PK                    | —                                                 | Primary key      |
| opportunity_id    | UUID          | Yes      | —                 | FK → opportunities.id | ON DELETE CASCADE                                 |                  |
| skill_id          | UUID          | Yes      | —                 | FK → skills.id        | ON DELETE RESTRICT                                |                  |
| requirement       | VARCHAR(10)   | Yes      | 'required'        | —                     | CHECK (requirement IN ('required','preferred'))   | Weight 1.0 / 0.5 |
| extraction_method | VARCHAR(12)   | Yes      | 'dictionary'      | —                     | CHECK (extraction_method IN ('dictionary','llm')) | Provenance       |
| created_at        | TIMESTAMPTZ   | Yes      | now()             | —                     | —                                                 | Creation time    |

Table constraints: UNIQUE (opportunity_id, skill_id)

## 2.8 OpportunityMatch — opportunity_matches

Per-user, per-session score. Added to keep global opportunities separate from user-specific scoring.

| **Column**        | **Data type** | **Req.** | **Default**       | **Key**                | **Constraints**                       | **Description**                                             |
| ----------------- | ------------- | -------- | ----------------- | ---------------------- | ------------------------------------- | ----------------------------------------------------------- |
| id                | UUID          | Yes      | gen_random_uuid() | PK                     | —                                     | Primary key                                                 |
| user_id           | UUID          | Yes      | —                 | FK → users.id          | ON DELETE CASCADE                     |                                                             |
| opportunity_id    | UUID          | Yes      | —                 | FK → opportunities.id  | ON DELETE CASCADE                     |                                                             |
| agent_session_id  | UUID          | Yes      | —                 | FK → agent_sessions.id | ON DELETE CASCADE                     |                                                             |
| match_score       | SMALLINT      | Yes      | —                 | —                      | CHECK (match_score BETWEEN 0 AND 100) | Final score                                                 |
| breakdown         | JSONB         | Yes      | —                 | —                      | —                                     | {components:\[{key,weight,score,points}\], weights_version} |
| matched_skill_ids | UUID\[\]      | Yes      | '{}'              | —                      | —                                     | Skills user has                                             |
| missing_skill_ids | UUID\[\]      | Yes      | '{}'              | —                      | —                                     | Skills user lacks                                           |
| low_confidence    | BOOLEAN       | Yes      | false             | —                      | —                                     | No skills extracted                                         |
| rank              | SMALLINT      | No       | —                 | —                      | —                                     | Rank within session                                         |
| created_at        | TIMESTAMPTZ   | Yes      | now()             | —                      | —                                     | Creation time                                               |

Table constraints: UNIQUE (agent_session_id, opportunity_id)

## 2.9 SavedOpportunity — saved_opportunities

Bookmarks.

| **Column**     | **Data type** | **Req.** | **Default**       | **Key**               | **Constraints**   | **Description** |
| -------------- | ------------- | -------- | ----------------- | --------------------- | ----------------- | --------------- |
| id             | UUID          | Yes      | gen_random_uuid() | PK                    | —                 | Primary key     |
| user_id        | UUID          | Yes      | —                 | FK → users.id         | ON DELETE CASCADE |                 |
| opportunity_id | UUID          | Yes      | —                 | FK → opportunities.id | ON DELETE CASCADE |                 |
| note           | VARCHAR(500)  | No       | —                 | —                     | —                 | Optional note   |
| created_at     | TIMESTAMPTZ   | Yes      | now()             | —                     | —                 | Creation time   |

Table constraints: UNIQUE (user_id, opportunity_id)

## 2.10 Application — applications

Application tracker.

| **Column**     | **Data type** | **Req.** | **Default**       | **Key**               | **Constraints**                                                                       | **Description**                         |
| -------------- | ------------- | -------- | ----------------- | --------------------- | ------------------------------------------------------------------------------------- | --------------------------------------- |
| id             | UUID          | Yes      | gen_random_uuid() | PK                    | —                                                                                     | Primary key                             |
| user_id        | UUID          | Yes      | —                 | FK → users.id         | ON DELETE CASCADE                                                                     |                                         |
| opportunity_id | UUID          | Yes      | —                 | FK → opportunities.id | ON DELETE CASCADE                                                                     |                                         |
| status         | VARCHAR(15)   | Yes      | 'planned'         | —                     | CHECK (status IN ('planned','applied','interviewing','offer','rejected','withdrawn')) | Current status                          |
| applied_on     | DATE          | No       | —                 | —                     | —                                                                                     | Date applied                            |
| notes          | TEXT          | No       | —                 | —                     | —                                                                                     | Free text (max 2,000 via API)           |
| status_history | JSONB         | Yes      | '\[\]'            | —                     | —                                                                                     | \[{status, at}\] appended on change     |
| created_at     | TIMESTAMPTZ   | Yes      | now()             | —                     | —                                                                                     | Creation time                           |
| updated_at     | TIMESTAMPTZ   | Yes      | now()             | —                     | —                                                                                     | Last update time (set by app on update) |

Table constraints: UNIQUE (user_id, opportunity_id)

## 2.11 AgentSession — agent_sessions

One AI Career Agent run.

| **Column**        | **Data type** | **Req.** | **Default**       | **Key**              | **Constraints**                                                       | **Description**                                |
| ----------------- | ------------- | -------- | ----------------- | -------------------- | --------------------------------------------------------------------- | ---------------------------------------------- |
| id                | UUID          | Yes      | gen_random_uuid() | PK                   | —                                                                     | Primary key                                    |
| user_id           | UUID          | Yes      | —                 | FK → users.id        | ON DELETE CASCADE                                                     |                                                |
| career_goal_id    | UUID          | No       | —                 | FK → career_goals.id | ON DELETE SET NULL                                                    |                                                |
| status            | VARCHAR(12)   | Yes      | 'queued'          | —                    | CHECK (status IN ('queued','running','completed','partial','failed')) | Lifecycle                                      |
| input_snapshot    | JSONB         | Yes      | —                 | —                    | —                                                                     | Profile/goal/skills used (no name/email)       |
| stages            | JSONB         | Yes      | '\[\]'            | —                    | —                                                                     | \[{key,status,started_at,duration_ms,detail}\] |
| warnings          | JSONB         | Yes      | '\[\]'            | —                    | —                                                                     | \[{code,message,engine?}\]                     |
| result_summary    | JSONB         | No       | —                 | —                    | —                                                                     | {opportunity_count, best_score, news:\[…\]}    |
| error_code        | VARCHAR(40)   | No       | —                 | —                    | —                                                                     | When failed                                    |
| serp_calls_live   | SMALLINT      | Yes      | 0                 | —                    | —                                                                     | Quota accounting                               |
| serp_calls_cached | SMALLINT      | Yes      | 0                 | —                    | —                                                                     | Cache hits                                     |
| started_at        | TIMESTAMPTZ   | No       | —                 | —                    | —                                                                     | Run start                                      |
| completed_at      | TIMESTAMPTZ   | No       | —                 | —                    | —                                                                     | Run end                                        |
| duration_ms       | INTEGER       | No       | —                 | —                    | —                                                                     | Total time                                     |
| created_at        | TIMESTAMPTZ   | Yes      | now()             | —                    | —                                                                     | Creation time                                  |

## 2.12 SearchHistory — search_history

Every SerpApi query executed.

| **Column**       | **Data type** | **Req.** | **Default**       | **Key**                | **Constraints**                                                    | **Description**        |
| ---------------- | ------------- | -------- | ----------------- | ---------------------- | ------------------------------------------------------------------ | ---------------------- |
| id               | UUID          | Yes      | gen_random_uuid() | PK                     | —                                                                  | Primary key            |
| user_id          | UUID          | Yes      | —                 | FK → users.id          | ON DELETE CASCADE                                                  |                        |
| agent_session_id | UUID          | Yes      | —                 | FK → agent_sessions.id | ON DELETE CASCADE                                                  |                        |
| engine           | VARCHAR(20)   | Yes      | —                 | —                      | CHECK (engine IN ('google_jobs','google','google_news','youtube')) | SerpApi engine         |
| query            | VARCHAR(200)  | Yes      | —                 | —                      | —                                                                  | q / search_query       |
| location         | VARCHAR(120)  | No       | —                 | —                      | —                                                                  | location param         |
| purpose          | VARCHAR(15)   | Yes      | —                 | —                      | CHECK (purpose IN ('jobs','programs','market_signal','learning'))  | Planner purpose        |
| result_count     | INTEGER       | Yes      | 0                 | —                      | —                                                                  | Items returned         |
| cached           | BOOLEAN       | Yes      | false             | —                      | —                                                                  | Served from serp_cache |
| latency_ms       | INTEGER       | No       | —                 | —                      | —                                                                  | Call latency           |
| error_code       | VARCHAR(40)   | No       | —                 | —                      | —                                                                  | If failed              |
| created_at       | TIMESTAMPTZ   | Yes      | now()             | —                      | —                                                                  | Creation time          |

## 2.13 SkillGap — skill_gaps

Aggregated missing skills per session.

| **Column**       | **Data type** | **Req.** | **Default**       | **Key**                | **Constraints**                             | **Description**                    |
| ---------------- | ------------- | -------- | ----------------- | ---------------------- | ------------------------------------------- | ---------------------------------- |
| id               | UUID          | Yes      | gen_random_uuid() | PK                     | —                                           | Primary key                        |
| user_id          | UUID          | Yes      | —                 | FK → users.id          | ON DELETE CASCADE                           |                                    |
| agent_session_id | UUID          | Yes      | —                 | FK → agent_sessions.id | ON DELETE CASCADE                           |                                    |
| skill_id         | UUID          | Yes      | —                 | FK → skills.id         | ON DELETE RESTRICT                          |                                    |
| demand_count     | SMALLINT      | Yes      | —                 | —                      | —                                           | Top-N opportunities listing it     |
| demand_pct       | NUMERIC(5,4)  | Yes      | —                 | —                      | —                                           | demand_count / N                   |
| avg_uplift       | NUMERIC(5,2)  | Yes      | 0                 | —                      | —                                           | Avg score points gained if learned |
| priority_score   | NUMERIC(5,4)  | Yes      | —                 | —                      | —                                           | 0.6·demand + 0.4·uplift_norm       |
| priority         | VARCHAR(6)    | Yes      | —                 | —                      | CHECK (priority IN ('high','medium','low')) | Bucket                             |
| rank             | SMALLINT      | Yes      | —                 | —                      | —                                           | 1 = most important                 |
| opportunity_ids  | UUID\[\]      | Yes      | '{}'              | —                      | —                                           | Opportunities needing this skill   |
| created_at       | TIMESTAMPTZ   | Yes      | now()             | —                      | —                                           | Creation time                      |

Table constraints: UNIQUE (agent_session_id, skill_id)

## 2.14 Roadmap — roadmaps

Personalized roadmap per session.

| **Column**        | **Data type** | **Req.** | **Default**       | **Key**                | **Constraints**                                 | **Description**     |
| ----------------- | ------------- | -------- | ----------------- | ---------------------- | ----------------------------------------------- | ------------------- |
| id                | UUID          | Yes      | gen_random_uuid() | PK                     | —                                               | Primary key         |
| user_id           | UUID          | Yes      | —                 | FK → users.id          | ON DELETE CASCADE                               |                     |
| agent_session_id  | UUID          | Yes      | —                 | FK → agent_sessions.id | ON DELETE CASCADE                               |                     |
| title             | VARCHAR(200)  | Yes      | —                 | —                      | —                                               | Roadmap title       |
| summary           | TEXT          | No       | —                 | —                      | —                                               | Short rationale     |
| total_weeks       | SMALLINT      | No       | —                 | —                      | —                                               | Estimate            |
| generation_method | VARCHAR(10)   | Yes      | 'llm'             | —                      | CHECK (generation_method IN ('llm','template')) | Fallback visibility |
| is_active         | BOOLEAN       | Yes      | true              | —                      | —                                               | Latest roadmap      |
| created_at        | TIMESTAMPTZ   | Yes      | now()             | —                      | —                                               | Creation time       |

Table constraints: UNIQUE (agent_session_id)

## 2.15 RoadmapStep — roadmap_steps

Ordered roadmap steps.

| **Column**      | **Data type** | **Req.** | **Default**       | **Key**               | **Constraints**                                | **Description**                      |
| --------------- | ------------- | -------- | ----------------- | --------------------- | ---------------------------------------------- | ------------------------------------ |
| id              | UUID          | Yes      | gen_random_uuid() | PK                    | —                                              | Primary key                          |
| roadmap_id      | UUID          | Yes      | —                 | FK → roadmaps.id      | ON DELETE CASCADE                              |                                      |
| skill_id        | UUID          | No       | —                 | FK → skills.id        | ON DELETE SET NULL                             |                                      |
| opportunity_id  | UUID          | No       | —                 | FK → opportunities.id | ON DELETE SET NULL                             | For apply steps                      |
| step_order      | SMALLINT      | Yes      | —                 | —                     | —                                              | 1..8                                 |
| step_type       | VARCHAR(6)    | Yes      | —                 | —                     | CHECK (step_type IN ('learn','build','apply')) | Type                                 |
| title           | VARCHAR(200)  | Yes      | —                 | —                     | —                                              | Step title                           |
| description     | TEXT          | No       | —                 | —                     | —                                              | Details                              |
| reason          | VARCHAR(300)  | No       | —                 | —                     | —                                              | Why this step (grounded in gap data) |
| estimated_hours | SMALLINT      | No       | —                 | —                     | —                                              | Effort                               |
| action          | VARCHAR(300)  | No       | —                 | —                     | —                                              | Concrete next action                 |
| resource_query  | VARCHAR(200)  | No       | —                 | —                     | —                                              | Search string (no fabricated URLs)   |
| resources       | JSONB         | Yes      | '\[\]'            | —                     | —                                              | **\[PHASE 2\]** real YouTube results |
| is_completed    | BOOLEAN       | Yes      | false             | —                     | —                                              | User progress                        |
| completed_at    | TIMESTAMPTZ   | No       | —                 | —                     | —                                              | When completed                       |
| created_at      | TIMESTAMPTZ   | Yes      | now()             | —                     | —                                              | Creation time                        |

Table constraints: UNIQUE (roadmap_id, step_order)

## 2.16 SerpCache — serp_cache

Raw SerpApi responses keyed by canonical params (excluding api_key). Added.

| **Column**   | **Data type** | **Req.** | **Default**       | **Key** | **Constraints** | **Description**            |
| ------------ | ------------- | -------- | ----------------- | ------- | --------------- | -------------------------- |
| id           | UUID          | Yes      | gen_random_uuid() | PK      | —               | Primary key                |
| cache_key    | CHAR(64)      | Yes      | —                 | —       | UNIQUE          | sha256 of canonical params |
| engine       | VARCHAR(20)   | Yes      | —                 | —       | —               | SerpApi engine             |
| params       | JSONB         | Yes      | —                 | —       | —               | Canonical params           |
| raw_json     | JSONB         | Yes      | —                 | —       | —               | Full response              |
| result_count | INTEGER       | Yes      | 0                 | —       | —               | Items                      |
| fetched_at   | TIMESTAMPTZ   | Yes      | now()             | —       | —               | Fetch time                 |
| expires_at   | TIMESTAMPTZ   | Yes      | —                 | —       | —               | fetched_at + TTL           |

# 3\. ER Diagram

_Mermaid diagram — Entity Relationship Diagram (paste into mermaid.live, GitHub, or Notion to render)_

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

| **Relationship**                                                           | **Cardinality**                | **On delete**      |
| -------------------------------------------------------------------------- | ------------------------------ | ------------------ |
| users → user_profiles                                                      | 1 : 1                          | CASCADE            |
| users → user_skills ← skills                                               | M : N                          | CASCADE / RESTRICT |
| users → career_goals                                                       | 1 : N (1 active)               | CASCADE            |
| opportunities → opportunity_skills ← skills                                | M : N                          | CASCADE / RESTRICT |
| users × opportunities via opportunity_matches (per session)                | M : N                          | CASCADE            |
| users → agent_sessions → search_history / skill_gaps / opportunity_matches | 1 : N : N                      | CASCADE            |
| agent_sessions → roadmaps → roadmap_steps                                  | 1 : 1 : N                      | CASCADE            |
| users → saved_opportunities / applications                                 | 1 : N (unique per opportunity) | CASCADE            |

# 4\. Reference DDL

Implement through Alembic; this DDL is the reference the migration must produce.

_schema.sql_

```
-- OpportunityOS PostgreSQL DDL (reference; implement via Alembic migrations)
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

```
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(120) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT true,
  last_login_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

```
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  education_level VARCHAR(30) NOT NULL CHECK (education_level IN ('high_school','diploma','bachelors','masters','phd','other')),
  degree VARCHAR(120),
  field_of_study VARCHAR(120),
  graduation_year SMALLINT CHECK (graduation_year BETWEEN 1990 AND 2040),
  institution VARCHAR(200),
  experience_level VARCHAR(20) NOT NULL DEFAULT 'student' CHECK (experience_level IN ('student','fresher','0_1_years','1_2_years')),
  location_city VARCHAR(100),
  location_state VARCHAR(100),
  location_country VARCHAR(2) NOT NULL DEFAULT 'IN',
  open_to_remote BOOLEAN NOT NULL DEFAULT true,
  weekly_learning_hours SMALLINT NOT NULL DEFAULT 10 CHECK (weekly_learning_hours BETWEEN 1 AND 60),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id)
);
```

```
CREATE TABLE skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(80) NOT NULL UNIQUE,
  slug VARCHAR(80) NOT NULL UNIQUE,
  category VARCHAR(40),
  aliases TEXT[] NOT NULL DEFAULT '{}',
  is_verified BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

```
CREATE TABLE user_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE RESTRICT,
  proficiency SMALLINT NOT NULL DEFAULT 2 CHECK (proficiency BETWEEN 1 AND 5),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, skill_id)
);
```

```
CREATE TABLE career_goals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  target_role VARCHAR(120) NOT NULL,
  goal_statement VARCHAR(280),
  timeline_months SMALLINT NOT NULL DEFAULT 3 CHECK (timeline_months IN (1,3,6,12)),
  opportunity_types TEXT[] NOT NULL DEFAULT '{internship}',
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

```
CREATE TABLE opportunities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dedupe_hash CHAR(64) NOT NULL UNIQUE,
  source_engine VARCHAR(20) NOT NULL CHECK (source_engine IN ('google_jobs','google')),
  external_id TEXT,
  title VARCHAR(300) NOT NULL,
  company_name VARCHAR(200),
  location VARCHAR(200),
  is_remote BOOLEAN NOT NULL DEFAULT false,
  opportunity_type VARCHAR(20) NOT NULL DEFAULT 'unknown' CHECK (opportunity_type IN ('internship','full_time','part_time','contract','career_page','program','unknown')),
  schedule_type VARCHAR(50),
  description TEXT,
  highlights JSONB,
  source_via VARCHAR(200),
  apply_url TEXT,
  posted_at_text VARCHAR(50),
  first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  raw JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

```
CREATE TABLE opportunity_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE RESTRICT,
  requirement VARCHAR(10) NOT NULL DEFAULT 'required' CHECK (requirement IN ('required','preferred')),
  extraction_method VARCHAR(12) NOT NULL DEFAULT 'dictionary' CHECK (extraction_method IN ('dictionary','llm')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (opportunity_id, skill_id)
);
```

```
CREATE TABLE agent_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  career_goal_id UUID REFERENCES career_goals(id) ON DELETE SET NULL,
  status VARCHAR(12) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','running','completed','partial','failed')),
  input_snapshot JSONB NOT NULL,
  stages JSONB NOT NULL DEFAULT '[]',
  warnings JSONB NOT NULL DEFAULT '[]',
  result_summary JSONB,
  error_code VARCHAR(40),
  serp_calls_live SMALLINT NOT NULL DEFAULT 0,
  serp_calls_cached SMALLINT NOT NULL DEFAULT 0,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  duration_ms INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

```
CREATE TABLE opportunity_matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  agent_session_id UUID NOT NULL REFERENCES agent_sessions(id) ON DELETE CASCADE,
  match_score SMALLINT NOT NULL CHECK (match_score BETWEEN 0 AND 100),
  breakdown JSONB NOT NULL,
  matched_skill_ids UUID[] NOT NULL DEFAULT '{}',
  missing_skill_ids UUID[] NOT NULL DEFAULT '{}',
  low_confidence BOOLEAN NOT NULL DEFAULT false,
  rank SMALLINT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (agent_session_id, opportunity_id)
);
```

```
CREATE TABLE saved_opportunities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  note VARCHAR(500),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, opportunity_id)
);
```

```
CREATE TABLE applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  status VARCHAR(15) NOT NULL DEFAULT 'planned' CHECK (status IN ('planned','applied','interviewing','offer','rejected','withdrawn')),
  applied_on DATE,
  notes TEXT,
  status_history JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, opportunity_id)
);
```

```
CREATE TABLE search_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  agent_session_id UUID NOT NULL REFERENCES agent_sessions(id) ON DELETE CASCADE,
  engine VARCHAR(20) NOT NULL CHECK (engine IN ('google_jobs','google','google_news','youtube')),
  query VARCHAR(200) NOT NULL,
  location VARCHAR(120),
  purpose VARCHAR(15) NOT NULL CHECK (purpose IN ('jobs','programs','market_signal','learning')),
  result_count INTEGER NOT NULL DEFAULT 0,
  cached BOOLEAN NOT NULL DEFAULT false,
  latency_ms INTEGER,
  error_code VARCHAR(40),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

```
CREATE TABLE skill_gaps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  agent_session_id UUID NOT NULL REFERENCES agent_sessions(id) ON DELETE CASCADE,
  skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE RESTRICT,
  demand_count SMALLINT NOT NULL,
  demand_pct NUMERIC(5,4) NOT NULL,
  avg_uplift NUMERIC(5,2) NOT NULL DEFAULT 0,
  priority_score NUMERIC(5,4) NOT NULL,
  priority VARCHAR(6) NOT NULL CHECK (priority IN ('high','medium','low')),
  rank SMALLINT NOT NULL,
  opportunity_ids UUID[] NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (agent_session_id, skill_id)
);
```

```
CREATE TABLE roadmaps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  agent_session_id UUID NOT NULL REFERENCES agent_sessions(id) ON DELETE CASCADE,
  title VARCHAR(200) NOT NULL,
  summary TEXT,
  total_weeks SMALLINT,
  generation_method VARCHAR(10) NOT NULL DEFAULT 'llm' CHECK (generation_method IN ('llm','template')),
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (agent_session_id)
);
```

```
CREATE TABLE roadmap_steps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  roadmap_id UUID NOT NULL REFERENCES roadmaps(id) ON DELETE CASCADE,
  skill_id UUID REFERENCES skills(id) ON DELETE SET NULL,
  opportunity_id UUID REFERENCES opportunities(id) ON DELETE SET NULL,
  step_order SMALLINT NOT NULL,
  step_type VARCHAR(6) NOT NULL CHECK (step_type IN ('learn','build','apply')),
  title VARCHAR(200) NOT NULL,
  description TEXT,
  reason VARCHAR(300),
  estimated_hours SMALLINT,
  action VARCHAR(300),
  resource_query VARCHAR(200),
  resources JSONB NOT NULL DEFAULT '[]',
  is_completed BOOLEAN NOT NULL DEFAULT false,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (roadmap_id, step_order)
);
```

```
CREATE TABLE serp_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cache_key CHAR(64) NOT NULL UNIQUE,
  engine VARCHAR(20) NOT NULL,
  params JSONB NOT NULL,
  raw_json JSONB NOT NULL,
  result_count INTEGER NOT NULL DEFAULT 0,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ NOT NULL
);
```

```
CREATE UNIQUE INDEX uq_career_goals_active ON career_goals(user_id) WHERE is_active;
CREATE INDEX ix_user_skills_user ON user_skills(user_id);
CREATE INDEX ix_opportunity_skills_opp ON opportunity_skills(opportunity_id);
CREATE INDEX ix_matches_user_session_score ON opportunity_matches(user_id, agent_session_id, match_score DESC);
CREATE INDEX ix_saved_user ON saved_opportunities(user_id, created_at DESC);
CREATE INDEX ix_applications_user_status ON applications(user_id, status);
CREATE INDEX ix_agent_sessions_user ON agent_sessions(user_id, created_at DESC);
CREATE INDEX ix_search_history_user ON search_history(user_id, created_at DESC);
CREATE INDEX ix_skill_gaps_session_rank ON skill_gaps(agent_session_id, rank);
CREATE INDEX ix_serp_cache_expires ON serp_cache(expires_at);
CREATE INDEX ix_skills_aliases ON skills USING GIN(aliases);
```

# 5\. API Conventions

- Base URL: https://&lt;backend-host&gt; (local <http://localhost:8000>). Optional prefix via API_PREFIX.
- Content-Type: application/json. Auth header: Authorization: Bearer &lt;access_token&gt;.
- Pagination: page (default 1), page_size (default 20, max 50); response includes page, page_size, total.
- Every response includes header X-Request-ID.
- Interactive docs: /docs (Swagger UI) and /openapi.json.

| **Method** | **Path**                 | **Auth** | **Purpose**                                            | **In brief?** |
| ---------- | ------------------------ | -------- | ------------------------------------------------------ | ------------- |
| POST       | /auth/register           | Public   | Create account, return JWT                             | Yes           |
| POST       | /auth/login              | Public   | Authenticate, return JWT                               | Yes           |
| GET        | /profile                 | JWT      | Get profile, skills and career goal                    | Yes           |
| PUT        | /profile                 | JWT      | Create/update profile, skills and career goal          | Yes           |
| GET        | /skills                  | JWT      | Search the skill catalog (autocomplete)                | Added         |
| POST       | /agent/search            | JWT      | Run the AI Career Agent end-to-end                     | Yes           |
| GET        | /agent/sessions/{id}     | JWT      | Fetch a past or running agent session                  | Added         |
| GET        | /opportunities           | JWT      | List matched opportunities (filters, sort, pagination) | Yes           |
| GET        | /opportunities/{id}      | JWT      | Opportunity detail + match explanation                 | Yes           |
| POST       | /opportunities/{id}/save | JWT      | Save opportunity                                       | Yes           |
| DELETE     | /opportunities/{id}/save | JWT      | Unsave opportunity                                     | Yes           |
| GET        | /skill-gap               | JWT      | Aggregated missing skills for latest session           | Yes           |
| GET        | /roadmap                 | JWT      | Personalized roadmap for latest session                | Yes           |
| PATCH      | /roadmap/steps/{id}      | JWT      | Mark a roadmap step done / not done                    | Added         |
| GET        | /applications            | JWT      | List tracked applications                              | Added         |
| POST       | /applications            | JWT      | Start tracking an application                          | Yes           |
| PUT        | /applications/{id}       | JWT      | Update application status / notes                      | Yes           |
| GET        | /search/history          | JWT      | List previous agent searches and queries               | Yes           |

# 6\. Error Format

_Standard error envelope_

```
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [{"field": "password", "issue": "min_length 8"}],
    "request_id": "0b6f3a52-7c1e-4a8f-9a44-2c1d0f1e9b10"
  }
}
```

| **Code**           | **HTTP** | **When**                                                    |
| ------------------ | -------- | ----------------------------------------------------------- |
| VALIDATION_ERROR   | 422      | Body/query fails Pydantic validation                        |
| UNAUTHORIZED       | 401      | Missing, invalid, or expired token; bad credentials         |
| FORBIDDEN          | 403      | Resource belongs to another user                            |
| NOT_FOUND          | 404      | Resource missing                                            |
| CONFLICT           | 409      | Duplicate email, application, etc.                          |
| PROFILE_INCOMPLETE | 400      | Agent run without target role / skills / location or remote |
| NO_SESSION         | 404      | No completed agent session yet                              |
| RATE_LIMITED       | 429      | Limit exceeded (includes Retry-After header)                |
| SERPAPI_QUOTA      | 503      | SerpApi quota exhausted and no cache                        |
| SERPAPI_ERROR      | 502      | Upstream SerpApi failure                                    |
| LLM_ERROR          | 502      | LLM failed and no fallback                                  |
| INTERNAL_ERROR     | 500      | Unhandled exception                                         |

FastAPI implementation: override RequestValidationError and HTTPException handlers, and raise a custom AppError(code, message, status, details) from services.

# 7\. API Reference

## 7.1 POST /auth/register

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Create a user account and return an access token.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>POST</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/auth/register</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>Public (rate limited 5/min/IP)</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>201 Created; 409; 422; 429</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>409 CONFLICT (email exists); 422 VALIDATION_ERROR; 429 RATE_LIMITED</p></td></tr></tbody></table></div>

_Request JSON_

```
{
  "full_name": "Riya Shah",
  "email": "riya@example.com",
  "password": "S3cure!pass"
}
```

_Response JSON_

```
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {"id": "3f2c…", "full_name": "Riya Shah", "email": "riya@example.com"},
  "profile_complete": false
}
```

## 7.2 POST /auth/login

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Authenticate and return an access token.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>POST</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/auth/login</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>Public (rate limited 10/min/IP)</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>200; 401; 422; 429</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>401 UNAUTHORIZED ("Email or password is incorrect" — same message for both cases)</p></td></tr></tbody></table></div>

_Request JSON_

```
{"email": "riya@example.com", "password": "S3cure!pass"}
```

_Response JSON_

```
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {"id": "3f2c…", "full_name": "Riya Shah", "email": "riya@example.com"},
  "profile_complete": true
}
```

## 7.3 GET /profile

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Return the user's profile, skills, and active career goal.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>GET</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/profile</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>200; 401</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>401 UNAUTHORIZED; 422 VALIDATION_ERROR</p></td></tr></tbody></table></div>

Request body: none.

_Response JSON_

```
{
  "user": {"id": "3f2c…", "full_name": "Riya Shah", "email": "riya@example.com"},
  "profile": {
    "education_level": "bachelors", "degree": "B.Tech", "field_of_study": "Computer Science",
    "graduation_year": 2027, "institution": null, "experience_level": "student",
    "location_city": "Ahmedabad", "location_state": "Gujarat", "location_country": "IN",
    "open_to_remote": true, "weekly_learning_hours": 10, "updated_at": "2026-09-27T09:10:00Z"
  },
  "skills": [
    {"skill_id": "a1…", "name": "HTML", "proficiency": 4},
    {"skill_id": "a2…", "name": "CSS", "proficiency": 3},
    {"skill_id": "a3…", "name": "JavaScript", "proficiency": 3}
  ],
  "career_goal": {
    "id": "c9…", "target_role": "Frontend Developer",
    "goal_statement": "Get a frontend internship before graduation",
    "timeline_months": 3, "opportunity_types": ["internship"]
  },
  "profile_complete": true
}
```

## 7.4 PUT /profile

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Create or replace profile, skills, and active career goal in one transaction (idempotent).</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>PUT</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/profile</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>200; 401; 422</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>422 VALIDATION_ERROR (e.g., empty skills, unknown opportunity type)</p></td></tr></tbody></table></div>

_Request JSON_

```
{
  "profile": {
    "education_level": "bachelors", "degree": "B.Tech", "field_of_study": "Computer Science",
    "graduation_year": 2027, "institution": null, "experience_level": "student",
    "location_city": "Ahmedabad", "location_state": "Gujarat", "location_country": "IN",
    "open_to_remote": true, "weekly_learning_hours": 10
  },
  "skills": [
    {"skill_id": "a1…", "proficiency": 4},
    {"name": "Figma", "proficiency": 2}
  ],
  "career_goal": {
    "target_role": "Frontend Developer",
    "goal_statement": "Get a frontend internship before graduation",
    "timeline_months": 3,
    "opportunity_types": ["internship"]
  }
}
```

_Response JSON_

```
// Same shape as GET /profile
```

Skill items accept either skill_id or name. Names are resolved against skills.name/aliases (case-insensitive); unknown names create an unverified skill. If career_goal.target_role changes, the previous goal is deactivated and a new row inserted (history preserved).

## 7.5 GET /skills (added)

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Skill catalog autocomplete.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>GET</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/skills</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT</p></td></tr><tr><td><p><strong>Query params</strong></p></td><td><p>q (min 1 char), limit (default 10, max 25), category (optional)</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>200; 401; 422</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>401 UNAUTHORIZED; 422 VALIDATION_ERROR</p></td></tr></tbody></table></div>

Request body: none.

_Response JSON_

```
{"items": [{"id": "b7…", "name": "React", "category": "frontend"}, {"id": "b8…", "name": "React Native", "category": "mobile"}]}
```

## 7.6 POST /agent/search

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Start an AI Career Agent run for the current profile. Runs in-process as a background task.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>POST</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/agent/search</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT (limit 5/hour and 15/day per user)</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>202 Accepted; 400; 401; 429</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>400 PROFILE_INCOMPLETE; 429 RATE_LIMITED; 503 SERPAPI_QUOTA (only if budget already exhausted and no cache can serve any planned query — checked early)</p></td></tr></tbody></table></div>

_Request JSON_

```
{
  "overrides": {
    "location_city": "Ahmedabad",
    "open_to_remote": true,
    "opportunity_types": ["internship"]
  },
  "include_news": true
}
// body optional; empty {} uses stored profile
```

_Response JSON_

```
{
  "session_id": "5d0e…",
  "status": "queued",
  "poll_url": "/agent/sessions/5d0e…",
  "poll_interval_ms": 1500
}
```

## 7.7 GET /agent/sessions/{id} (added)

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Get status, stage progress, and summary of an agent run.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>GET</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/agent/sessions/{id}</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT (owner only)</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>200; 401; 403; 404</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>403 FORBIDDEN; 404 NOT_FOUND</p></td></tr></tbody></table></div>

Request body: none.

_Response JSON_

```
{
  "id": "5d0e…",
  "status": "running",
  "created_at": "2026-09-27T09:12:00Z",
  "stages": [
    {"key": "plan_queries", "status": "done", "duration_ms": 3120,
     "detail": {"queries": [
       {"engine": "google_jobs", "q": "frontend developer internship", "location": "Ahmedabad, Gujarat, India", "purpose": "jobs"},
       {"engine": "google_news", "q": "frontend developer hiring India", "purpose": "market_signal"}]}},
    {"key": "search", "status": "running", "detail": {"completed": 3, "total": 5, "results": 0}},
    {"key": "normalize_dedupe", "status": "pending"},
    {"key": "extract_skills", "status": "pending"},
    {"key": "match", "status": "pending"},
    {"key": "skill_gap", "status": "pending"},
    {"key": "roadmap", "status": "pending"}
  ],
  "warnings": [],
  "result_summary": null
}
// When completed:
// "status": "completed",
// "result_summary": {"opportunity_count": <int>, "best_score": <int>,
//   "news": [{"title": "...", "link": "...", "source": "...", "date": "..."}]}
// (news items are copied from real google_news results only)
```

## 7.8 GET /opportunities

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>List scored opportunities for a session (default: latest completed) or the user's saved items.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>GET</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/opportunities</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT</p></td></tr><tr><td><p><strong>Query params</strong></p></td><td><p>session_id (optional), saved (bool), type, remote (bool), min_score (0–100), engine, sort = score|recent (default score), page, page_size</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>200; 401; 404; 422</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>404 NO_SESSION (no completed session and saved≠true)</p></td></tr></tbody></table></div>

Request body: none.

_Response JSON_

```
{
  "session_id": "5d0e…",
  "items": [
    {
      "id": "9a1…",
      "title": "<from source>",
      "company_name": "<from source>",
      "location": "<from source>",
      "is_remote": true,
      "opportunity_type": "internship",
      "source_engine": "google_jobs",
      "source_via": "<from source>",
      "posted_at_text": "<from source>",
      "match_score": 87,
      "low_confidence": false,
      "top_skills": [
        {"name": "HTML", "has": true, "requirement": "required"},
        {"name": "React", "has": false, "requirement": "required"}
      ],
      "saved": false,
      "application_status": null
    }
  ],
  "page": 1, "page_size": 20, "total": 28
}
```

## 7.9 GET /opportunities/{id}

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Opportunity detail with the current user's match explanation.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>GET</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/opportunities/{id}</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT</p></td></tr><tr><td><p><strong>Query params</strong></p></td><td><p>session_id (optional; default latest session containing this opportunity)</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>200; 401; 404</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>404 NOT_FOUND</p></td></tr></tbody></table></div>

Request body: none.

_Response JSON_

```
{
  "opportunity": {
    "id": "9a1…", "title": "…", "company_name": "…", "location": "…", "is_remote": true,
    "opportunity_type": "internship", "schedule_type": "…", "source_engine": "google_jobs",
    "source_via": "…", "apply_url": "https://…", "posted_at_text": "…",
    "description": "…", "highlights": [{"title": "Qualifications", "items": ["…"]}],
    "first_seen_at": "2026-09-27T09:12:40Z"
  },
  "match": {
    "match_score": 87,
    "low_confidence": false,
    "breakdown": {
      "weights_version": "v1",
      "components": [
        {"key": "skills", "weight": 0.50, "score": 0.74, "points": 37.0},
        {"key": "role", "weight": 0.15, "score": 1.0, "points": 15.0},
        {"key": "location", "weight": 0.15, "score": 1.0, "points": 15.0},
        {"key": "experience", "weight": 0.10, "score": 1.0, "points": 10.0},
        {"key": "type", "weight": 0.10, "score": 1.0, "points": 10.0}
      ]
    },
    "matched_skills": [{"id": "a1…", "name": "HTML", "requirement": "required"}],
    "missing_skills": [{"id": "b7…", "name": "React", "requirement": "required"}]
  },
  "saved": true,
  "application": {"id": "e4…", "status": "applied"}
}
```

## 7.10 POST /opportunities/{id}/save

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Save an opportunity (idempotent).</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>POST</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/opportunities/{id}/save</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>201 Created (new); 200 OK (already saved); 401; 404</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>404 NOT_FOUND</p></td></tr></tbody></table></div>

_Request JSON_

```
{"note": "Apply after finishing React basics"}   // optional
```

_Response JSON_

```
{"saved": true, "saved_at": "2026-09-27T09:20:00Z", "opportunity_id": "9a1…"}
```

## 7.11 DELETE /opportunities/{id}/save

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Remove a saved opportunity (idempotent).</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>DELETE</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/opportunities/{id}/save</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>204 No Content; 401; 404</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>404 NOT_FOUND (opportunity does not exist)</p></td></tr></tbody></table></div>

Request body: none.

_Response JSON_

```
// 204: empty body
```

## 7.12 GET /skill-gap

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Ranked missing skills for a session.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>GET</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/skill-gap</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT</p></td></tr><tr><td><p><strong>Query params</strong></p></td><td><p>session_id (optional, default latest completed)</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>200; 401; 404</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>404 NO_SESSION</p></td></tr></tbody></table></div>

Request body: none.

_Response JSON_

```
{
  "session_id": "5d0e…",
  "top_n": 15,
  "items": [
    {"rank": 1, "skill": {"id": "b7…", "name": "React"}, "priority": "high",
     "demand_count": 9, "demand_pct": 0.60, "avg_uplift": 11.2, "priority_score": 0.76,
     "opportunity_ids": ["9a1…", "9a4…"]}
  ]
}
// numbers illustrative
```

## 7.13 GET /roadmap

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Active roadmap for a session.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>GET</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/roadmap</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT</p></td></tr><tr><td><p><strong>Query params</strong></p></td><td><p>session_id (optional)</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>200; 401; 404</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>404 NO_SESSION</p></td></tr></tbody></table></div>

Request body: none.

_Response JSON_

```
{
  "id": "r1…",
  "session_id": "5d0e…",
  "title": "Frontend Developer roadmap",
  "summary": "Close the React and REST API gaps, prove them with a project, then apply.",
  "total_weeks": 6,
  "generation_method": "llm",
  "progress_pct": 25,
  "steps": [
    {"id": "s1…", "step_order": 1, "step_type": "learn", "title": "React fundamentals",
     "skill": {"id": "b7…", "name": "React"}, "estimated_hours": 20,
     "reason": "Listed in 9 of your top 15 matches",
     "action": "Complete a beginner React course and build 3 small components",
     "resource_query": "react tutorial for beginners", "resources": [],
     "is_completed": true, "opportunity": null},
    {"id": "s4…", "step_order": 4, "step_type": "apply", "title": "Apply to top matches",
     "skill": null, "estimated_hours": 2, "reason": "Your match improves after steps 1–3",
     "action": "Apply and track in OpportunityOS", "resource_query": null, "resources": [],
     "is_completed": false, "opportunity": {"id": "9a1…", "title": "…"}}
  ]
}
```

## 7.14 PATCH /roadmap/steps/{id} (added)

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Mark a roadmap step complete or incomplete.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>PATCH</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/roadmap/steps/{id}</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT (owner only)</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>200; 401; 403; 404; 422</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>403 FORBIDDEN; 404 NOT_FOUND</p></td></tr></tbody></table></div>

_Request JSON_

```
{"is_completed": true}
```

_Response JSON_

```
{"id": "s1…", "is_completed": true, "completed_at": "2026-09-27T10:00:00Z", "roadmap_progress_pct": 25}
```

## 7.15 GET /applications (added)

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>List tracked applications.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>GET</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/applications</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT</p></td></tr><tr><td><p><strong>Query params</strong></p></td><td><p>status (optional), page, page_size</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>200; 401</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>401 UNAUTHORIZED; 422 VALIDATION_ERROR</p></td></tr></tbody></table></div>

Request body: none.

_Response JSON_

```
{
  "items": [
    {"id": "e4…", "status": "applied", "applied_on": "2026-09-12", "notes": "Referred by senior",
     "opportunity": {"id": "9a1…", "title": "…", "company_name": "…", "match_score": 87},
     "updated_at": "2026-09-27T09:30:00Z"}
  ],
  "page": 1, "page_size": 20, "total": 1
}
```

## 7.16 POST /applications

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Start tracking an application for an opportunity.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>POST</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/applications</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>201; 401; 404; 409; 422</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>404 NOT_FOUND (opportunity); 409 CONFLICT (already tracked — response includes existing id in details)</p></td></tr></tbody></table></div>

_Request JSON_

```
{"opportunity_id": "9a1…", "status": "applied", "applied_on": "2026-09-27", "notes": "Applied via company site"}
```

_Response JSON_

```
{"id": "e4…", "opportunity_id": "9a1…", "status": "applied", "applied_on": "2026-09-27", "notes": "Applied via company site",
 "status_history": [{"status": "applied", "at": "2026-09-27T09:30:00Z"}], "created_at": "2026-09-27T09:30:00Z"}
```

## 7.17 PUT /applications/{id}

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>Update status, date, or notes. Status changes append to status_history.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>PUT</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/applications/{id}</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT (owner only)</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>200; 401; 403; 404; 422</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>403 FORBIDDEN; 404 NOT_FOUND; 422 invalid status</p></td></tr></tbody></table></div>

_Request JSON_

```
{"status": "interviewing", "applied_on": "2026-09-27", "notes": "Round 1 on 3 Oct"}
```

_Response JSON_

```
{"id": "e4…", "status": "interviewing", "applied_on": "2026-09-27", "notes": "Round 1 on 3 Oct",
 "status_history": [{"status": "applied", "at": "…"}, {"status": "interviewing", "at": "…"}], "updated_at": "…"}
```

## 7.18 GET /search/history

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Purpose</strong></p></th><th><p>List past agent sessions with the SerpApi queries executed.</p></th></tr><tr><td><p><strong>HTTP method</strong></p></td><td><p>GET</p></td></tr><tr><td><p><strong>URL</strong></p></td><td><pre><code>/search/history</code></pre></td></tr><tr><td><p><strong>Authentication</strong></p></td><td><p>JWT</p></td></tr><tr><td><p><strong>Query params</strong></p></td><td><p>page, page_size</p></td></tr><tr><td><p><strong>Status codes</strong></p></td><td><p>200; 401</p></td></tr><tr><td><p><strong>Error responses</strong></p></td><td><p>401 UNAUTHORIZED; 422 VALIDATION_ERROR</p></td></tr></tbody></table></div>

Request body: none.

_Response JSON_

```
{
  "items": [
    {"session_id": "5d0e…", "status": "completed", "created_at": "2026-09-27T09:12:00Z",
     "target_role": "Frontend Developer", "opportunity_count": 28, "best_score": 87,
     "queries": [
       {"engine": "google_jobs", "query": "frontend developer internship",
        "location": "Ahmedabad, Gujarat, India", "result_count": 10, "cached": false, "latency_ms": 2140},
       {"engine": "google_news", "query": "frontend developer hiring India",
        "location": null, "result_count": 10, "cached": true, "latency_ms": 12}
     ]}
  ],
  "page": 1, "page_size": 20, "total": 3
}
```

# 8\. JWT Authentication Flow

1. Client calls /auth/register or /auth/login.
2. Server issues HS256 JWT: {"sub": "&lt;user_uuid&gt;", "email": "...", "type": "access", "iat": ..., "exp": iat + JWT_EXPIRE_MINUTES}.
3. Client sends Authorization: Bearer &lt;token&gt; on every protected call.
4. get_current_user dependency decodes with JWT_SECRET, checks exp and type, loads active user; failure → 401.
5. On 401 the client clears the token and redirects to /login?next=….

_Reference implementation_

```
# app/core/security.py
def create_access_token(user_id: UUID, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "email": email, "type": "access",
               "iat": now, "exp": now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
```

```
# app/api/deps.py
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise AppError("UNAUTHORIZED", "Invalid or expired token", 401)
    user = db.get(User, UUID(data["sub"]))
    if not user or not user.is_active:
        raise AppError("UNAUTHORIZED", "Invalid or expired token", 401)
    return user
```

# 9\. Validation

| **Field**             | **Rule**                                                             |
| --------------------- | -------------------------------------------------------------------- |
| email                 | EmailStr; lower-cased; ≤ 255                                         |
| password              | 8–128 chars; at least one letter and one digit                       |
| full_name             | 1–120 chars, trimmed                                                 |
| skills                | 1–40 items; proficiency 1–5; no duplicates after resolution          |
| target_role           | 2–120 chars                                                          |
| opportunity_types     | non-empty subset of internship, full_time, part_time, contract       |
| graduation_year       | 1990–2040                                                            |
| weekly_learning_hours | 1–60                                                                 |
| status (application)  | planned \| applied \| interviewing \| offer \| rejected \| withdrawn |
| notes                 | ≤ 2,000 chars                                                        |
| page_size             | 1–50                                                                 |
| min_score             | 0–100                                                                |
| UUID path params      | Validated by FastAPI; invalid → 422                                  |

# 10\. Rate Limiting

| **Scope**             | **Limit**                        | **Implementation**                                                                 |
| --------------------- | -------------------------------- | ---------------------------------------------------------------------------------- |
| POST /auth/login      | 10/min per IP                    | slowapi decorator                                                                  |
| POST /auth/register   | 5/min per IP                     | slowapi decorator                                                                  |
| POST /agent/search    | 5/hour and 15/day per user       | slowapi key_func = user id from JWT; plus DB count of agent_sessions as a backstop |
| Authenticated default | 120/min per user                 | slowapi default_limits                                                             |
| SerpApi global budget | SERP_DAILY_BUDGET live calls/day | SUM(agent_sessions.serp_calls_live) for today checked before each live call        |

429 responses use the standard error format with Retry-After. slowapi's in-memory storage resets on restart and is per-process — acceptable for the hackathon; the DB backstop protects SerpApi spend.

# 11\. Security

- bcrypt (cost 12) password hashing; generic login error message.
- Ownership enforced in services: every query on user-owned tables filters by user_id; cross-user access returns 403 or 404.
- CORS: CORS_ORIGINS exact origins; credentials not required (Bearer header).
- No secrets in responses or logs; SerpApi api_key excluded from serp_cache.params.
- Descriptions stored as plain text; frontend never renders HTML from sources.
- LLM prompts receive no name, email, or institution; job text passed as delimited data with an instruction to ignore embedded instructions.
- Security headers via middleware: X-Content-Type-Options: nosniff, Referrer-Policy: no-referrer.

# 12\. API Folder Structure

_backend/app_

```
backend/app/
├── main.py                  # create_app(): CORS, routers, handlers, /health
├── config.py                # Settings (pydantic-settings), MATCH_WEIGHTS
├── db.py
├── models/
│   ├── user.py              # User, UserProfile
│   ├── skill.py             # Skill, UserSkill, OpportunitySkill
│   ├── career_goal.py
│   ├── opportunity.py       # Opportunity, OpportunityMatch, SavedOpportunity
│   ├── application.py
│   ├── agent.py             # AgentSession, SearchHistory, SerpCache
│   └── roadmap.py           # SkillGap, Roadmap, RoadmapStep
├── schemas/                 # auth.py, profile.py, skill.py, agent.py, opportunity.py,
│                            # skill_gap.py, roadmap.py, application.py, history.py, error.py
├── api/
│   ├── deps.py
│   └── routes/
│       ├── auth.py          # POST /auth/register, POST /auth/login
│       ├── profile.py       # GET/PUT /profile
│       ├── skills.py        # GET /skills
│       ├── agent.py         # POST /agent/search, GET /agent/sessions/{id}
│       ├── opportunities.py # GET /opportunities, GET /opportunities/{id}, POST/DELETE save
│       ├── skill_gap.py     # GET /skill-gap
│       ├── roadmap.py       # GET /roadmap, PATCH /roadmap/steps/{id}
│       ├── applications.py  # GET/POST /applications, PUT /applications/{id}
│       └── search_history.py# GET /search/history
├── services/  agent/  search/  matching/  core/
└── tests/
    ├── test_auth.py  test_profile.py  test_opportunities.py
    ├── test_scorer.py  test_normalizer.py  test_gap.py
    └── fixtures/serpapi/    # REAL responses captured from SerpApi, committed for tests
```