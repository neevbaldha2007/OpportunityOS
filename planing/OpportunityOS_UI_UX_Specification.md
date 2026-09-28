**OpportunityOS**

**UI/UX Design Specification**

_Design system, components, and screen wireframes_

| **Document** | OpportunityOS_UI_UX_Specification.docx                                                       |
| ------------ | -------------------------------------------------------------------------------------------- |
| **Product**  | OpportunityOS — AI Career & Opportunity Agent                                                |
| **Tagline**  | Discover opportunities. Understand the gap. Take the next step.                              |
| **Version**  | v1.0 (Hackathon baseline)                                                                    |
| **Date**     | 27 September 2026                                                                            |
| **Team**     | 4 members — Frontend (M1), Backend (M2), AI + SerpApi (M3), Database + Integration + QA (M4) |
| **Status**   | Approved for build                                                                           |

# Contents

1\. UX Goals

2\. Design Principles

3\. Brand Identity

4\. Color System

5\. Typography

6\. Spacing

7\. Grid

8\. Buttons

9\. Cards

10\. Forms

11\. Navigation

12\. Modals

13\. Toasts

14\. Loading States

15\. Empty States

16\. Error States

17\. Accessibility

18\. Responsive Design

19\. Screen Specifications & Wireframes

20\. Design Handoff Checklist

# 1\. UX Goals

1. **Time to value under 3 minutes:** signup → onboarding → first results.
2. **Trust through transparency:** every number is explainable in one click.
3. **Clarity over density:** one primary action per screen.
4. **Momentum:** every screen ends with a next step (save, learn, apply, track).
5. **Demo-ready:** the agent run is visually legible from the back of a room.

# 2\. Design Principles

| **Principle**             | **In practice**                                                                         |
| ------------------------- | --------------------------------------------------------------------------------------- |
| Show the work             | Agent stages, queries, and score breakdowns are visible, not hidden                     |
| Honest AI                 | Low-confidence scores are labelled; examples are labelled "Example"; no fabricated data |
| Progressive disclosure    | Cards show 3 skills; details show all; breakdown on demand                              |
| Student-friendly language | "You have 3 of 5 skills" instead of "coverage ratio 0.6"                                |
| Consistent status colour  | Green = have/match, amber = partial/medium, red-rose = missing/high-priority gap        |
| Mobile-first layouts      | Single column at 360 px; grids expand at md/lg                                          |

# 3\. Brand Identity

| **Name**           | OpportunityOS                                                                                                                                       |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tagline**        | Discover opportunities. Understand the gap. Take the next step.                                                                                     |
| **Personality**    | Smart, calm, encouraging, precise — a capable senior mentor, not a hype machine                                                                     |
| **Logo (MVP)**     | Wordmark "Opportunity" in slate-900 + "OS" in indigo-600, Inter 700; favicon: rounded indigo square with "O"                                        |
| **Voice examples** | "You match 4 of 6 listed skills." · "React appears in 9 of your top 15 matches — start there." · "Search limit reached. Showing your last results." |
| **Avoid**          | Exclamation-heavy copy, "guaranteed", "dream job", emojis in data areas                                                                             |

# 4\. Color System

| **Token**     | **Tailwind** | **Hex** | **Usage**                                      |
| ------------- | ------------ | ------- | ---------------------------------------------- |
| primary       | indigo-600   | #4F46E5 | Primary buttons, links, active nav, focus ring |
| primary-hover | indigo-700   | #4338CA | Hover/pressed                                  |
| primary-soft  | indigo-50    | #EEF2FF | Selected chips, highlight backgrounds          |
| accent        | violet-500   | #8B5CF6 | AI agent accents, gradients (sparingly)        |
| success       | emerald-600  | #059669 | Matched skill ✓, high match ≥ 75%              |
| warning       | amber-500    | #F59E0B | Medium match 50–74%, partial warnings          |
| danger        | rose-600     | #E11D48 | Missing skill ✗, errors, high-priority gap     |
| text          | slate-900    | #0F172A | Primary text                                   |
| text-muted    | slate-500    | #64748B | Secondary text                                 |
| border        | slate-200    | #E2E8F0 | Card and input borders                         |
| surface       | white        | #FFFFFF | Cards                                          |
| background    | slate-50     | #F8FAFC | App background                                 |
| dark-bg       | slate-950    | #020617 | Dark mode background                           |
| dark-surface  | slate-900    | #0F172A | Dark mode cards                                |

| **Match band** | **Range** | **Colour**  | **Label**     |
| -------------- | --------- | ----------- | ------------- |
| High           | 75–100%   | emerald-600 | Strong match  |
| Medium         | 50–74%    | amber-500   | Partial match |
| Low            | 0–49%     | slate-400   | Stretch       |

Never convey match level by colour alone; always show the number and label (accessibility).

# 5\. Typography

| **Style** | **Tailwind**         | **Size / line-height** | **Weight** | **Use**                       |
| --------- | -------------------- | ---------------------- | ---------- | ----------------------------- |
| Display   | text-4xl md:text-5xl | 36/40 → 48/52          | 800        | Landing hero                  |
| H1        | text-3xl             | 30/36                  | 700        | Page titles                   |
| H2        | text-2xl             | 24/32                  | 600        | Section titles                |
| H3        | text-lg              | 18/28                  | 600        | Card titles                   |
| Body      | text-base            | 16/24                  | 400        | Default text                  |
| Small     | text-sm              | 14/20                  | 400/500    | Meta, labels                  |
| Caption   | text-xs              | 12/16                  | 500        | Badges, helper text           |
| Numeric   | tabular-nums         | —                      | 700        | Match %, counts               |
| Mono      | font-mono text-sm    | 14/20                  | 400        | Queries shown in agent screen |

Font family: **Inter** (Google Fonts) with system fallback ui-sans-serif, system-ui. Mono: **JetBrains Mono** or ui-monospace.

# 6\. Spacing

4-px base scale (Tailwind default). Common: 2 (8 px) inside chips, 4 (16 px) card padding mobile, 6 (24 px) card padding desktop, 8 (32 px) between sections, 12–16 (48–64 px) landing sections. Card radius rounded-xl (12 px); buttons/inputs rounded-lg (8 px); chips rounded-full.

# 7\. Grid

| **Breakpoint** | **Width** | **Columns** | **Container**          | **Card grid**                       |
| -------------- | --------- | ----------- | ---------------------- | ----------------------------------- |
| base           | < 640 px  | 4           | px-4                   | 1 column                            |
| sm             | ≥ 640 px  | 8           | px-6                   | 1 column                            |
| md             | ≥ 768 px  | 12          | px-6                   | 2 columns                           |
| lg             | ≥ 1024 px | 12          | max-w-6xl mx-auto px-8 | 3 columns; sidebar nav appears      |
| xl             | ≥ 1280 px | 12          | max-w-7xl              | 3 columns + right rail on dashboard |

# 8\. Buttons

| **Variant** | **Classes (core)**                                                            | **Use**                        |
| ----------- | ----------------------------------------------------------------------------- | ------------------------------ |
| Primary     | bg-indigo-600 text-white hover:bg-indigo-700 h-10 px-4 rounded-lg font-medium | One per view: main action      |
| Secondary   | bg-white border border-slate-300 text-slate-800 hover:bg-slate-50             | Alternative actions            |
| Ghost       | text-indigo-600 hover:bg-indigo-50                                            | Tertiary, inline               |
| Danger      | bg-rose-600 text-white hover:bg-rose-700                                      | Destructive (withdraw, delete) |
| Icon        | h-9 w-9 rounded-lg + aria-label                                               | Save (bookmark), close         |
| AI CTA      | Primary + sparkle icon + subtle indigo→violet gradient                        | "Find my opportunities" only   |

States: default, hover, focus-visible (ring-2 ring-indigo-500 ring-offset-2), disabled (opacity-50 cursor-not-allowed), loading (spinner replaces icon, label kept, width locked). Sizes: sm h-8, md h-10, lg h-12.

# 9\. Cards

| **Element**      | **Specification**                                                                                                                                                                 |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Base             | bg-white border border-slate-200 rounded-xl p-4 md:p-6 shadow-sm hover:shadow-md transition                                                                                       |
| Opportunity card | Title (H3, 2-line clamp), company · location, type badge + remote badge, match ring (48 px) top-right, 3 skill chips (✓ green / ✗ rose), footer: source + posted text + save icon |
| KPI tile         | Label (text-sm muted), value (text-3xl tabular-nums bold), optional delta                                                                                                         |
| Gap card         | Skill name, priority badge, bar, "in X of Y top matches"                                                                                                                          |
| Roadmap step     | Left timeline dot coloured by type (learn indigo / build violet / apply emerald), content card on right                                                                           |

# 10\. Forms

| **Element**             | **Specification**                                                                                                                    |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Input                   | h-10 rounded-lg border-slate-300 focus:ring-2 focus:ring-indigo-500; label above (text-sm font-medium); helper below (text-xs muted) |
| Error                   | border-rose-500, message text-xs text-rose-600 with icon; aria-invalid + aria-describedby                                            |
| Combobox (skills, role) | Headless UI / Radix-style combobox; keyboard: ↑↓ Enter Esc; Enter on no match adds custom item                                       |
| Chips                   | Selected skills as removable chips with proficiency stepper (1–5 dots)                                                               |
| Stepper                 | 4 steps with labels; completed steps clickable                                                                                       |
| Validation timing       | On blur and on submit; never on first keystroke                                                                                      |

# 11\. Navigation

| **Element**        | **Specification**                                                                                                 |
| ------------------ | ----------------------------------------------------------------------------------------------------------------- |
| Public             | Top bar: logo left; Login + Get started right                                                                     |
| App desktop (≥ lg) | Left sidebar 240 px: Dashboard, Opportunities, Skill Gap, Roadmap, Saved, Applications; bottom: Profile, Settings |
| App mobile         | Top bar with logo + avatar; bottom tab bar: Home, Jobs, Roadmap, Saved, More                                      |
| Active state       | bg-indigo-50 text-indigo-700 + left 3-px indicator                                                                |
| Global CTA         | "Run new search" in top bar on dashboard/results                                                                  |

# 12\. Modals

Used only for: match explanation (side sheet on desktop, bottom sheet on mobile), track application form, confirm destructive actions. Max width 560 px, overlay bg-slate-900/40, focus trapped, Esc closes, returns focus to trigger.

# 13\. Toasts

| **Type** | **Example**                                         | **Duration**                 |
| -------- | --------------------------------------------------- | ---------------------------- |
| Success  | Saved to your list                                  | 3 s                          |
| Info     | Using cached results from 2 hours ago               | 4 s                          |
| Warning  | Google News was skipped — results may be incomplete | 6 s                          |
| Error    | Could not save. Retry                               | Until dismissed, with action |

Position: bottom-right desktop, top on mobile. Max 3 stacked. role="status" (info/success) or role="alert" (error).

# 14\. Loading States

- Skeletons (animate-pulse slate-200 blocks) matching final layout for lists, cards, dashboard widgets.
- Button-level spinners for form submits.
- Agent screen: dedicated stage timeline — the showcase loading state.
- Never show a blank page; never block the whole app for one widget.
- Respect prefers-reduced-motion: disable pulse and ring animations.

# 15\. Empty States

| **Context**     | **Message**                                        | **Action**            |
| --------------- | -------------------------------------------------- | --------------------- |
| No search yet   | Let's find opportunities that fit you.             | Find my opportunities |
| Zero results    | No listings matched. Try remote or a related role. | Edit preferences      |
| No gaps         | You match the listed skills. Focus on applying.    | View top matches      |
| No saved        | Save opportunities to build your shortlist.        | Browse results        |
| No applications | Track applications to never miss a follow-up.      | Go to saved           |

# 16\. Error States

- Inline (field) → form errors.
- Widget-level card with icon, one-sentence cause, Retry button.
- Page-level (404/500) with illustration-free message and a route home.
- Agent failure: show which stage failed and the error code in muted text for debugging during the demo.

# 17\. Accessibility

- WCAG 2.1 AA contrast (text ≥ 4.5:1). indigo-600 on white passes; avoid amber text on white — use amber for fills with dark text.
- All interactive elements reachable by keyboard; visible focus ring.
- Match ring has aria-label="Match 87 percent, strong match".
- Skill ✓/✗ include text ("Has React" / "Missing React") for screen readers.
- Form inputs have associated labels; errors linked via aria-describedby.
- Agent stage updates announced via aria-live="polite".
- Minimum tap target 44 × 44 px on mobile.

# 18\. Responsive Design

| **Screen** | **Mobile (360–767)**                         | **Tablet (768–1023)** | **Desktop (≥ 1024)**                                   |
| ---------- | -------------------------------------------- | --------------------- | ------------------------------------------------------ |
| Dashboard  | Stacked: KPIs 2×2, cards 1 col, gap, roadmap | Cards 2 col           | Sidebar + 3-col cards + right rail (gap, roadmap)      |
| Results    | Filters in bottom sheet                      | Filters row           | Filters row + 3-col grid                               |
| Detail     | Single column; sticky bottom action bar      | Single column         | 2 columns: content + sticky side card (score, actions) |
| Tracker    | Grouped list by status                       | Grouped list          | 6 columns board                                        |
| Agent      | Timeline full width                          | Timeline + counters   | Timeline left, counters + queries right                |

# 19\. Screen Specifications & Wireframes

Wireframes use ASCII-safe symbols so they align in any monospace font. Legend: + have / done · x missing · # filled bar · . empty bar · @ running · o pending · \* proficiency dot. In the UI these render as ✓, ✗, progress bars, and icons per the component specs.

## 19.1 Landing Page

_Wireframe — Landing (desktop)_

```
┌──────────────────────────────────────────────────────────────┐
│ OpportunityOS                          Login   [Get started] │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   Discover opportunities.                ┌────────────────┐  │
│   Understand the gap.                    │ EXAMPLE        │  │
│   Take the next step.                    │ Frontend Intern│  │
│                                          │ Remote    87%  │  │
│   An AI career agent that finds live     │ + HTML + CSS   │  │
│   openings, explains your fit, and       │ x React        │  │
│   builds your learning roadmap.          └────────────────┘  │
│                                                              │
│   [ Find my opportunities → ]                                │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  1 Discover        2 Understand the gap     3 Take next step │
│  Live search via   Transparent match %      Roadmap + apply  │
│  Google Jobs,      and missing skills       + track          │
│  Search, News                                                │
└──────────────────────────────────────────────────────────────┘
```

| **Element** | **Specification**                                               |
| ----------- | --------------------------------------------------------------- |
| Hero        | Display type, 2 CTAs max; example card labelled EXAMPLE         |
| Trust strip | "Powered by live search via SerpApi" + "Scores are explainable" |
| Performance | No heavy images; LCP < 2 s                                      |

## 19.2 Login

_Wireframe — Login_

```
┌──────────────────────────────┐
│        OpportunityOS         │
│   Welcome back               │
│                              │
│   Email                      │
│   [______________________]   │
│   Password                   │
│   [__________________] (eye) │
│                              │
│   [        Log in        ]   │
│   New here? Create account   │
└──────────────────────────────┘
```

| **Element** | **Specification**                                                    |
| ----------- | -------------------------------------------------------------------- |
| Layout      | Centered card max-w-sm; background slate-50                          |
| Errors      | Single form-level alert for 401 (do not reveal which field is wrong) |

## 19.3 Signup

_Wireframe — Signup_

```
┌──────────────────────────────┐
│   Create your account        │
│   Full name  [____________]  │
│   Email      [____________]  │
│   Password   [____________]  │
│   ###.. strength             │
│   [x] I understand my career │
│       data is processed by an│
│       AI provider and SerpApi│
│   [    Create account    ]   │
│   Already have one? Log in   │
└──────────────────────────────┘
```

| **Element** | **Specification**                                      |
| ----------- | ------------------------------------------------------ |
| Consent     | Checkbox required; link to privacy section in Settings |

## 19.4 Profile Setup (Onboarding)

_Wireframe — Onboarding — Step 3 Skills_

```
┌──────────────────────────────────────────────┐
│ *───*───@───o   Step 3 of 4: Your skills     │
├──────────────────────────────────────────────┤
│ Search skills                                │
│ [ reac|                                  ]   │
│   ┌──────────────────────┐                   │
│   │ React        Frontend│                   │
│   │ React Native Mobile  │                   │
│   └──────────────────────┘                   │
│ Your skills                                  │
│ (HTML ****o x) (CSS ***oo x)                 │
│ (JavaScript ***oo x)                         │
│                                              │
│ Suggested for Frontend Developer:            │
│ + React  + Git  + TypeScript  + REST API     │
│                                              │
│ [ Back ]                        [ Next → ]   │
└──────────────────────────────────────────────┘
```

| **Element** | **Specification**                                                                                            |
| ----------- | ------------------------------------------------------------------------------------------------------------ |
| Stepper     | Profile · Goal · Skills · Preferences                                                                        |
| Proficiency | 5 dots; tooltip labels: Aware, Beginner, Working, Strong, Expert                                             |
| Suggestions | Static per-role list; adding a suggestion does not imply the user has it at high proficiency (defaults to 2) |

## 19.5 AI Agent Screen

_Wireframe — AI Agent Processing_

```
┌──────────────────────────────────────────────────────────────┐
│ Finding opportunities for: Frontend Developer · Ahmedabad    │
├───────────────────────────────┬──────────────────────────────┤
│ + Understanding your goal     │  Queries planned: 5          │
│ + Searching live opportunities│  Results found:   41         │
│   google_jobs +  google +     │  Unique:          28         │
│   google_news +               │  Best match:      —          │
│ @ Reading job requirements…   │                              │
│ o Scoring your fit            │  Queries                     │
│ o Finding skill gaps          │  [jobs] frontend developer   │
│ o Building your roadmap       │         internship ahmedabad │
│                               │  [jobs] react intern remote  │
│                               │  [news] frontend hiring india│
└───────────────────────────────┴──────────────────────────────┘
(Numbers illustrative — rendered from GET /agent/sessions/{id})
```

| **Element**   | **Specification**                                                                                        |
| ------------- | -------------------------------------------------------------------------------------------------------- |
| Stage icons   | ○ pending (slate-300), ◉ running (indigo, pulsing), ✓ done (emerald), ! warning (amber), × failed (rose) |
| Counters      | Animate count-up; tabular numerals                                                                       |
| Engine badges | jobs = indigo, search = slate, news = violet                                                             |
| Duration      | Show elapsed seconds; after 45 s show "Taking longer than usual…"                                        |

## 19.6 Dashboard

_Wireframe — Dashboard (desktop)_

```
┌───────────┬──────────────────────────────────────────────────┐
│ Opportunity│ Hello, Riya                  [ Run new search ] │
│ OS        │ Target: Frontend Developer · last search 2h ago  │
│           ├──────────┬──────────┬──────────┬─────────────────┤
│ Dashboard │ Found 28 │ Best 87% │ Saved 3  │ Roadmap 25%     │
│ Opportun. ├──────────┴──────────┴──────────┼─────────────────┤
│ Skill Gap │ Recommended opportunities      │ Skill gap       │
│ Roadmap   │ ┌──────────┐┌──────────┐┌─────┐│ React   #######.│
│ Saved     │ │React     ││Frontend  ││ ... ││ REST API ####...│
│ Applicat. │ │Intern 87%││Intern 81%││     ││ Git     ###.....│
│           │ │Remote    ││Ahmedabad ││     │├─────────────────┤
│ Profile   │ └──────────┘└──────────┘└─────┘│ Next steps      │
│ Settings  │ [ View all 28 → ]              │ 1 Learn React   │
│           │ Market signals (news)          │ 2 Build project │
└───────────┴────────────────────────────────┴─────────────────┘
```

| **Element** | **Specification**                                                |
| ----------- | ---------------------------------------------------------------- |
| KPI tiles   | 4 tiles; values from latest session                              |
| Cards       | Top 6 by score                                                   |
| Right rail  | Gap (top 5) + next 2 roadmap steps                               |
| News        | Max 3; source + date; opens externally; labelled "Market signal" |

## 19.7 Opportunity Cards

_Wireframe — Opportunity card_

```
┌─────────────────────────────────────┐
│ Frontend Developer Intern     (87%) │
│ Company · Ahmedabad / Remote        │
│ [Internship] [Remote]               │
│ + HTML  + JavaScript  x React  +3   │
│ via LinkedIn · 3 days ago    [save] │
└─────────────────────────────────────┘
```

| **Element**    | **Specification**                                         |
| -------------- | --------------------------------------------------------- |
| Match ring     | SVG circle, stroke colour by band, number centered        |
| Skill chips    | Show up to 3: missing required first, then matched        |
| Low confidence | If no skills extracted: chip "Skills not listed" in slate |

## 19.8 Opportunity Detail

_Wireframe — Opportunity detail (desktop)_

```
┌──────────────────────────────────────────┬──────────────────┐
│ ← Back to results                        │  ┌────────────┐  │
│ Frontend Developer Intern                │  │    87%     │  │
│ Company · Ahmedabad · Remote OK          │  │Strong match│  │
│ via <source> · posted 3 days ago         │  └────────────┘  │
│                                          │ [Why this score] │
│ Skills                                   │ [ Save ]         │
│ + HTML (required)   x React (required)   │ [ Track ]        │
│ + CSS  (required)   x REST API (pref.)   │ [Apply on source]│
│ + JavaScript (required)                  │                  │
│                                          │                  │
│ Highlights                               │                  │
│ - Qualifications …                       │                  │
│ Description (expand)                     │                  │
└──────────────────────────────────────────┴──────────────────┘
```

## 19.9 Match Score

_Wireframe — Match explanation sheet_

```
┌──────────────────────────────────────────────┐
│ Why 87%?                                  x  │
├───────────────┬────────┬────────┬────────────┤
│ Component     │ Weight │ Score  │ Points     │
├───────────────┼────────┼────────┼────────────┤
│ Skills        │  50%   │ 0.74   │ 37.0       │
│ Role fit      │  15%   │ 1.00   │ 15.0       │
│ Location      │  15%   │ 1.00   │ 15.0       │
│ Experience    │  10%   │ 1.00   │ 10.0       │
│ Type          │  10%   │ 1.00   │ 10.0       │
├───────────────┴────────┴────────┼────────────┤
│ Total                           │ 87         │
└─────────────────────────────────┴────────────┘
(Values illustrative; rendered from the stored breakdown)
```

Implementation rule: display match_score from the API and render breakdown.components\[\].points; the sum of points must equal match_score within ±1 after rounding.

## 19.10 Skill Gap

_Wireframe — Skill gap_

```
┌──────────────────────────────────────────────┐
│ Your top skill gaps (from top 15 matches)    │
├──────────────────────────────────────────────┤
│ 1 React      [HIGH]  ###########...  9/15    │
│   Avg +11% match if learned        [ v ]     │
│ 2 REST API   [HIGH]  ########......  7/15    │
│ 3 Git        [MED]   #####.........  5/15    │
│ 4 TypeScript [LOW]   ##............  2/15    │
│                                              │
│ [ See your roadmap → ]                       │
└──────────────────────────────────────────────┘
```

## 19.11 Roadmap

_Wireframe — Roadmap_

```
┌──────────────────────────────────────────────┐
│ Frontend Developer roadmap · ~6 weeks  25%   │
│ #####..............                          │
├──────────────────────────────────────────────┤
│ *  [LEARN] React fundamentals · ~20 h   [x]  │
│ │  Why: in 9 of 15 top matches               │
│ │  Search: "react tutorial for beginners"    │
│ *  [BUILD] Portfolio app with public API [ ] │
│ │  ~12 h · uses React + REST API             │
│ *  [LEARN] REST API basics · ~8 h        [ ] │
│ *  [APPLY] Apply to 3 saved internships  [ ] │
│    → Frontend Intern (87%) · React Intern…   │
└──────────────────────────────────────────────┘
```

## 19.12 Saved Opportunities

_Wireframe — Saved_

```
┌────────────────────────────────────────────────────────────────┐
│ Saved (3)                                  Filter: [All v]     │
├────────────────────────────────────────────────────────────────┤
│ Frontend Intern · 87% · saved 2d  [Tracked: Applied]  [unsave] │
│ React Intern    · 81% · saved 2d  [ Track ]           [unsave] │
│ UI Dev Trainee  · 64% · saved 1d  [ Track ]           [unsave] │
└────────────────────────────────────────────────────────────────┘
```

## 19.13 Application Tracker

_Wireframe — Tracker (desktop board)_

```
┌──────────┬──────────┬────────────┬────────┬──────────┬──────────┐
│ Planned  │ Applied  │Interviewing│ Offer  │ Rejected │ Withdrawn│
├──────────┼──────────┼────────────┼────────┼──────────┼──────────┤
│┌────────┐│┌────────┐│            │        │          │          │
││React   │││Frontend││            │        │          │          │
││Intern  │││Intern  ││            │        │          │          │
││[stat v]│││Applied ││            │        │          │          │
│└────────┘││12 Sep  ││            │        │          │          │
│          │└────────┘│            │        │          │          │
└──────────┴──────────┴────────────┴────────┴──────────┴──────────┘
```

| **Element**     | **Specification**                                   |
| --------------- | --------------------------------------------------- |
| MVP interaction | Status dropdown per card (drag-and-drop is Phase 2) |

## 19.14 Settings

_Wireframe — Settings_

```
┌──────────────────────────────────────────────┐
│ Settings                                     │
│ Account        riya@example.com              │
│ Theme          ( ) Light (-) System ( ) Dark │
│ Search history [ View history → ]            │
│ Privacy        What we share and with whom → │
│ [ Log out ]                                  │
│ Delete account — contact team (Phase 2)      │
└──────────────────────────────────────────────┘
```

# 20\. Design Handoff Checklist

- Tailwind config with colour tokens and Inter font committed on Day 3.
- Component library (Button, Card, Badge, Chip, MatchRing, GapBar, Stepper, Toast, Modal, Skeleton) built before pages.
- All screens tested at 360, 768, 1280 px.
- Dark mode optional — ship only if Day 9 has slack.
- Screenshot every screen for the submission deck.