# Frontend Documentation — Engineering Governance Dashboard

> Complete reference for moving this frontend to another project. Covers tech stack, architecture, every component, every API endpoint consumed, every data shape, and every UI section.

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Project Structure](#project-structure)
3. [Running the App](#running-the-app)
4. [Backend API Dependency](#backend-api-dependency)
5. [Page Architecture](#page-architecture)
6. [Data Fetching & Refresh Strategy](#data-fetching--refresh-strategy)
7. [All API Endpoints Consumed](#all-api-endpoints-consumed)
8. [Complete Data Shapes (TypeScript Interfaces)](#complete-data-shapes-typescript-interfaces)
9. [Component Reference](#component-reference)
   - [MetricCard](#metriccard)
   - [HealthScoreCard](#healthscorecard)
   - [RiskCard](#riskcard)
   - [FindingsSummary](#findingssummary)
   - [HotspotTable](#hotspottable)
   - [TimelineFeed](#timelinefeed)
   - [DeveloperTable](#developertable)
   - [ContextStatusCard](#contextstatuscard)
   - [ReviewFeed & ReviewCard](#reviewfeed--reviewcard)
   - [AIReviewSection](#aireviewsection)
   - [RiskBadge](#riskbadge)
   - [DecisionBadge](#decisionbadge)
10. [UI Sections on the Page (Top to Bottom)](#ui-sections-on-the-page-top-to-bottom)
11. [Styling & Theming](#styling--theming)
12. [State Management](#state-management)
13. [Error Handling](#error-handling)

---

## Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Next.js | 16.2.4 | React framework (App Router) |
| React | 19.2.4 | UI library |
| TypeScript | ^5 | Type safety |
| Tailwind CSS | ^4 | Utility-first styling |
| lucide-react | ^1.14.0 | Icon library |
| Geist Sans / Geist Mono | via `next/font/google` | Typography |

No state management library (Redux, Zustand, etc.) is used. Everything is React `useState` + `useCallback` + `useEffect`.

---

## Project Structure

```
frontend/
├── app/
│   ├── globals.css          # Tailwind import + CSS variables
│   ├── layout.tsx           # Root layout — sets fonts, metadata, body wrapper
│   └── page.tsx             # Single page — the entire dashboard (GovernanceDashboard)
├── components/
│   ├── AIReviewSection.tsx  # AI governance review panel inside ReviewCard
│   ├── ContextStatusCard.tsx# Repository context coverage card
│   ├── DecisionBadge.tsx    # APPROVED / NEEDS_REVIEW / BLOCKED pill badge
│   ├── DeveloperTable.tsx   # Per-developer analytics table
│   ├── FindingsSummary.tsx  # Findings count by category (grid of colored cards)
│   ├── HealthScoreCard.tsx  # SVG ring gauge for Engineering Health Score
│   ├── HotspotTable.tsx     # Top 10 most-modified files with mini bar charts
│   ├── MetricCard.tsx       # Generic metric tile (icon + big number + label)
│   ├── ReviewCard.tsx       # Collapsible card for a single review (findings, diff, AI, context)
│   ├── ReviewFeed.tsx       # List of ReviewCard components
│   ├── RiskBadge.tsx        # LOW / MEDIUM / HIGH colored pill badge
│   ├── RiskCard.tsx         # Full risk level card with count, %, progress bar
│   └── TimelineFeed.tsx     # Chronological activity event list
├── public/                  # Static assets (empty by default)
├── eslint.config.mjs
├── next.config.ts           # Minimal Next.js config (no overrides)
├── next-env.d.ts
├── package.json
├── postcss.config.mjs
└── tsconfig.json
```

---

## Running the App

```bash
# Install dependencies
npm install

# Development server (port 3002)
npm run dev

# Production build
npm run build
npm run start        # also runs on port 3002
```

The dev and production servers both run on **port 3002** (not the default 3000).

---

## Backend API Dependency

The entire frontend is a read-only consumer of a REST backend. The base URL is hard-coded in `page.tsx`:

```ts
const BASE_URL = 'https://review-engine.onrender.com';
```

**To move to another project, change this constant** (or make it an environment variable like `process.env.NEXT_PUBLIC_API_URL`).

All requests are plain `fetch()` GET requests — no authentication headers, no cookies, no body. If the server returns a non-OK status, the frontend silently keeps the previous state.

---

## Data Fetching & Refresh Strategy

- All 10 endpoints are fetched **in parallel** using `Promise.all` inside a `fetchAll` callback.
- `fetchAll` runs **immediately on mount** and then **every 10 seconds** via `setInterval`.
- The **"Live"** indicator in the header reflects this auto-refresh.
- The last-updated timestamp shown in the header is set after every successful fetch cycle.
- Individual endpoint failures are swallowed (`safeFetch` returns `null` on error). The page only shows the error banner if **both** `/analytics/overview` AND `/analytics/risks` fail simultaneously.

```ts
const REFRESH_INTERVAL_MS = 10_000; // 10 seconds
```

---

## All API Endpoints Consumed

| Endpoint | Method | Used for |
|---|---|---|
| `GET /analytics/overview` | GET | 6 summary metric cards |
| `GET /analytics/risks` | GET | Risk distribution (LOW / MEDIUM / HIGH counts) |
| `GET /analytics/health` | GET | Engineering Health Score ring gauge |
| `GET /analytics/developers` | GET | Developer analytics table |
| `GET /reviews` | GET | Full review history feed |
| `GET /analytics/hotspots` | GET | File hotspot table |
| `GET /analytics/timeline` | GET | Activity timeline feed |
| `GET /analytics/findings-summary` | GET | Findings by category (SECURITY, GOVERNANCE, etc.) |
| `GET /analytics/summary` | GET | AI-generated governance prose summary banner |
| `GET /analytics/context-status` | GET | Repository context coverage card |

---

## Complete Data Shapes (TypeScript Interfaces)

### `OverviewData` — from `/analytics/overview`
```ts
interface OverviewData {
  total_reviews: number;
  total_repositories: number;
  total_developers: number;
  total_findings: number;
  high_risk_reviews: number;
  blocked_reviews: number;
}
```

### `RiskData` — from `/analytics/risks`
```ts
interface RiskData {
  LOW: number;
  MEDIUM: number;
  HIGH: number;
}
```

### `HealthData` — from `/analytics/health`
```ts
interface HealthData {
  engineering_health_score: number;  // 0–100
  health_label: string;              // "EXCELLENT" | "GOOD" | "WARNING" | "CRITICAL"
}
```

### `Developer` — from `/analytics/developers` (array)
```ts
interface Developer {
  author: string;
  total_pushes: number;
  avg_files_changed: number;
  avg_risk_score: number;  // numeric; ≥6 → HIGH, ≥3 → MEDIUM, <3 → LOW
}
```

### `HotspotEntry` — from `/analytics/hotspots` (array)
```ts
interface HotspotEntry {
  filename: string;
  modifications: number;
  risk_score: number;  // cumulative risk score across all touches
}
```

### `TimelineEvent` — from `/analytics/timeline` (array)
```ts
interface TimelineEvent {
  timestamp: string;   // ISO 8601 date string
  author: string;
  repository: string;
  event: string;       // human-readable event description
  type: string;        // "HIGH_RISK" | "SENSITIVE" | "REVIEW"
}
```

### Findings summary — from `/analytics/findings-summary`
```ts
// Plain object: category name → count
Record<string, number>
// Known keys: "SECURITY", "SENSITIVE_MODULE", "GOVERNANCE", "CODE_QUALITY", "ARCHITECTURE"
// Example: { "SECURITY": 4, "CODE_QUALITY": 12, "GOVERNANCE": 3 }
```

### Summary banner — from `/analytics/summary`
```ts
{ summary: string }  // A prose paragraph generated by the AI governance engine
```

### `ContextStatus` — from `/analytics/context-status`
```ts
interface ContextStatus {
  repositories_with_context: number;
  repositories_missing_context: number;
  loaded_user_stories: number;
  latest_detected_story: string | null;    // e.g. "US-101"
  repos_with_context: string[];            // list of repo names
  repos_missing_context: string[];         // list of repo names
}
```

### `Review` — from `/reviews` (array)
```ts
interface Review {
  status: string;
  repository: string;
  branch: string;
  commit_sha: string;
  author: string;
  timestamp: string;             // ISO 8601
  risk_score: string;            // "LOW" | "MEDIUM" | "HIGH"
  risk_score_value: number;
  review_decision?: string;      // "APPROVED" | "NEEDS_REVIEW" | "BLOCKED"
  total_files_changed: number;
  findings: Finding[];
  files_changed: FileChanged[];
  // Context metadata
  repository_context_loaded?: boolean;
  loaded_context_files?: string[];
  detected_user_story?: string | null;
  available_user_stories?: string[];
  commit_message?: string;
  // AI governance review
  ai_review?: AIReviewResult;
  // Balanced decision engine outputs
  decision_reason?: string[];
  governance_confidence?: number;   // 0–100
}

interface Finding {
  category: string;   // "SECURITY" | "GOVERNANCE" | "CODE_QUALITY" | etc.
  severity: string;   // "LOW" | "MEDIUM" | "HIGH"
  message: string;
  file: string;       // filename where the finding was detected
}

interface FileChanged {
  filename: string;
  status: string;     // "added" | "modified" | "removed" etc.
  additions: number;
  deletions: number;
  changes: number;
  patch: string | null;  // raw unified diff string
}

interface AIReviewResult {
  // Success shape
  ai_summary?: string;
  coverage_percentage?: number;        // 0–100; user story requirement coverage
  missing_requirements?: string[];
  security_review?: string[];          // list of security observations
  architecture_review?: string[];      // list of architecture observations
  recommendations?: string[];
  // Failure shape
  status?: string;   // "failed"
  message?: string;
}
```

---

## Component Reference

### MetricCard

**File:** `components/MetricCard.tsx`

A simple tile showing a single KPI.

| Prop | Type | Description |
|---|---|---|
| `title` | `string` | Small uppercase label |
| `value` | `number \| string` | Large number displayed prominently |
| `description` | `string` | Small subtitle text |
| `icon` | `React.ReactNode` | lucide-react icon element |
| `iconBg` | `string` | Tailwind bg class for icon container |
| `iconColor` | `string` | Tailwind text class for icon |

**Displays:** icon on the left, title + large value + description on the right.

---

### HealthScoreCard

**File:** `components/HealthScoreCard.tsx`

An SVG ring gauge showing the engineering health score.

| Prop | Type | Description |
|---|---|---|
| `score` | `number` | 0–100 numeric health score |
| `label` | `string` | `"EXCELLENT"` \| `"GOOD"` \| `"WARNING"` \| `"CRITICAL"` |

**Displays:** Animated ring gauge (score fills the ring as a percentage), label, description of the health state.

**Color mapping:**
- `EXCELLENT` → emerald (green)
- `GOOD` → indigo (blue)
- `WARNING` → amber (yellow)
- `CRITICAL` → red

---

### RiskCard

**File:** `components/RiskCard.tsx`

A colored card for one risk tier.

| Prop | Type | Description |
|---|---|---|
| `level` | `"LOW" \| "MEDIUM" \| "HIGH"` | Risk tier |
| `count` | `number` | Reviews at this risk level |
| `total` | `number` | Total reviews (used to compute percentage) |

**Displays:** Badge label, percentage of total, large count number, description ("Safe to merge", "Review recommended", "Immediate review required"), mini progress bar.

---

### FindingsSummary

**File:** `components/FindingsSummary.tsx`

A grid of colored count cards, one per finding category.

| Prop | Type | Description |
|---|---|---|
| `summary` | `Record<string, number>` | Category → count map |

**Known categories and colors:**
| Category key | Display label | Color |
|---|---|---|
| `SECURITY` | Security | Red |
| `SENSITIVE_MODULE` | Sensitive Module | Orange |
| `GOVERNANCE` | Governance | Amber |
| `CODE_QUALITY` | Code Quality | Blue |
| `ARCHITECTURE` | Architecture | Violet |
| *(any other)* | Other | Slate/grey |

Sorted descending by count. Renders as a responsive grid (2 → 3 → 5 columns).

---

### HotspotTable

**File:** `components/HotspotTable.tsx`

A ranked list of the top 10 most-modified files.

| Prop | Type | Description |
|---|---|---|
| `hotspots` | `HotspotEntry[]` | Array from `/analytics/hotspots` |

**Displays:** Rank number (top 3 highlighted red), filename, modification count, cumulative risk score, horizontal progress bar (relative to the most-modified file).

---

### TimelineFeed

**File:** `components/TimelineFeed.tsx`

A vertical chronological event list (up to 20 events shown).

| Prop | Type | Description |
|---|---|---|
| `events` | `TimelineEvent[]` | Array from `/analytics/timeline` (`.slice(0, 20)`) |

**Event types and icons/colors:**
| `type` value | Icon | Dot color |
|---|---|---|
| `HIGH_RISK` | ShieldAlert | Red |
| `SENSITIVE` | AlertTriangle | Amber |
| `REVIEW` | GitCommit | Indigo |
| *(fallback)* | GitCommit | Indigo |

**Displays:** Vertical line connector, colored dot + icon, event description, author, repository name, formatted timestamp.

---

### DeveloperTable

**File:** `components/DeveloperTable.tsx`

A table of all developers with activity and risk metrics.

| Prop | Type | Description |
|---|---|---|
| `developers` | `Developer[]` | Array from `/analytics/developers` |

**Columns:** Developer (avatar initial + name), Total Pushes, Avg Files Changed, Avg Risk Score (number + `RiskBadge`).

**Risk label logic:** `avg_risk_score >= 6` → HIGH, `>= 3` → MEDIUM, `< 3` → LOW.

---

### ContextStatusCard

**File:** `components/ContextStatusCard.tsx`

Shows governance context coverage across all connected repositories.

| Prop | Type | Description |
|---|---|---|
| `status` | `ContextStatus` | Object from `/analytics/context-status` |

**Displays:**
- 4 stat tiles: Repos with context, Repos missing context, Number of loaded user stories, Last detected user story ID
- List of repos that **have** context (green pills with ✓)
- List of repos **missing** context (amber pills with ✕)

---

### ReviewFeed & ReviewCard

**Files:** `components/ReviewFeed.tsx`, `components/ReviewCard.tsx`

`ReviewFeed` is a simple wrapper that renders a `ReviewCard` for each item in the reviews array.

| Prop | Type | Description |
|---|---|---|
| `reviews` | `Review[]` | Array from `GET /reviews` |

**ReviewCard — Collapsed state shows:**
- Repository name
- `RiskBadge` (LOW / MEDIUM / HIGH)
- `DecisionBadge` (APPROVED / NEEDS_REVIEW / BLOCKED) if present
- Governance confidence % badge (green/amber/red based on value)
- Commit SHA (first 8 chars), branch, author, timestamp, files changed count
- First 3 finding messages as chips, "+N more" if there are more

**ReviewCard — Expanded state shows (5 sections):**

1. **Governance Decision** — confidence bar (0–100%) + list of decision reasoning strings
2. **Repository Context** — whether context was loaded, how many user stories are available, detected user story ID, list of loaded context file names
3. **AI Governance Review** — full `AIReviewSection` (see below)
4. **Findings** — all findings, each showing severity badge, message, filename, category tag
5. **Changed Files** — each file shows filename, status, +additions / −deletions, and the raw unified diff rendered in a dark `<pre>` block (dark background `#0d1117`, emerald text)

Cards are only clickable/expandable if they have at least one finding or changed file.

---

### AIReviewSection

**File:** `components/AIReviewSection.tsx`

Rendered inside an expanded `ReviewCard` when `ai_review` is present.

| Prop | Type | Description |
|---|---|---|
| `aiReview` | `AIReviewResult` | The `ai_review` field from a `Review` object |

**Displays (success state):**
- AI Summary prose paragraph
- User Story Coverage bar (0–100% with color: green ≥80%, amber ≥50%, red <50%)
- Missing Requirements bullet list
- Security Observations bullet list
- Architecture Review bullet list
- Recommendations list (styled as arrow-prefixed cards)

**Displays (failure state):** A single grey italic line: "AI Governance Review unavailable" (or the error message from `aiReview.message`).

---

### RiskBadge

**File:** `components/RiskBadge.tsx`

A small colored pill badge.

| Prop | Type | Description |
|---|---|---|
| `level` | `string` | `"LOW"` \| `"MEDIUM"` \| `"HIGH"` |
| `size` | `"sm" \| "md"` | Controls padding/font size (default `"sm"`) |

**Colors:** LOW → emerald, MEDIUM → amber, HIGH → red.

---

### DecisionBadge

**File:** `components/DecisionBadge.tsx`

A pill badge for the review decision.

| Prop | Type | Description |
|---|---|---|
| `decision` | `string` | `"APPROVED"` \| `"NEEDS_REVIEW"` \| `"BLOCKED"` |
| `size` | `"sm" \| "md"` | Controls padding/font size (default `"sm"`) |

**Colors:** APPROVED → emerald, NEEDS_REVIEW → amber, BLOCKED → red.
**Icons:** APPROVED → ✓, NEEDS_REVIEW → ◎, BLOCKED → ✕.

---

## UI Sections on the Page (Top to Bottom)

```
┌─────────────────────────────────────────────────────────────┐
│ HEADER (sticky)                                             │
│  [Activity icon] Engineering Governance Dashboard           │
│                             [Last updated time] [● Live]   │
├─────────────────────────────────────────────────────────────┤
│ ERROR BANNER (only if both overview + risks fail)           │
├─────────────────────────────────────────────────────────────┤
│ GOVERNANCE SUMMARY BANNER                                   │
│  Indigo box with prose summary from /analytics/summary      │
├─────────────────────────────────────────────────────────────┤
│ OVERVIEW SECTION                                            │
│  HealthScoreCard (ring gauge, score 0–100, label)           │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┐              │
│  │Total │Devs  │Find- │High  │Block-│Repos │              │
│  │Review│      │ings  │Risk  │ed    │      │              │
│  └──────┴──────┴──────┴──────┴──────┴──────┘              │
├─────────────────────────────────────────────────────────────┤
│ RISK DISTRIBUTION                                           │
│  ┌────────────┬────────────┬────────────┐                  │
│  │  LOW RISK  │ MEDIUM RISK│  HIGH RISK │                  │
│  │ count, %, bar           │            │                  │
│  └────────────┴────────────┴────────────┘                  │
├─────────────────────────────────────────────────────────────┤
│ FINDINGS DISTRIBUTION                                       │
│  Grid of category cards: Security | Governance | Quality.. │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────┬────────────────────────┐           │
│ │ FILE HOTSPOTS       │ ACTIVITY TIMELINE       │           │
│ │ Top 10 files with   │ Last 20 events          │           │
│ │ bar chart           │ (scrollable, 480px max) │           │
│ └─────────────────────┴────────────────────────┘           │
├─────────────────────────────────────────────────────────────┤
│ DEVELOPER ANALYTICS                                         │
│  Table: Developer | Total Pushes | Avg Files | Avg Risk     │
├─────────────────────────────────────────────────────────────┤
│ REPOSITORY CONTEXT STATUS                                   │
│  4 stat tiles + repo lists with ✓/✕ pills                  │
├─────────────────────────────────────────────────────────────┤
│ REVIEW HISTORY                                              │
│  List of collapsible ReviewCards (newest first from API)    │
│  Each card expands to show:                                 │
│    - Governance Decision + confidence bar                   │
│    - Repository Context (loaded files, user story)          │
│    - AI Governance Review (summary, coverage, findings)     │
│    - Rule-based Findings list                               │
│    - Changed Files with inline diff                         │
├─────────────────────────────────────────────────────────────┤
│ FOOTER (empty, just a border)                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Styling & Theming

- **CSS framework:** Tailwind CSS v4 (via `@import "tailwindcss"` in `globals.css`)
- **Color palette:** Uses Tailwind's default slate, indigo, violet, emerald, amber, red, rose, teal, orange, blue color scales.
- **Typography:** Geist Sans (sans-serif) + Geist Mono (monospace) from Google Fonts, applied via CSS variables `--font-geist-sans` / `--font-geist-mono`.
- **Dark mode:** `globals.css` has `prefers-color-scheme: dark` CSS variables defined (`--background: #0a0a0a`, `--foreground: #ededed`) but **none of the components use `dark:` Tailwind classes** — the dashboard is effectively light-mode only in practice.
- **Background:** `bg-slate-50` on the main container.
- **Cards:** White (`bg-white`) with `rounded-2xl`, `border border-slate-100`, `shadow-sm`.
- **Diff view:** Hard-coded dark background `bg-[#0d1117]` with `text-emerald-400`.
- **Icons:** All from `lucide-react`.

---

## State Management

All state lives in a single `useState` in the `GovernanceDashboard` component in `page.tsx`. There is no context, no global store.

| State variable | Type | Source |
|---|---|---|
| `overview` | `OverviewData \| null` | `/analytics/overview` |
| `risks` | `RiskData \| null` | `/analytics/risks` |
| `health` | `HealthData \| null` | `/analytics/health` |
| `developers` | `Developer[]` | `/analytics/developers` |
| `reviews` | `Review[]` | `/reviews` |
| `hotspots` | `HotspotEntry[]` | `/analytics/hotspots` |
| `timeline` | `TimelineEvent[]` | `/analytics/timeline` |
| `findingsSummary` | `Record<string, number>` | `/analytics/findings-summary` |
| `summaryText` | `string` | `/analytics/summary` |
| `contextStatus` | `ContextStatus \| null` | `/analytics/context-status` |
| `lastUpdated` | `Date \| null` | Set locally after each fetch cycle |
| `loading` | `boolean` | `true` until first fetch completes |
| `error` | `string \| null` | Set if overview + risks both fail |

---

## Error Handling

- **Network errors / non-OK responses:** `safeFetch` catches all exceptions and returns `null`. Stale data stays on screen.
- **Error banner:** Shown in red at the top of main content only when `overview` AND `risks` both return null.
- **Empty states:** Every component has its own empty state UI (e.g., "No reviews yet", "No file hotspot data yet").
- **Loading state:** A `<Spinner />` (spinning `RefreshCw` icon + "Loading…") is shown in place of each section while `loading === true`.
- **Partial failures:** If one endpoint fails but others succeed, the page still renders with whatever data was received. The failed section either retains its previous value or shows its empty state.
