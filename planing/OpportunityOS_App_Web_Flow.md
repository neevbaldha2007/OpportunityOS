**OpportunityOS**

**Application & Web Flow Specification**

_Screens, routes, transitions, and API interactions_

| **Document** | OpportunityOS_App_Web_Flow.docx                                                              |
| ------------ | -------------------------------------------------------------------------------------------- |
| **Product**  | OpportunityOS — AI Career & Opportunity Agent                                                |
| **Tagline**  | Discover opportunities. Understand the gap. Take the next step.                              |
| **Version**  | v1.0 (Hackathon baseline)                                                                    |
| **Date**     | 27 September 2026                                                                            |
| **Team**     | 4 members — Frontend (M1), Backend (M2), AI + SerpApi (M3), Database + Integration + QA (M4) |
| **Status**   | Approved for build                                                                           |

# Contents

1\. Overview

2\. Sitemap

3\. User Flow Diagram

4\. Authentication Flow

5\. AI Agent Flow

6\. Opportunity Application Flow

7\. Screen Specifications

8\. Global Behaviours

# 1\. Overview

This document specifies every screen, route, transition, and API interaction in OpportunityOS. It is the contract between the frontend (M1) and backend (M2/M3). Endpoint names match the Backend Database & API Specification exactly.

_Primary end-to-end flow_

```
Landing Page
↓
Signup/Login
↓
Profile Setup
↓
Career Goal
↓
Skills
↓
Location
↓
Preferences
↓
AI Career Agent
↓
SerpApi Search
↓
Normalize Results
↓
Opportunity Matching
↓
Skill Gap Analysis
↓
Personalized Roadmap
↓
Dashboard
```

Onboarding is one wizard at /onboarding with 4 steps: (1) Profile (education + experience), (2) Career Goal, (3) Skills, (4) Location & Preferences. Steps 9–15 of the flow happen server-side during the agent run and are surfaced as stages on the AI Agent Processing screen.

# 2\. Sitemap

_Route map_

```
/                         Landing (public)
/login                    Login (public)
/signup                   Signup (public)
/onboarding               Profile setup wizard (auth)
   ?step=profile | goal | skills | preferences
/agent/:sessionId         AI Agent Processing (auth)
/dashboard                Dashboard (auth, default after login if profile complete)
/opportunities            Search Results (auth)
/opportunities/:id        Opportunity Details + Match Explanation (auth)
/skill-gap                Skill Gap (auth)
/roadmap                  Learning Roadmap (auth)
/saved                    Saved Opportunities (auth)
/applications             Application Tracker (auth)
/profile                  Profile (auth)
/settings                 Settings (auth)
/history                  Search History (auth, linked from Settings/Profile)
*                         404
```

_Mermaid diagram — Sitemap (paste into mermaid.live, GitHub, or Notion to render)_

```
flowchart TD
  L[Landing /] --> LG[Login]
  L --> SU[Signup]
  SU --> OB[Onboarding wizard]
  LG -->|profile incomplete| OB
  LG -->|profile complete| DB[Dashboard]
  OB --> AG[AI Agent Processing]
  AG --> DB
  DB --> OP[Search Results]
  OP --> OD[Opportunity Details]
  OD --> ME[Match Explanation panel]
  DB --> SG[Skill Gap]
  DB --> RM[Roadmap]
  DB --> SV[Saved]
  DB --> AP[Application Tracker]
  DB --> PR[Profile]
  DB --> ST[Settings]
  ST --> HI[Search History]
```

# 3\. User Flow Diagram

_Mermaid diagram — User Flow (paste into mermaid.live, GitHub, or Notion to render)_

```
flowchart LR
  A[Visit landing] --> B{Has account?}
  B -- no --> C[Signup] --> D[Onboarding 4 steps]
  B -- yes --> E[Login] --> F{Profile complete?}
  F -- no --> D
  F -- yes --> G{Has completed session?}
  D --> H[Run AI Career Agent]
  G -- no --> H
  G -- yes --> I[Dashboard]
  H --> I
  I --> J[Browse opportunities] --> K[Open detail] --> L{Decision}
  L -- fit is good --> M[Save / Track / Apply on source]
  L -- gap too big --> N[Skill gap → Roadmap]
  N --> O[Complete steps] --> H
```

# 4\. Authentication Flow

_Mermaid diagram — Authentication Flow (paste into mermaid.live, GitHub, or Notion to render)_

```
sequenceDiagram
  participant U as User
  participant FE as React App
  participant API as FastAPI
  participant DB as PostgreSQL
  U->>FE: submit email + password
  FE->>API: POST /auth/login
  API->>DB: SELECT user by lower(email)
  API->>API: bcrypt verify
  alt valid
    API-->>FE: 200 {access_token, user, profile_complete}
    FE->>FE: store token, set AuthContext
    FE->>API: GET /profile (Authorization: Bearer)
    FE-->>U: route to /dashboard or /onboarding
  else invalid
    API-->>FE: 401 UNAUTHORIZED
    FE-->>U: inline error "Email or password is incorrect"
  end
  Note over FE,API: Any 401 on a protected call → clear token → /login?next=current_path
```

- Route guard ProtectedRoute checks token presence and expiry (decode exp client-side) before rendering.
- Post-login redirect honours ?next=.
- Logout clears token and TanStack Query cache.

# 5\. AI Agent Flow

_Mermaid diagram — AI Agent Flow (client perspective) (paste into mermaid.live, GitHub, or Notion to render)_

```
sequenceDiagram
  participant FE as React App
  participant API as FastAPI
  participant BG as BackgroundTask (Agent)
  FE->>API: POST /agent/search {overrides?}
  API->>API: validate profile, rate limit
  API-->>FE: 202 {session_id, status: "queued"}
  API->>BG: run_agent(session_id)
  FE->>FE: navigate /agent/:sessionId
  loop every 1.5 s until terminal status
    FE->>API: GET /agent/sessions/{id}
    API-->>FE: {status, stages[], warnings[]}
  end
  BG->>BG: plan → search → normalize → match → gap → roadmap
  FE->>FE: status completed|partial → /dashboard
  FE->>FE: status failed → error state with retry
```

| **Stage key**    | **UI label**                 | **Typical detail shown**                     |
| ---------------- | ---------------------------- | -------------------------------------------- |
| plan_queries     | Understanding your goal      | Number of queries planned                    |
| search           | Searching live opportunities | Engines queried, results found, cached count |
| normalize_dedupe | Cleaning and de-duplicating  | Unique opportunities                         |
| extract_skills   | Reading job requirements     | Skills identified                            |
| match            | Scoring your fit             | Best match %                                 |
| skill_gap        | Finding your skill gaps      | Top missing skill                            |
| roadmap          | Building your roadmap        | Number of steps                              |

# 6\. Opportunity Application Flow

_Mermaid diagram — Opportunity Application Flow (paste into mermaid.live, GitHub, or Notion to render)_

```
stateDiagram-v2
  [*] --> Discovered
  Discovered --> Saved: POST /opportunities/{id}/save
  Saved --> Discovered: DELETE /opportunities/{id}/save
  Discovered --> planned: POST /applications
  Saved --> planned: POST /applications
  planned --> applied: PUT /applications/{id}
  applied --> interviewing
  interviewing --> offer
  applied --> rejected
  interviewing --> rejected
  planned --> withdrawn
  applied --> withdrawn
  offer --> [*]
  rejected --> [*]
  withdrawn --> [*]
```

1. User clicks "Apply on source" → original link opens in new tab; app shows a toast "Did you apply? Track it" with a one-click action.
2. Tracking creates an Application with status planned or applied (user chooses).
3. Status changes are made from the tracker or detail page via PUT /applications/{id}.

# 7\. Screen Specifications

Each screen lists purpose, inputs, components, actions, API calls, expected response, navigation, and loading/empty/error states.

## 7.1 1. Landing Page

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Explain the promise and convert visitors to signup.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>None</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Top nav (logo, Login, Get started)</p><p>Hero: tagline, sub-copy, primary CTA</p><p>"How it works" 3 steps: Discover · Understand the gap · Take the next step</p><p>Illustrative sample match card (clearly labelled "Example")</p><p>Footer: team, hackathon, privacy note</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Get started → /signup; Login → /login</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><p>None</p></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>—</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>/signup, /login; logged-in users are redirected to /dashboard</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>Static; no loading state</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>N/A</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>N/A</p></td></tr></tbody></table></div>

## 7.2 2. Login

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/login</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Authenticate returning users.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>Email, password</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Email input</p><p>Password input with show/hide</p><p>Primary button "Log in"</p><p>Link to signup</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Submit; switch to signup</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><pre><code>POST /auth/login</code></pre></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>200 {access_token, token_type, expires_in, user{id, full_name, email}, profile_complete}</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>profile_complete ? /dashboard (or ?next) : /onboarding</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>Button spinner, inputs disabled</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>N/A</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>401 → "Email or password is incorrect"; 429 → "Too many attempts, wait a minute"; network → toast with retry</p></td></tr></tbody></table></div>

## 7.3 3. Signup

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/signup</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Create an account.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>Full name, email, password, confirm password, consent checkbox (privacy note)</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Form with inline validation</p><p>Password strength hint (≥ 8 chars)</p><p>Privacy note: data shared with LLM provider and SerpApi (no name/email)</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Submit; switch to login</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><pre><code>POST /auth/register</code></pre></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>201 {access_token, token_type, expires_in, user}</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>→ /onboarding?step=profile</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>Button spinner</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>N/A</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>409 → "Account exists — log in instead"; 422 → field errors</p></td></tr></tbody></table></div>

## 7.4 4. Profile Setup (Onboarding Step 1)

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/onboarding?step=profile</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Capture education and experience.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>Education level (select), degree, field of study, graduation year, institution (optional), experience level (student | fresher | 0-1 years | 1-2 years)</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Stepper (1 of 4)</p><p>Selects and text inputs</p><p>Back / Next buttons</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Next (client-side validation), Back</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><p>None until final step (wizard state held client-side; saved on step 4). Optional: PUT /profile partial save on each step <strong>[PHASE 2]</strong></p></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>—</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>→ step=goal</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>N/A</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>Fields prefilled if GET /profile returns data</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>Inline field validation</p></td></tr></tbody></table></div>

## 7.5 5. Career Goal Setup (Onboarding Step 2)

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/onboarding?step=goal</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Define target role and goal.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>Target role (autocomplete from common roles + free text), goal statement (optional, 280 chars), timeline (1 / 3 / 6 months)</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Role combobox with suggestions (Frontend Developer, Backend Developer, Data Analyst, …)</p><p>Textarea</p><p>Segmented control for timeline</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Next, Back</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><p>None (client state)</p></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>—</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>→ step=skills</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>N/A</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>Role suggestions shown by default</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>Target role required</p></td></tr></tbody></table></div>

## 7.6 6. Skill Selection (Onboarding Step 3)

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/onboarding?step=skills</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Capture current skills and proficiency.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>Skills (multi-select), proficiency 1–5 per skill</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Skill search box with autocomplete</p><p>Selected skill chips with proficiency stepper</p><p>Suggested skills for the chosen role (static list per role in frontend constants)</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Add/remove skill, set proficiency, Next, Back</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><p>GET /skills?q=react&amp;limit=10 (debounced 250 ms)</p></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>200 {items:[{id, name, category}]}</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>→ step=preferences</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>Spinner inside dropdown</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>"No match — press Enter to add '&lt;text&gt;' as a custom skill"</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>Autocomplete failure → allow free-text; at least 1 skill required</p></td></tr></tbody></table></div>

## 7.7 7. Opportunity Preferences (Onboarding Step 4 — Location & Preferences)

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/onboarding?step=preferences</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Capture location and opportunity preferences, then save profile.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>City/state (text with suggestions), open to remote (toggle), opportunity types (internship, full_time, part_time, contract), weekly learning hours</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Location input</p><p>Remote toggle</p><p>Type checkboxes</p><p>Hours slider</p><p>Primary button "Save &amp; find opportunities"</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Save profile then start agent</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><p>PUT /profile → then POST /agent/search</p></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>PUT 200 {profile…}; POST 202 {session_id, status:"queued"}</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>→ /agent/:sessionId</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>Button spinner "Saving profile…"</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>N/A</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>422 → highlight step with error; 429 on agent → toast "Search limit reached" and go to /dashboard</p></td></tr></tbody></table></div>

## 7.8 8. AI Agent Processing

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/agent/:sessionId</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Show the agent working in real time; build trust.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>None</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Stage timeline (7 stages) with status icons: pending / running / done / warning</p><p>Live counters (queries planned, results found, unique opportunities, best match %)</p><p>Queries list (engine badge + query text) as they are planned</p><p>Cancel link (navigates away; run continues server-side)</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Wait; View results (enabled on completion)</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><p>GET /agent/sessions/{id} polled every 1.5 s</p></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>200 {id, status, stages:[{key, status, started_at, duration_ms, detail}], warnings[], result_summary?}</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>completed|partial → /dashboard (auto after 1.5 s); failed → stay with error</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>This screen is the loading state; skeleton for counters</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>status completed but 0 opportunities → message with suggestions (enable remote, broaden role) and button "Edit preferences"</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>failed → "We could not complete the search" + reason code + Retry (POST /agent/search) ; partial → warning banner listing skipped sources</p></td></tr></tbody></table></div>

## 7.9 9. Dashboard

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/dashboard</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Home: summary of latest results and next steps.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>None</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Greeting + target role + "Last searched X ago" + Run new search</p><p>KPI tiles: opportunities found, best match, saved, roadmap progress</p><p>Top 6 opportunity cards</p><p>Skill gap bars (top 5)</p><p>Next 2 roadmap steps</p><p>Market signals (news, max 3)</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Open card, save, view all, open gap/roadmap, run new search</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><p>GET /opportunities?page=1&amp;page_size=6&amp;sort=score, GET /skill-gap, GET /roadmap, GET /agent/sessions/{latest_id} (for news + counts; id from GET /search/history?page_size=1)</p></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>See API spec for each</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>Cards → /opportunities/:id; View all → /opportunities; gap → /skill-gap; roadmap → /roadmap</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>Skeleton cards and bars</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>No completed session → hero "Run your first search" CTA</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>Per-widget error with retry; page remains usable</p></td></tr></tbody></table></div>

## 7.10 10. Search Results

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/opportunities</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Browse, filter, and sort all matched opportunities for the latest session.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>Filters: type, remote only, min score, source engine; sort: score | recent</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Filter bar</p><p>Result count</p><p>Opportunity card grid (title, company, location, type, match ring, 3 skill chips, save icon)</p><p>Pagination</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Filter, sort, paginate, save, open detail</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><pre><code>GET /opportunities?session_id=&amp;type=&amp;remote=&amp;min_score=&amp;sort=&amp;page=&amp;page_size=</code></pre></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>200 {items:[OpportunityCard], page, page_size, total}</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>→ /opportunities/:id</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>Skeleton grid</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>No items for filters → "Clear filters" button</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>Inline error with retry</p></td></tr></tbody></table></div>

## 7.11 11. Opportunity Details

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/opportunities/:id</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Full context to decide: apply or learn.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>None</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Header: title, company, location, remote badge, type, source (via), posted text, fetched date</p><p>Match ring + "Why this score" button</p><p>Skill checklist ✓/✗ with required/preferred tags</p><p>Highlights and description (plain text, collapsible)</p><p>Actions: Save, Track, Apply on source (external)</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Save/unsave, track, apply externally, open match explanation</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><p>GET /opportunities/{id}, POST|DELETE /opportunities/{id}/save, POST /applications</p></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>200 {opportunity, match{score, breakdown, matched_skills, missing_skills}, saved, application?}</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>Back to results; external apply_url in new tab</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>Skeleton header + body</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>Description missing → "Description not provided by source"</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>404 → "Opportunity not found" + back link</p></td></tr></tbody></table></div>

## 7.12 12. Match Explanation

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/opportunities/:id (side panel / modal)</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Show exactly how the match % was computed.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>None</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Component table: Skills (50%), Role (15%), Location (15%), Experience (10%), Type (10%) with component score and weighted points</p><p>Matched vs missing skills with weights (required 1.0, preferred 0.5)</p><p>Confidence note if no skills listed</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Close; jump to skill gap for a missing skill</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><p>None (data from GET /opportunities/{id})</p></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>—</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>Missing skill → /skill-gap?skill=&lt;id&gt;</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>N/A</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>Low-confidence message if skills not listed</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>N/A</p></td></tr></tbody></table></div>

## 7.13 13. Skill Gap

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/skill-gap</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Prioritized missing skills across top matches.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>Optional query ?skill= to highlight</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Ranked list: skill, priority badge, "appears in X of Y top matches", avg score uplift, bar</p><p>Expandable: list of opportunities needing this skill</p><p>CTA "See roadmap"</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Expand, open opportunity, go to roadmap</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><pre><code>GET /skill-gap?session_id=</code></pre></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>200 {session_id, top_n, items:[{skill, priority, demand_count, demand_pct, avg_uplift, opportunity_ids}]}</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>→ /roadmap, → /opportunities/:id</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>Skeleton bars</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>"No gaps found — you match the listed skills. Focus on applying."</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>Retry</p></td></tr></tbody></table></div>

## 7.14 14. Learning Roadmap

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/roadmap</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Sequenced learn → build → apply plan.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>Step completion checkbox</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Header: title, summary, total weeks, progress bar</p><p>Vertical timeline of steps: type badge (learn/build/apply), title, skill, est. hours, why (reason), action, resource query (copy / search button)</p><p>Apply steps link to specific opportunities</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Mark step done/undone</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><p>GET /roadmap, PATCH /roadmap/steps/{id} (added endpoint)</p></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>200 {roadmap{…, steps[]}}</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>Apply step → /opportunities/:id</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>Skeleton timeline</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>No roadmap → CTA run agent</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>Retry; step toggle failure reverts optimistically</p></td></tr></tbody></table></div>

Step completion needs a write endpoint that was not in the original brief: PATCH /roadmap/steps/{id} is documented in the API specification as an added MVP endpoint.

## 7.15 15. Saved Opportunities

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/saved</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Shortlist management.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>Filter by type</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>List/grid of saved cards with saved date and tracker status badge</p><p>Unsave icon</p><p>Track button</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Unsave, track, open detail</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><p>GET /opportunities?saved=true, DELETE /opportunities/{id}/save, POST /applications</p></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>200 {items, page, page_size, total}</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>→ detail, → /applications</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>Skeleton</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>"Nothing saved yet — save opportunities from your results"</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>Retry</p></td></tr></tbody></table></div>

## 7.16 16. Application Tracker

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/applications</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Track application status.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>Status changes, notes, applied_on date</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Columns (desktop) / grouped list (mobile): planned, applied, interviewing, offer, rejected, withdrawn</p><p>Card: title, company, status dropdown, applied date, notes icon</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Change status, edit notes</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><p>GET /applications, PUT /applications/{id}</p></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>200 {items:[Application]}</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>Card → /opportunities/:id</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>Skeleton columns</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>"No applications tracked yet"</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>Optimistic update revert + toast</p></td></tr></tbody></table></div>

## 7.17 17. Profile

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/profile</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>View and edit profile, skills, goal, preferences.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>Same fields as onboarding</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Sections: Education, Career goal, Skills, Location &amp; preferences</p><p>Edit per section</p><p>Banner "Profile changed — re-run search for updated matches"</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Save, re-run agent</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><p>GET /profile, PUT /profile, GET /skills, POST /agent/search</p></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>See API spec</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>Re-run → /agent/:sessionId</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>Skeleton</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>N/A (profile exists after onboarding)</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>Field errors; save failure toast</p></td></tr></tbody></table></div>

## 7.18 18. Settings

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Route</strong></p></th><th><pre><code>/settings</code></pre></th></tr><tr><td><p><strong>Purpose</strong></p></td><td><p>Account settings and history.</p></td></tr><tr><td><p><strong>User inputs</strong></p></td><td><p>Theme (light/dark), logout</p></td></tr><tr><td><p><strong>UI components</strong></p></td><td><p>Account info (read-only email)</p><p>Theme toggle (localStorage)</p><p>Search history link</p><p>Privacy: what is shared with third parties</p><p>Logout</p><p>Delete account (Phase 2 — shows instructions in MVP)</p></td></tr><tr><td><p><strong>Actions</strong></p></td><td><p>Toggle theme, open history, logout</p></td></tr><tr><td><p><strong>API calls</strong></p></td><td><p>GET /search/history (on /history page)</p></td></tr><tr><td><p><strong>Expected response</strong></p></td><td><p>200 {items:[{session_id, created_at, status, queries:[…]}]}</p></td></tr><tr><td><p><strong>Navigation</strong></p></td><td><p>→ /history, → / after logout</p></td></tr><tr><td><p><strong>Loading state</strong></p></td><td><p>N/A</p></td></tr><tr><td><p><strong>Empty state</strong></p></td><td><p>History empty → "No searches yet"</p></td></tr><tr><td><p><strong>Error state</strong></p></td><td><p>Retry</p></td></tr></tbody></table></div>

# 8\. Global Behaviours

| **Concern**    | **Behaviour**                                                                             |
| -------------- | ----------------------------------------------------------------------------------------- |
| Auth expiry    | Any 401 → clear token → /login?next=                                                      |
| Toasts         | Success (save, track), warning (partial results), error (network)                         |
| Stale results  | If profile.updated_at > latest session.created_at → banner on dashboard                   |
| External links | Open in new tab with rel="noopener noreferrer"                                            |
| Deep links     | All auth routes deep-linkable after login                                                 |
| Analytics      | **\[PHASE 2\]** basic event tracking (search_started, opportunity_opened, saved, tracked) |