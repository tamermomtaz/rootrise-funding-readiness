# Platform DNA Report
# RootRise Funding Readiness Dashboard (FRD)
# Generated: 2026-03-09
# Extracted by: Claude Code from live codebase

---

## 1. IDENTITY

- **Platform Name:** RootRise Funding Readiness Dashboard (FRD)
- **One-Line Purpose:** A real-time tracking system for managing startup funding opportunities and investor-readiness preparation items for DEVONEERS/RootRise.
- **Target Users:** DEVONEERS founding team (Tee, Rouba) — internal operations tool for tracking accelerators, grants, VC funds, business development opportunities, and readiness milestones.
- **Domain:** Startup Funding & Investor Readiness Management (FinTech-adjacent / Startup Operations)
- **Build Period:** January 23, 2026 — February 13, 2026 (~3 weeks, 31 commits)
- **Current Status:** Live / In-dev — deployed on Railway (start.sh present, deployment configs iterated through Dockerfile → nixpacks → start.sh), actively maintained with v1.1 feature additions.
- **Repo Structure:** Single app — monorepo with `backend/` (FastAPI single file) and `frontend/` (single-page HTML application), served together by the backend.

## 2. TECH STACK (exact versions from package.json / requirements.txt)

### Frontend
- **Framework:** Vanilla JavaScript (no framework — single HTML file SPA)
- **UI Library:** None — custom CSS with hand-built component system
- **State Management:** Global JavaScript variables (`opportunities`, `readinessItems`, `dashboardStats`, `currentPipeline`, etc.)
- **Routing:** Hash-based section switching via `showSection()` function (no router library)
- **Build Tool:** None — no build step, raw HTML/CSS/JS served directly
- **CSS Approach:** Embedded `<style>` block with CSS custom properties (design tokens), responsive breakpoints at 1200px and 768px
- **Key Dependencies (with versions):**
  - Google Fonts (Cinzel, Raleway, JetBrains Mono) — loaded via CDN
  - No npm dependencies — zero-dependency frontend
- **Deployment Target:** Served as static file by FastAPI backend (same origin)

### Backend
- **Framework:** FastAPI 0.103.2
- **Language + Version:** Python 3.11.7
- **ORM / DB Client:** Raw `sqlite3` module (no ORM) with context manager pattern
- **Auth Approach:** API key via environment variable (`API_KEY`), but **NOT enforced** — no auth middleware is active. The API key is defined but never checked on any endpoint.
- **Key Dependencies (with versions):**
  - fastapi==0.103.2
  - uvicorn==0.23.2
  - pydantic==1.10.13
- **Deployment Target:** Railway (via `start.sh`: `uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}`)

### Database
- **Engine:** SQLite
- **Provider:** Local file (`funding_readiness.db`, path configurable via `DATABASE_PATH` env var)
- **Tables (list ALL table names):**
  1. `opportunities`
  2. `readiness_items`
  3. `activity_log`
- **Uses RLS:** No — SQLite does not support RLS. No row-level security of any kind.
- **Migration Approach:** Hybrid — initial schema via `CREATE TABLE IF NOT EXISTS` on startup, incremental column additions via `run_migrations()` which checks `PRAGMA table_info` before `ALTER TABLE`. Idempotent, runs every startup.

### AI Layer (if applicable)
- **Model(s) Used:** N/A — no AI integration in this platform
- **API Integration:** N/A
- **System Prompts:** N/A
- **JSON Parse Protection:** N/A
- **Failover:** N/A

### Infrastructure
- **CI/CD:** None — manual pushes to GitHub, Railway auto-deploys from main branch
- **Hosting Frontend:** Same server as backend (FastAPI serves `frontend/index.html` and `/static/` directory)
- **Hosting Backend:** Railway
- **Environment Variables (list ALL env var names, NOT values):**
  - `DATABASE_PATH` — SQLite file location
  - `API_KEY` — authentication key (defined but unused)
  - `PORT` — server port (Railway injects this)
  - `SLACK_WEBHOOK_URL` — Slack notifications (defined in env.example, not implemented)
  - `DISCORD_WEBHOOK_URL` — Discord notifications (defined in env.example, not implemented)
  - `SMTP_HOST` — Email config (defined in env.example, not implemented)
  - `SMTP_PORT` — Email config (defined in env.example, not implemented)
  - `SMTP_USER` — Email config (defined in env.example, not implemented)
  - `SMTP_PASSWORD` — Email config (defined in env.example, not implemented)
  - `EMAIL_FROM` — Email config (defined in env.example, not implemented)
  - `EMAIL_TO` — Email config (defined in env.example, not implemented)
  - `DEBUG` — mentioned in env.example comments, not read by code
  - `CORS_ORIGINS` — mentioned in env.example comments, not read by code
- **Domain/URLs (from config files):** None configured — uses relative paths (`/api`) and Railway's auto-generated domain

## 3. ARCHITECTURE PATTERNS

### Auth Pattern
- **How does auth work?** It doesn't. An `API_KEY` env var is defined (`backend/main.py:29`) with a default value of `rootrise-dev-key-2024`, but **no middleware or dependency checks it**. All endpoints are completely open. This is the most critical security gap.
- **Where is the auth middleware?** Does not exist. No `Depends()` for auth on any route.
- **Is there role-based access?** No. No user model, no roles, no permissions.
- **Is there a 401 interceptor on the frontend?** No. The `fetchAPI()` function (`frontend/index.html:511-517`) only throws on non-ok responses and shows a generic toast error. No specific 401 handling.
- **Is JWT auto-refresh implemented?** No — there is no JWT system at all.

### API Pattern
- **REST / GraphQL / RPC?** REST
- **How are routes organized?** By entity — opportunities (`/api/opportunities/*`), readiness items (`/api/readiness-items/*`), dashboard (`/api/dashboard-stats`), activity (`/api/activity-log`), health (`/api/health`). All in a single `main.py` file.
- **Is there a gateway/aggregator?** No. Single FastAPI application handles everything.
- **CORS configuration:** Wildcard — `allow_origins=["*"]`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]` (`backend/main.py:352-358`). This is a security concern, especially with `allow_credentials=True` combined with wildcard origins.
- **Error response format:** FastAPI default HTTPException format: `{"detail": "error message"}`. Used for 404s on missing entities.

### Data Flow Pattern
- **How does data flow from UI -> API -> DB -> back?**
  1. Frontend JS calls `fetchAPI()` which hits `/api/*` endpoints
  2. FastAPI endpoint opens SQLite connection via `db_session()` context manager
  3. Raw SQL query executes, results converted via `sqlite3.Row` then `clean_row()` dict cleanup
  4. JSON response returned, frontend updates global arrays and re-renders DOM
- **Are there intermediate services/layers?** No — direct endpoint-to-database with no service layer.
- **Is there an event system / message queue?** No. Activity logging is synchronous and inline (`log_activity()` called within the same transaction).

### State Management Pattern (Frontend)
- **How is state managed?** Global variables: `opportunities`, `readinessItems`, `dashboardStats`, `currentPipeline`, `currentTypeFilter`, `currentReadinessFilter`, `showingSavedOnly`, `typeCounts` (`frontend/index.html:492-495`).
- **Where is API data cached?** In those global arrays. No cache invalidation — data is fully replaced on each `refreshData()` call.
- **How are loading/error states handled?** Minimal — no loading spinners on initial load. The refresh button gets a spinning SVG animation during refresh (`frontend/index.html:863-864`). Errors show a toast notification. No skeleton screens or loading indicators on data load.

### File Organization Pattern
- **What's the directory tree?**
  ```
  .
  ├── .python-version
  ├── README.md
  ├── PLATFORM_DNA.md
  ├── backend/
  │   └── main.py                    (715 lines — entire backend)
  ├── env.example
  ├── frontend/
  │   ├── index.html                 (891 lines — entire frontend)
  │   └── static/
  │       ├── .gitkeep
  │       ├── favicon.ico
  │       ├── icon-152x152.png
  │       ├── icon-16x16.png
  │       ├── icon-180x180.png
  │       ├── icon-192x192.png
  │       ├── icon-32x32.png
  │       ├── icon-48x48.png
  │       ├── icon-512x512.png
  │       ├── icon-72x72.png
  │       ├── icon-96x96.png
  │       ├── logo-header.png
  │       └── manifest.json
  ├── gitignore
  ├── requirements.txt
  └── start.sh
  ```
- **How are things grouped?** By layer — `backend/` and `frontend/` directories. But each layer is a single file, so there's no further decomposition.
- **Is there a clear separation of concerns?** At the macro level (frontend/backend split), yes. At the micro level, no — `main.py` is a 715-line monolith containing models, database setup, migrations, seed data, and all endpoints. `index.html` is 891 lines combining HTML structure, all CSS, and all JavaScript.

## 4. DATABASE SCHEMA (complete)

### Table: opportunities
- **Purpose:** Track funding opportunities (accelerators, grants, VC funds, competitions, RFPs, tenders, etc.)
- **Columns:**
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | INTEGER | PRIMARY KEY AUTOINCREMENT |
  | name | TEXT | NOT NULL |
  | type | TEXT | NOT NULL |
  | deadline | TEXT | (ISO datetime string, nullable) |
  | status | TEXT | NOT NULL, DEFAULT 'researching' |
  | fit_score | INTEGER | DEFAULT 50 |
  | url | TEXT | (nullable) |
  | notes | TEXT | (nullable) |
  | funding_amount | TEXT | (nullable) |
  | requirements | TEXT | (nullable) |
  | contact_info | TEXT | (nullable) |
  | priority | INTEGER | DEFAULT 3 |
  | is_saved | BOOLEAN | DEFAULT 0 |
  | created_at | TEXT | NOT NULL |
  | updated_at | TEXT | NOT NULL |
- **Relationships:** None — no foreign keys
- **Indexes:** Only the implicit primary key index on `id`
- **RLS Policies:** N/A — SQLite
- **Created How:** `CREATE TABLE IF NOT EXISTS` on startup (`backend/main.py:220-237`), `is_saved` column added via idempotent migration (`backend/main.py:206-214`)

### Table: readiness_items
- **Purpose:** Track investor-readiness preparation items (legal docs, pitch deck, financial projections, team info, etc.)
- **Columns:**
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | INTEGER | PRIMARY KEY AUTOINCREMENT |
  | name | TEXT | NOT NULL |
  | category | TEXT | NOT NULL |
  | status | TEXT | NOT NULL, DEFAULT 'not_started' |
  | owner | TEXT | (nullable) |
  | due_date | TEXT | (ISO datetime string, nullable) |
  | description | TEXT | (nullable) |
  | priority | INTEGER | DEFAULT 3 |
  | dependencies | TEXT | (nullable, free text) |
  | completion_percentage | INTEGER | DEFAULT 0 |
  | created_at | TEXT | NOT NULL |
  | updated_at | TEXT | NOT NULL |
- **Relationships:** None — dependencies stored as free text, not FK references
- **Indexes:** Only the implicit primary key index on `id`
- **RLS Policies:** N/A
- **Created How:** `CREATE TABLE IF NOT EXISTS` on startup (`backend/main.py:239-252`)

### Table: activity_log
- **Purpose:** Audit trail of all CRUD operations on opportunities and readiness items
- **Columns:**
  | Column | Type | Constraints |
  |--------|------|-------------|
  | id | INTEGER | PRIMARY KEY AUTOINCREMENT |
  | action | TEXT | NOT NULL |
  | entity_type | TEXT | NOT NULL |
  | entity_id | INTEGER | NOT NULL |
  | details | TEXT | (nullable) |
  | timestamp | TEXT | NOT NULL |
- **Relationships:** Logical reference to opportunities/readiness_items via `entity_type` + `entity_id`, but no foreign key constraint
- **Indexes:** Only the implicit primary key index on `id`
- **RLS Policies:** N/A
- **Created How:** `CREATE TABLE IF NOT EXISTS` on startup (`backend/main.py:254-263`)

## 5. API ENDPOINTS (complete)

| Method | Path | Auth? | Purpose | Request Body | Response Shape |
|--------|------|-------|---------|-------------|----------------|
| GET | `/api/health` | No | Health check | - | `{status, version, timestamp}` |
| GET | `/api/opportunities` | No | List opportunities with filters | - (query params: status, type, min_fit_score, pipeline, is_saved, sort_by, sort_order) | `[{id, name, type, deadline, status, fit_score, url, notes, funding_amount, requirements, contact_info, priority, is_saved, created_at, updated_at}]` |
| GET | `/api/opportunities/counts-by-type` | No | Get opportunity counts grouped by type | - (query param: pipeline) | `{counts: {type: count}, total, saved_count, auth_count, pipeline}` |
| GET | `/api/opportunities/{opp_id}` | No | Get single opportunity | - | `{id, name, type, ...}` (same as list item) |
| POST | `/api/opportunities` | No | Create opportunity | `{name, type, deadline?, status?, fit_score?, url?, notes?, funding_amount?, requirements?, contact_info?, priority?}` | Created opportunity object |
| PUT | `/api/opportunities/{opp_id}` | No | Update opportunity | Partial `{name?, type?, deadline?, status?, ...}` | Updated opportunity object |
| PUT | `/api/opportunities/{opp_id}/toggle-save` | No | Toggle saved/starred status | - | `{id, is_saved, message}` |
| DELETE | `/api/opportunities/{opp_id}` | No | Delete opportunity | - | `{message, id}` |
| GET | `/api/readiness-items` | No | List readiness items with filters | - (query params: status, category, owner, sort_by, sort_order) | `[{id, name, category, status, owner, due_date, description, priority, dependencies, completion_percentage, created_at, updated_at}]` |
| GET | `/api/readiness-items/{item_id}` | No | Get single readiness item | - | Readiness item object |
| POST | `/api/readiness-items` | No | Create readiness item | `{name, category, status?, owner?, due_date?, description?, priority?, dependencies?, completion_percentage?}` | Created item object |
| PUT | `/api/readiness-items/{item_id}` | No | Update readiness item | Partial update fields | Updated item object |
| DELETE | `/api/readiness-items/{item_id}` | No | Delete readiness item | - | `{message, id}` |
| GET | `/api/dashboard-stats` | No | Computed dashboard metrics | - | `{total_opportunities, active_opportunities, upcoming_deadlines, total_readiness_items, completed_items, in_progress_items, overall_readiness_score, opportunities_by_status, opportunities_by_type, readiness_by_category, urgent_items, recent_activity}` |
| GET | `/api/activity-log` | No | Recent activity entries | - (query param: limit) | `[{id, action, entity_type, entity_id, details, timestamp}]` |
| POST | `/api/reset-database` | No | Wipe and reseed database | - | `{message}` |
| GET | `/` | No | Serve frontend HTML | - | HTML page |

**Total: 16 endpoints (15 API + 1 HTML)**

**Critical finding: `/api/reset-database` is exposed with NO authentication.** Anyone can wipe the production database.

## 6. BUGS ENCOUNTERED & FIXES

### Bug: CORS Wildcard with Credentials
- **Severity:** Warning
- **Category:** CORS
- **Evidence:** `backend/main.py:352-358` — `allow_origins=["*"]` combined with `allow_credentials=True`. Browsers will reject credentialed requests with wildcard origins per the CORS spec.
- **Root Cause:** Default permissive CORS config used during development and left in production.
- **Fix Applied:** None — still present.
- **Prevention Rule:** Always use explicit origin list from environment variable for production. Never combine `*` origins with credentials.
- **Codex Match:** Pattern #1 — CORS "No Access-Control-Allow-Origin"

### Bug: Unauthenticated Destructive Endpoint
- **Severity:** Critical
- **Category:** Auth
- **Evidence:** `backend/main.py:698-703` — `POST /api/reset-database` wipes the entire database with no auth check. `API_KEY` is defined at line 29 but never used in any endpoint.
- **Root Cause:** Auth was planned (env var exists, env.example documents it) but never implemented.
- **Fix Applied:** None — endpoint is still exposed.
- **Prevention Rule:** Always implement auth middleware before deploying any destructive endpoints. Use `Depends()` on all mutation endpoints at minimum.
- **Codex Match:** Related to Pattern #4 (JWT token expiry) — but this is worse: there's no auth at all.

### Bug: Empty String vs NULL Confusion in SQLite
- **Severity:** Warning
- **Category:** Database
- **Evidence:** `backend/main.py:192-204` — `clean_row()` function that converts empty strings to `None` for datetime and nullable fields. This wouldn't be necessary if the schema used proper NULL handling.
- **Root Cause:** SQLite stores empty strings and NULLs differently. Some code paths insert `''` instead of `NULL`, requiring post-query cleanup.
- **Fix Applied:** `clean_row()` sanitization function applied to all query results.
- **Prevention Rule:** Always use `NULL` explicitly in SQL inserts. Validate at the Pydantic model level that optional fields are `None`, not empty strings.
- **Codex Match:** New pattern — "SQLite empty string vs NULL desync"

### Bug: Deployment Configuration Churn
- **Severity:** Info
- **Category:** Deployment
- **Evidence:** Git history shows rapid iteration through deployment configs:
  - Created `railway.json` → Updated → Deleted
  - Created `Dockerfile` → Updated → Deleted
  - Created `nixpacks.toml` → Deleted
  - Finally settled on `start.sh` with pip install + uvicorn
- **Root Cause:** Trial-and-error deployment to Railway without understanding which config format Railway expects.
- **Fix Applied:** Settled on `start.sh` approach (build + run in one script).
- **Prevention Rule:** Standardize on one deployment method. Document Railway's expected configuration format. Use `start.sh` pattern as the default for Python/FastAPI apps.
- **Codex Match:** Pattern #9 — Railway $PORT not expanding (the `${PORT:-8000}` syntax in `start.sh` is the fix)

### Bug: Pydantic v1 Usage (Technical Debt)
- **Severity:** Warning
- **Category:** Schema
- **Evidence:** `requirements.txt:3` — `pydantic==1.10.13`. Using `.dict(exclude_unset=True)` at `backend/main.py:502` and `backend/main.py:601` (Pydantic v1 API). FastAPI 0.103.2 supports both v1 and v2, but this pins to v1.
- **Root Cause:** Likely started with Pydantic v1, pinned to avoid breaking changes.
- **Fix Applied:** Explicit version pin prevents accidental v2 upgrade.
- **Prevention Rule:** If using Pydantic v1, pin explicitly (done). Plan migration path to v2. Use `model_dump()` instead of `.dict()` when upgrading.
- **Codex Match:** Pattern #7 — Pydantic v1/v2 incompatibility (proactively pinned)

### Bug: `is_saved` Column Migration Without Default for Existing Rows
- **Severity:** Info
- **Category:** Database / Schema
- **Evidence:** `backend/main.py:212` — `ALTER TABLE opportunities ADD COLUMN is_saved BOOLEAN DEFAULT 0`. This is correct, but the migration check (`backend/main.py:209-211`) only checks column existence, not data integrity.
- **Root Cause:** Feature added post-initial-release (v1.1). Migration is idempotent and correctly defaults to 0.
- **Fix Applied:** The migration itself is well-implemented — idempotent check + sensible default.
- **Prevention Rule:** Always run migrations idempotently on startup for SQLite-based apps. This pattern is actually a good example.
- **Codex Match:** Pattern #3 — Missing database tables (preventive migration pattern)

### Bug: Auto-Status Update Logic May Conflict
- **Severity:** Info
- **Category:** Schema
- **Evidence:** `backend/main.py:610-617` — When `completion_percentage` is updated to 100, status is auto-set to "complete". When set to 1-99 and current status is "not_started", auto-set to "in_progress". But if a user explicitly sets both `completion_percentage` and `status` in the same request, the auto-logic may override their explicit `status`.
- **Root Cause:** Auto-status update runs after explicit field updates are queued but before they're committed, and the explicit status check (`"status" not in update_data`) doesn't account for ordering.
- **Fix Applied:** Partial — checks if `status` was explicitly provided before auto-updating.
- **Prevention Rule:** Auto-derived fields should be clearly documented and should never override explicit user input. Apply auto-logic only when the controlling field is the sole change.
- **Codex Match:** New pattern — "Auto-derived field conflict"

### Bug: No Input Sanitization on Delete Confirmation
- **Severity:** Warning
- **Category:** UI
- **Evidence:** `frontend/index.html:740` — `deleteOpportunity(${opp.id}, '${escapeHtml(opp.name).replace(/'/g, "\\'")}')`  — the name is escaped for HTML but then embedded in an `onclick` handler as a JS string literal. While `escapeHtml` + quote escaping helps, this is a fragile XSS prevention pattern.
- **Root Cause:** Inline onclick handlers with dynamic data are inherently risky.
- **Fix Applied:** `escapeHtml()` + single-quote escaping applied.
- **Prevention Rule:** Use event delegation with data attributes instead of inline onclick with dynamic strings. Or use a framework with built-in XSS protection.
- **Codex Match:** New pattern — "Inline onclick with dynamic data injection"

### Bug: Frontend API Base Detection
- **Severity:** Info
- **Category:** Deployment
- **Evidence:** `frontend/index.html:491` — `const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000/api' : '/api';`
- **Root Cause:** Needed to distinguish local dev (separate servers) from production (same origin). Since backend serves frontend, this works, but hardcoding `localhost:8000` is fragile.
- **Fix Applied:** Conditional based on hostname.
- **Prevention Rule:** Use environment-injected config or always use relative paths. Since the frontend is served by the backend, `/api` always works — the localhost branch is unnecessary dead code for this deployment model.
- **Codex Match:** N/A — minor issue

## 7. AI PROMPTS (if applicable)

N/A — This platform has no AI integration. No system prompts, no model calls, no LLM features.

## 8. DEPLOYMENT CONFIGURATION

### Backend Deployment
- **Provider:** Railway
- **Start Command:** `pip install -r requirements.txt && exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}` (from `start.sh`)
- **Build Command:** `pip install -r requirements.txt` (embedded in start.sh)
- **Root Directory:** Repository root
- **Dockerfile:** No — was created and deleted during development. Using start.sh approach instead.
- **Health Check:** Yes — `GET /api/health` returns `{status: "healthy", version: "1.1.0", timestamp: "..."}` (`backend/main.py:694-696`)

### Frontend Deployment
- **Provider:** Same as backend — FastAPI serves the frontend HTML and static files
- **Build Command:** None — no build step
- **Output Directory:** `frontend/` directory served directly
- **SPA Rewrites:** Not needed — single HTML file served at `/` by FastAPI catch-all route
- **Environment Variables:** None — frontend uses no VITE_* or build-time env vars. API base is detected at runtime.

### Database Deployment
- **Provider:** Local SQLite file on Railway's ephemeral filesystem
- **Migration Method:** Auto-create on startup via `init_db()` + `run_migrations()`. Schema is recreated fresh if file doesn't exist.
- **Backup Strategy:** None. **Critical risk**: Railway's filesystem is ephemeral — database is lost on redeploy. Seed data re-populates, but user-created data is lost.

## 9. WHAT WORKED (positive patterns to replicate)

### 1. Single-File Simplicity
- **What:** Entire backend in one `main.py`, entire frontend in one `index.html`
- **Where:** `backend/main.py`, `frontend/index.html`
- **Why it works:** For a small internal tool, this eliminates import complexity, build tooling, and mental overhead. Fast to develop, easy to understand at a glance. Zero build steps means zero build failures.

### 2. Idempotent Migration Pattern
- **What:** `run_migrations()` checks column existence before ALTER TABLE, runs on every startup
- **Where:** `backend/main.py:206-214`
- **Why it works:** Safe to run repeatedly, handles both fresh and existing databases. No migration files to track. Perfect for SQLite-based single-instance apps.

### 3. Context Manager for DB Sessions
- **What:** `db_session()` context manager with auto-commit/rollback/close
- **Where:** `backend/main.py:180-190`
- **Why it works:** Prevents connection leaks, ensures transactions are properly committed or rolled back. Clean pattern that eliminates try/finally boilerplate in every endpoint.

### 4. Seed Data with Real Content
- **What:** `seed_initial_data()` populates the database with actual RootRise opportunities and readiness items
- **Where:** `backend/main.py:272-334`
- **Why it works:** The app is immediately useful after first deploy — not an empty shell. Users see real data and understand the system's purpose. Also serves as documentation of the data model.

### 5. PWA Configuration
- **What:** Complete Progressive Web App setup with manifest, icons at multiple sizes, theme colors
- **Where:** `frontend/static/manifest.json`, `frontend/index.html:8-24`
- **Why it works:** Installable on mobile devices, looks native. Good for an internal tool that team members access frequently.

### 6. Pipeline Segmentation Pattern
- **What:** Dual pipeline concept — Startup (accelerators/grants/VC) vs BD (RFPs/tenders/consulting)
- **Where:** Backend: `STARTUP_TYPES`/`BD_TYPES` constants (`main.py:76-78`), Frontend: pipeline toggle UI
- **Why it works:** Clean categorization that maps to real organizational workflows. Filter logic is consistent between frontend and backend.

### 7. Activity Logging as Audit Trail
- **What:** Every CRUD operation logs to `activity_log` table within the same transaction
- **Where:** `backend/main.py:336-340`, called in every create/update/delete endpoint
- **Why it works:** Provides accountability and timeline. Transactional consistency (log fails = operation fails). Simple pattern that's easy to extend.

### 8. Weighted Readiness Score
- **What:** Overall readiness calculated as priority-weighted average: `SUM(completion * (6 - priority)) / SUM(6 - priority)`
- **Where:** `backend/main.py:664-666`
- **Why it works:** Higher-priority items count more toward the overall score. A clever single-query calculation that provides meaningful insight.

### 9. Clean Row Sanitization
- **What:** `clean_row()` function normalizes SQLite results (empty strings → None, is_saved → bool)
- **Where:** `backend/main.py:192-204`
- **Why it works:** Centralizes data cleanup in one place. Every query result passes through it. Prevents inconsistent null/empty handling downstream.

### 10. Responsive Design System
- **What:** Full design system with CSS custom properties, three breakpoints, consistent spacing
- **Where:** `frontend/index.html:28-291` (style block)
- **Why it works:** Bronze/teal/navy color scheme is distinctive and branded. Custom properties make theme changes trivial. Mobile-friendly layout with sidebar collapse.

## 10. WHAT BROKE OR WAS PAINFUL (anti-patterns to prevent)

### 1. No Authentication Whatsoever
- **What:** API_KEY defined but never enforced. All endpoints including `reset-database` are public.
- **Where:** `backend/main.py:29` (defined), nowhere (used)
- **Why it's a problem:** Anyone who discovers the URL can read, modify, or wipe all data. The reset endpoint is a one-click data destruction vector.
- **What to do instead:** At minimum, add a `Depends()` that checks `X-API-Key` header. For multi-user, implement JWT with Supabase Auth or equivalent.

### 2. Ephemeral SQLite on Railway
- **What:** SQLite database stored on Railway's filesystem, which is wiped on every redeploy.
- **Where:** `backend/main.py:28` — `DATABASE_PATH` defaults to local file
- **Why it's a problem:** All user-created data is lost on every deploy. Only seed data survives.
- **What to do instead:** Use a persistent database — Supabase PostgreSQL, Railway Postgres, or at minimum, a mounted volume. SQLite is fine for local dev but not for production on ephemeral PaaS.

### 3. 891-Line Single HTML File
- **What:** All CSS (~290 lines), HTML (~200 lines), and JavaScript (~400 lines) in one file.
- **Where:** `frontend/index.html`
- **Why it's a problem:** No code splitting, no component reuse, no minification. Hard to maintain as features grow. The v1.1 additions (save/star) added complexity to an already-dense file.
- **What to do instead:** At minimum, split into separate `.css` and `.js` files. For growth: use a lightweight framework (Alpine.js, Preact) with component structure.

### 4. Global Mutable State in Frontend
- **What:** All data stored in global `let` variables, mutated from anywhere.
- **Where:** `frontend/index.html:492-495`
- **Why it's a problem:** No encapsulation. Race conditions possible with concurrent API calls. Hard to debug state issues. `refreshData()` replaces entire arrays, but individual cards may have stale event handlers.
- **What to do instead:** Use a simple store pattern (even a plain object with getters/setters) or a reactive library.

### 5. SQL Injection Potential in ORDER BY
- **What:** `sort_by` and `sort_order` are inserted directly into SQL via f-string formatting.
- **Where:** `backend/main.py:408` — `query += f" ORDER BY {sort_by} {sort_order.upper()}"` (same pattern at line 557)
- **Why it's a problem:** Although the values are validated by FastAPI's `Query(regex=...)`, the SQL is constructed via string interpolation, not parameterized queries. If the regex validation were ever loosened or bypassed, this becomes SQL injection.
- **What to do instead:** Use a whitelist dict mapping valid field names to SQL expressions, or use an ORM.

### 6. No Tests
- **What:** Zero test files in the entire repository.
- **Where:** Everywhere (absence)
- **Why it's a problem:** No regression protection. No way to verify behavior after changes. No CI safety net.
- **What to do instead:** Add pytest tests for at least the API endpoints. FastAPI's TestClient makes this trivial.

### 7. Hardcoded Seed Data
- **What:** Seed data contains specific RootRise opportunities with dates that are now in the past.
- **Where:** `backend/main.py:275-333`
- **Why it's a problem:** Deadlines like `2026-01-30` are already past. Every database reset creates stale data. Not reusable for other projects.
- **What to do instead:** Either update seed data regularly, use relative dates, or provide seed data as an importable JSON file.

### 8. `gitignore` Not Named `.gitignore`
- **What:** The gitignore file is named `gitignore` without the leading dot.
- **Where:** Repository root — file is named `gitignore` instead of `.gitignore`
- **Why it's a problem:** Git does not recognize `gitignore` as a gitignore file. The rules in it have no effect. `.db` files, `.env` files, etc. are NOT being ignored by git.
- **What to do instead:** Rename to `.gitignore`.

### 9. Duplicate OS Import
- **What:** `os` is imported at line 21, then `os_module` is imported at line 360.
- **Where:** `backend/main.py:21` and `backend/main.py:360`
- **Why it's a problem:** Confusing — two names for the same module. Suggests the static files mounting was added later without reviewing existing imports.
- **What to do instead:** Use the existing `os` import.

### 10. No Error Boundaries on Frontend
- **What:** If any API call fails during `refreshData()`, the Promise.all may leave the UI in a partially updated state.
- **Where:** `frontend/index.html:862-868`
- **Why it's a problem:** `Promise.all` fails fast — if one request fails, the others' results may not be processed. No retry logic, no partial update handling.
- **What to do instead:** Use `Promise.allSettled()` and handle each result independently.

## 11. UNIQUE CONTRIBUTIONS

### The "Funding Readiness Score" Pattern

This platform introduces a **weighted readiness score** concept that is unique in the portfolio. The formula `SUM(completion_percentage * (6 - priority)) / SUM(6 - priority)` creates a single metric that:

1. Tracks multi-dimensional preparation across 8 categories (legal, financial, pitch, team, product, market, operations, documentation)
2. Weights by priority (P1 items matter more than P5 items)
3. Auto-updates status based on completion percentage (0% = not_started, 1-99% = in_progress, 100% = complete)
4. Visualizes as both a circular progress ring and per-category bar chart

This is a reusable pattern for any platform that needs to track readiness/maturity across multiple dimensions with varying importance.

### The "Dual Pipeline" Pattern

The startup vs. BD pipeline segmentation with type-based categorization is a novel organizational pattern. It maps a single data model (opportunities) to two distinct workflow contexts using type enums and constant arrays, with shared UI components that adapt their styling (teal for startup, purple for BD). This is reusable for any platform where the same entity class serves different business functions.

### The "Idempotent SQLite Migration" Pattern

While not complex, the `run_migrations()` pattern (`PRAGMA table_info` → check → `ALTER TABLE`) is a clean, zero-dependency approach to SQLite schema evolution that should become a standard template. It's simpler than Alembic for single-file apps and perfectly safe for startup-on-every-deploy scenarios.

## 12. COMPLEXITY METRICS

- **Total files:** 21 (including static assets)
- **Total lines of code (excluding node_modules, .git):** ~1,970
- **Backend files / lines:** 1 file / 715 lines
- **Frontend files / lines:** 1 file (index.html) / 891 lines + 1 file (manifest.json) / 54 lines
- **Database migration files / lines:** 0 separate files / ~15 lines embedded in main.py
- **Config files:** 5 (requirements.txt, start.sh, env.example, .python-version, gitignore)
- **Test files (if any):** 0
- **Number of API endpoints:** 16 (15 JSON API + 1 HTML)
- **Number of database tables:** 3
- **Number of frontend pages/routes:** 4 sections (Dashboard, Opportunities, Readiness, Activity)
- **Number of AI prompts/agents:** 0
- **Number of external dependencies (backend):** 3 (fastapi, uvicorn, pydantic)
- **Number of external dependencies (frontend):** 1 (Google Fonts CDN)

## 13. REUSABLE CODE FRAGMENTS

### Fragment: SQLite Context Manager
- **Purpose:** Safe database connection handling with auto-commit/rollback
- **Language:** Python
- **Code:**
```python
from contextlib import contextmanager
import sqlite3

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def db_session():
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
```
- **Where It's Used:** `backend/main.py:175-190`
- **Reuse Instructions:** Copy directly. Replace `DATABASE_PATH` with your env var. Use as `with db_session() as conn:` in every endpoint.

### Fragment: Idempotent SQLite Migration
- **Purpose:** Safely add columns to existing tables without breaking fresh installs
- **Language:** Python
- **Code:**
```python
def run_migrations(conn):
    """Run database migrations safely (idempotent). Called on every startup."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(opportunities)")
    columns = [col[1] for col in cursor.fetchall()]
    if "new_column" not in columns:
        cursor.execute("ALTER TABLE opportunities ADD COLUMN new_column TYPE DEFAULT value")
        conn.commit()
        print("Migration: Added 'new_column' to table", flush=True)
```
- **Where It's Used:** `backend/main.py:206-214`
- **Reuse Instructions:** Add one block per new column. Call inside `init_db()`. Order doesn't matter since each block is independent.

### Fragment: CORS Configuration (with fix needed)
- **Purpose:** FastAPI CORS middleware setup
- **Language:** Python
- **Code:**
```python
import os

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
- **Where It's Used:** `backend/main.py:352-358` (current code uses `["*"]` — the above is the corrected version)
- **Reuse Instructions:** Always use env var for origins. Never use `["*"]` with `allow_credentials=True`. Split comma-separated origins from env var.

### Fragment: Row Sanitization
- **Purpose:** Normalize SQLite row data to clean Python dicts
- **Language:** Python
- **Code:**
```python
def clean_row(row) -> dict:
    """Convert SQLite row to dict, handling empty strings as None for datetime fields"""
    d = dict(row)
    datetime_fields = ['deadline', 'due_date', 'created_at', 'updated_at', 'timestamp']
    nullable_fields = ['url', 'notes', 'funding_amount', 'requirements', 'contact_info',
                       'owner', 'description', 'dependencies', 'details']
    for field in datetime_fields + nullable_fields:
        if field in d and d[field] == '':
            d[field] = None
    return d
```
- **Where It's Used:** `backend/main.py:192-204`
- **Reuse Instructions:** Adapt field lists to your schema. Apply to every query result before returning.

### Fragment: Activity Logging
- **Purpose:** Transactional audit trail for entity changes
- **Language:** Python
- **Code:**
```python
def log_activity(cursor, action: str, entity_type: str, entity_id: int, details: str = None):
    cursor.execute("""
        INSERT INTO activity_log (action, entity_type, entity_id, details, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (action, entity_type, entity_id, details, datetime.utcnow().isoformat()))
```
- **Where It's Used:** `backend/main.py:336-340`
- **Reuse Instructions:** Call within the same `db_session()` as the operation. Pass the cursor, not a new connection — ensures transactional consistency.

### Fragment: Frontend API Wrapper with Toast Errors
- **Purpose:** Centralized fetch wrapper with error handling and user notification
- **Language:** JavaScript
- **Code:**
```javascript
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: { 'Content-Type': 'application/json', ...options.headers },
            ...options
        });
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast('Error connecting to server', 'error');
        throw error;
    }
}
```
- **Where It's Used:** `frontend/index.html:511-517`
- **Reuse Instructions:** Adapt `API_BASE` detection. Add 401 handling for authenticated apps. Add retry logic for flaky connections.

### Fragment: HTML Escape Utility
- **Purpose:** Prevent XSS in dynamically generated HTML
- **Language:** JavaScript
- **Code:**
```javascript
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;');
}
```
- **Where It's Used:** `frontend/index.html:745`
- **Reuse Instructions:** Apply to ALL user-generated content before inserting into HTML. Also escape single quotes (`'` → `&#39;`) if inserting into attribute values.

### Fragment: Railway Start Script
- **Purpose:** Universal Python app startup for Railway deployment
- **Language:** Bash
- **Code:**
```bash
#!/bin/bash
pip install -r requirements.txt
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
```
- **Where It's Used:** `start.sh`
- **Reuse Instructions:** Copy directly. Change the module path (`backend.main:app`) to match your app structure. The `${PORT:-8000}` pattern handles Railway's PORT injection with a local fallback.

## 14. DEPENDENCY MAP

| Service | Purpose | Required? | Env Var | Fallback |
|---------|---------|-----------|---------|----------|
| Railway | PaaS hosting | Yes (production) | PORT | 8000 (local dev) |
| SQLite | Database | Yes | DATABASE_PATH | `funding_readiness.db` (local file) |
| Google Fonts CDN | Typography (Cinzel, Raleway, JetBrains Mono) | No (degraded appearance) | None | System fonts |
| Slack API | Deadline notifications | No (not implemented) | SLACK_WEBHOOK_URL | None |
| Discord API | Notifications | No (not implemented) | DISCORD_WEBHOOK_URL | None |
| SMTP Server | Email digests | No (not implemented) | SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD | None |

**Note:** This platform has remarkably few external dependencies — only Railway for hosting and Google Fonts for typography. Everything else is self-contained. This is both a strength (simplicity, reliability) and a limitation (ephemeral storage, no auth provider, no notifications).

## 15. HANDOFF READINESS SCORE

Rate this platform on the Phase 07 criteria (1-5 each):

- [3] /5 — **Code organization** — Two-file architecture is easy to grasp initially but becomes unwieldy. Clear backend/frontend separation but no internal decomposition.
- [3] /5 — **Documentation** — README is comprehensive with API docs, data models, and deployment instructions. No inline code comments. No CLAUDE.md.
- [2] /5 — **Error handling** — Backend returns proper HTTP errors. Frontend shows toast notifications. But no input validation on frontend, no error boundaries, no retry logic, `Promise.all` failure mode is unhandled.
- [1] /5 — **Auth completeness** — API_KEY defined but never enforced. No login, no register, no JWT, no RBAC. Destructive endpoints publicly accessible.
- [2] /5 — **Deployment reliability** — Health check exists. start.sh works. But SQLite on ephemeral filesystem means data loss on every deploy. No CI/CD pipeline. No automated testing.
- [1] /5 — **Data integrity** — No RLS, no foreign keys, no indexes beyond PK, no backups, ephemeral storage. Dependencies stored as free text. `gitignore` file not named correctly.
- [0] /5 — **AI reliability** — N/A — no AI features.
- [3] /5 — **UI completeness** — Good empty states, toast notifications, responsive design, PWA support. Missing: loading skeletons, confirmation modals for edits (only delete has confirm), no optimistic updates.
- [0] /5 — **Testing** — Zero tests of any kind.
- [3] /5 — **Codex compliance** — CORS wildcard (not fixed), no auth (not implemented), Railway PORT handled correctly, Pydantic v1 pinned, SQLite empty-string handled, no AI to worry about.

**Total: 18/50** (excluding AI reliability, adjusted to 18/45 = 40%)

---

END OF PLATFORM DNA REPORT.

Key takeaway for ArchTeeStrator v2: This platform demonstrates that a **minimal, zero-dependency approach** (3 Python packages, 0 JS packages, 2 code files) can deliver a functional, polished internal tool rapidly (~3 weeks). The weaknesses are predictable: no auth, ephemeral storage, no tests. The strengths are real: instant deployability, PWA support, clean design system, and several reusable patterns (idempotent migrations, weighted scoring, dual pipelines). Future platform generation should start from this simplicity and add auth + persistent storage from day one.
