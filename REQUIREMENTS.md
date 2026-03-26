# Supersonic: Flet Application Requirements

## 1. Project Overview

**Supersonic** is an AI-powered project planning platform built as a full-stack application with a Flet (Python) frontend and a FastAPI backend. Users can create projects, manage tasks with status and priority tracking, attach messages, import data from spreadsheets, view analytics, and interact with an AI assistant for project insights.

**Delivery format**: A fully functional Flet application with multiple screens where every visible element performs an action.

---

## 2. Architecture

### 2.1 System Layers

| Layer      | Technology                   | Responsibility                                     |
| ---------- | ---------------------------- | -------------------------------------------------- |
| Frontend   | Flet 0.82.x (Python)         | UI controls, layouts, navigation, state management |
| API Client | httpx                        | HTTP communication with backend, JWT handling      |
| Backend    | FastAPI + SQLAlchemy (async) | REST API, business logic, data persistence         |
| Database   | PostgreSQL 16 (Docker)       | Relational data storage                            |
| AI Service | Pluggable stub (LLM-ready)   | Project summaries and scheduling suggestions       |

### 2.2 Request Lifecycle

1. User interacts with a Flet control (button click, form submit, tab switch).
2. The view handler calls `ApiClient`, which sends an HTTP request with a JWT bearer token.
3. FastAPI validates the token, queries PostgreSQL through SQLAlchemy, and returns JSON.
4. The view handler updates Flet controls with the response data and calls `page.update()`.

### 2.3 Separation of Concerns

- **`flet_app/`**: All frontend code. No direct database access.
- **`app/`**: All backend code. No Flet imports.
- **`flet_app/state.py`**: Centralized application state (token, user, selected project). Single source of truth.
- **`flet_app/theme.py`**: Design system. All colors, typography, spacing, and component factories defined once.
- **`flet_app/api_client.py`**: HTTP abstraction. Views never construct raw HTTP requests.
- **`flet_app/components/`**: Reusable UI components (cards, rows, badges). No business logic.
- **`flet_app/views/`**: Screen-level modules. Each view owns its layout, data loading, and event handlers.

---

## 3. Screens and Navigation

### 3.1 Navigation Structure

The app uses client-side routing via `page.on_route_change` with a `NavigationRail` for authenticated views.

| Route           | Screen              | Auth Required | Nav Rail Index  |
| --------------- | ------------------- | ------------- | --------------- |
| `/login`        | Login / Register    | No            | Hidden          |
| `/dashboard`    | Project Portfolio   | Yes           | 0               |
| `/project/{id}` | Project Detail      | Yes           | 0 (highlighted) |
| `/analytics`    | Analytics Dashboard | Yes           | 1               |
| `/ai-chat`      | AI Chat             | Yes           | 2               |
| `/profile`      | User Profile        | Yes           | 3               |

**Guard behavior**: Every authenticated route checks `state.is_authenticated()`. If false, redirect to `/login`.

### 3.2 Login Screen (`/login`)

**Purpose**: Authenticate existing users or register new accounts.

**Controls used**: `Container`, `Column`, `Row`, `Text`, `TextField` (styled), `Button`, `TextButton`.

| Requirement | Detail                                                                                         |
| ----------- | ---------------------------------------------------------------------------------------------- |
| L-1         | Toggle between "Sign In" and "Create Account" modes without page reload                        |
| L-2         | Sign In fields: username, password                                                             |
| L-3         | Register fields: username, full name (optional), password                                      |
| L-4         | Submit via button click or Enter key (`on_submit`)                                             |
| L-5         | Display error text on failed auth (red, below form)                                            |
| L-6         | Disable submit button during API call to prevent double-submit                                 |
| L-7         | On success: store JWT via `AppState.set_token()`, fetch user profile, navigate to `/dashboard` |
| L-8         | Registration auto-logs in (register then login in sequence)                                    |
| L-9         | Centered card layout with brand logo and tagline                                               |

### 3.3 Dashboard (`/dashboard`)

**Purpose**: Portfolio overview of all projects with aggregate statistics.

**Controls used**: `Container`, `Column`, `Row`, `Text`, `AlertDialog`, `TextButton`, `IconButton`, `Divider`, `FilePicker` (desktop mode).

| Requirement | Detail                                                                                                           |
| ----------- | ---------------------------------------------------------------------------------------------------------------- |
| D-1         | Stats row: total projects, active tasks, completed tasks, blocked tasks (using `stat_card` component)            |
| D-2         | Project grid: 2-column responsive layout of `project_card` components                                            |
| D-3         | Each card shows: name (truncated), description, task counts (done/active/blocked as colored dots), creation date |
| D-4         | Click a card to navigate to `/project/{id}`                                                                      |
| D-5         | Delete button on each card with confirmation snackbar                                                            |
| D-6         | "New Project" button opens `AlertDialog` with name and description fields                                        |
| D-7         | "Import" button opens file picker for CSV/XLSX/XLS upload                                                        |
| D-8         | Empty state: illustration text and CTA buttons when no projects exist                                            |
| D-9         | Data reloads on every route entry (fresh stats)                                                                  |

### 3.4 Project Detail (`/project/{id}`)

**Purpose**: Single project workspace with tabbed interface for tasks, messages, and AI.

**Controls used**: `Container`, `Column`, `Row`, `Text`, `TabBar`, `Tab`, `TabBarView`, `ProgressBar`, `AlertDialog`, `TextField`, `Dropdown`, `IconButton`, `TextButton`, `OutlinedButton`, `Divider`.

#### 3.4.1 Header

| Requirement | Detail                                                                               |
| ----------- | ------------------------------------------------------------------------------------ |
| P-1         | Breadcrumb: "Projects > {project name}" with clickable back link to `/dashboard`     |
| P-2         | Progress bar showing percentage of completed tasks                                   |
| P-3         | Edit button: opens dialog to update project name/description                         |
| P-4         | Delete button: opens confirmation dialog, deletes project, navigates to `/dashboard` |

#### 3.4.2 Tasks Tab

| Requirement | Detail                                                                                                                                 |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| T-1         | Filter chips: All, Not Started, In Progress, Completed, Blocked                                                                        |
| T-2         | Active filter highlighted with accent color                                                                                            |
| T-3         | Task list using `task_row` component: status dot, title, status badge, priority badge, assignee avatar, end date                       |
| T-4         | Edit and delete icon buttons per task row                                                                                              |
| T-5         | "Add Task" button opens dialog with fields: title, description, status (dropdown), priority (dropdown), assignee, start date, end date |
| T-6         | Edit task opens pre-filled dialog with same fields                                                                                     |
| T-7         | Delete task with snackbar confirmation                                                                                                 |
| T-8         | Empty state text when no tasks match current filter                                                                                    |

#### 3.4.3 Messages Tab

| Requirement | Detail                                                              |
| ----------- | ------------------------------------------------------------------- |
| M-1         | Chronological message list (newest first)                           |
| M-2         | Each message shows: subject, sender, date, body                     |
| M-3         | "New Message" button opens dialog with subject, sender, body fields |
| M-4         | Empty state when no messages exist                                  |

#### 3.4.4 AI Assistant Tab

| Requirement | Detail                                                                       |
| ----------- | ---------------------------------------------------------------------------- |
| A-1         | Summary section with focus area buttons: Overview, Risks, Timeline, Workload |
| A-2         | Suggestions section with free-text prompt input                              |
| A-3         | Loading indicator (`ProgressRing`) during AI generation                      |
| A-4         | Results displayed in styled containers                                       |

### 3.5 Analytics (`/analytics`)

**Purpose**: Data visualization dashboard with portfolio-level metrics.

**Controls used**: `Container`, `Column`, `Row`, `Text`, `Stack`, `ProgressRing`, `Icon`, `Divider`.

| Requirement | Detail                                                                                  |
| ----------- | --------------------------------------------------------------------------------------- |
| AN-1        | Summary stats: total tasks, completion rate (%), at-risk count, active projects         |
| AN-2        | Stacked horizontal bar chart for task status distribution (built from Container widths) |
| AN-3        | Per-project progress bars using `Stack` (background + foreground layers)                |
| AN-4        | Priority distribution horizontal bars with labels and counts                            |
| AN-5        | AI risk analysis section: iterates all projects, calls AI summary, displays results     |
| AN-6        | Loading spinner while data loads                                                        |
| AN-7        | Color legend for status categories                                                      |

### 3.6 AI Chat (`/ai-chat`)

**Purpose**: Conversational interface for AI-powered project insights.

**Controls used**: `Container`, `Column`, `Row`, `Text`, `TextField`, `Dropdown`, `dropdown.Option`, `IconButton`, `ProgressRing`.

| Requirement | Detail                                                                                             |
| ----------- | -------------------------------------------------------------------------------------------------- |
| C-1         | Project selector dropdown (loaded from API)                                                        |
| C-2         | Chat message history rendered as bubbles (user = accent/right, bot = surface/left)                 |
| C-3         | Text input with send button and Enter key support (`on_submit`)                                    |
| C-4         | Quick-action chips: Overview, Risks, Timeline, Workload (pre-fill and auto-send)                   |
| C-5         | Typing indicator (animated `ProgressRing` + "Thinking..." text) during API calls                   |
| C-6         | Messages appended dynamically to the column control list                                           |
| C-7         | Context-aware: routes to `ai_summary` (focus areas) or `ai_suggestions` (free text) based on input |

### 3.7 Profile (`/profile`)

**Purpose**: Display current user information.

**Controls used**: `Container`, `Column`, `Row`, `Text`, `Divider`.

| Requirement | Detail                                                          |
| ----------- | --------------------------------------------------------------- |
| PR-1        | Avatar circle with user initial, accent background              |
| PR-2        | Display: full name, @username, member since date                |
| PR-3        | Info card with labeled rows (username, full name, member since) |
| PR-4        | Redirect to `/login` on API error (expired token)               |

---

## 4. Components

Reusable components live in `flet_app/components/`. Each is a factory function that returns a Flet control tree.

| Component       | File               | Purpose                                       |
| --------------- | ------------------ | --------------------------------------------- |
| `nav_rail`      | `nav_rail.py`      | NavigationRail with 4 destinations + sign-out |
| `project_card`  | `project_card.py`  | Clickable project card with stats and delete  |
| `stat_card`     | `stat_card.py`     | KPI display card (label + value)              |
| `task_row`      | `task_row.py`      | Single task row with badges, actions          |
| `chat_bubble`   | `chat_bubble.py`   | User/bot chat message bubble                  |
| `file_importer` | `file_importer.py` | FilePicker wrapper for CSV/Excel              |

---

## 5. Design System

All visual tokens are centralized in `flet_app/theme.py`. No hardcoded colors, fonts, or spacing in views or components.

### 5.1 Color Palette

| Token                                               | Hex                               | Usage                         |
| --------------------------------------------------- | --------------------------------- | ----------------------------- |
| `BG`                                                | `#f8f9fa`                         | Page background               |
| `SURFACE`                                           | `#ffffff`                         | Elevated surfaces             |
| `CARD` / `CARD_BORDER`                              | `#ffffff` / `#e9ecef`             | Card backgrounds and borders  |
| `SIDEBAR`                                           | `#f1f3f5`                         | Navigation rail background    |
| `ACCENT`                                            | `#7c3aed`                         | Primary action color (violet) |
| `ACCENT_LIGHT` / `ACCENT_TEXT`                      | `#ede9fe` / `#5b21b6`             | Accent tints                  |
| `SUCCESS` / `WARNING` / `ERROR` / `INFO`            | Green / Amber / Red / Blue        | Status semantics              |
| `TEXT_PRIMARY` / `TEXT_SECONDARY` / `TEXT_TERTIARY` | `#111827` / `#6b7280` / `#9ca3af` | Text hierarchy                |

### 5.2 Typography

Font: **Inter** (Google Fonts). Three heading levels, body, secondary body, and label.

| Factory            | Size | Weight | Use              |
| ------------------ | ---- | ------ | ---------------- |
| `heading_1()`      | 28   | 700    | Page titles      |
| `heading_2()`      | 20   | 600    | Section titles   |
| `heading_3()`      | 16   | 600    | Card titles      |
| `body_text()`      | 14   | 400    | Default body     |
| `body_secondary()` | 13   | 400    | Descriptions     |
| `label_text()`     | 12   | 600    | Uppercase labels |

### 5.3 Spacing Scale

`SP_1` (4px) through `SP_10` (64px). Used for all padding, margin, and gap values.

### 5.4 Border Radius

`RADIUS_SM` (6), `RADIUS_MD` (10), `RADIUS_LG` (14), `RADIUS_XL` (20).

### 5.5 Component Factories

Pre-styled controls available from `theme.py`:

- `badge()`, `status_badge()`, `priority_badge()`: Status and priority pill badges
- `card_container()`: Card with border, radius, padding
- `accent_button()`, `outlined_button()`: Primary and secondary buttons
- `styled_textfield()`, `styled_dropdown()`: Themed form inputs
- `snackbar()`: Brief notification overlay

---

## 6. State Management

### 6.1 AppState (`flet_app/state.py`)

Centralized state object passed to all views and the API client.

| Property           | Type  | Persistence |
| ------------------ | ----- | ----------- | --------------------------------------- |
| `token`            | `str  | None`       | Persisted to `~/.supersonic/token.json` |
| `user`             | `dict | None`       | In-memory only                          |
| `selected_project` | `dict | None`       | In-memory only                          |

**Token lifecycle**:

1. On login: `set_token()` writes to disk.
2. On app launch: `_load_token()` reads from disk for auto-login.
3. On logout or 401: `clear()` wipes memory and deletes file.

### 6.2 View-Level State

Each view function uses `nonlocal` variables for local state (filter selection, dialog references, loaded data). State is re-initialized on every route entry.

---

## 7. API Integration

### 7.1 API Client (`flet_app/api_client.py`)

Synchronous HTTP client using `httpx`. All methods raise `ApiError` on failure.

| Category | Methods                                                                                                            |
| -------- | ------------------------------------------------------------------------------------------------------------------ |
| Auth     | `register()`, `login()`, `get_me()`                                                                                |
| Projects | `list_projects()`, `get_project()`, `create_project()`, `update_project()`, `delete_project()`, `import_project()` |
| Tasks    | `list_tasks()`, `get_task()`, `create_task()`, `update_task()`, `delete_task()`                                    |
| Messages | `list_messages()`, `create_message()`                                                                              |
| AI       | `ai_summary()`, `ai_suggestions()`                                                                                 |
| System   | `health()`                                                                                                         |

### 7.2 Authentication Flow

1. `POST /auth/login` returns `{"access_token": "..."}`.
2. Token stored via `AppState.set_token()`.
3. All subsequent requests include `Authorization: Bearer {token}` header.
4. On 401 response: state cleared, user redirected to `/login`.

---

## 8. Backend API (18 Endpoints)

| Method | Path                      | Description                | Auth |
| ------ | ------------------------- | -------------------------- | ---- |
| POST   | `/auth/register`          | Create user account        | No   |
| POST   | `/auth/login`             | Get JWT token              | No   |
| GET    | `/auth/me`                | Current user profile       | Yes  |
| POST   | `/projects`               | Create project             | Yes  |
| GET    | `/projects`               | List all projects          | Yes  |
| GET    | `/projects/{id}`          | Get single project         | Yes  |
| PUT    | `/projects/{id}`          | Update project             | Yes  |
| DELETE | `/projects/{id}`          | Delete project + children  | Yes  |
| POST   | `/projects/import`        | Import from spreadsheet    | Yes  |
| POST   | `/projects/{id}/tasks`    | Create task                | Yes  |
| GET    | `/projects/{id}/tasks`    | List tasks (filterable)    | Yes  |
| GET    | `/tasks/{id}`             | Get single task            | Yes  |
| PUT    | `/tasks/{id}`             | Update task                | Yes  |
| DELETE | `/tasks/{id}`             | Delete task                | Yes  |
| POST   | `/projects/{id}/messages` | Create message             | Yes  |
| GET    | `/projects/{id}/messages` | List messages              | Yes  |
| POST   | `/ai/summary`             | Generate project summary   | Yes  |
| POST   | `/ai/suggestions`         | Get scheduling suggestions | Yes  |
| GET    | `/health`                 | Health check               | No   |
| GET    | `/policy`                 | Ethics policy              | No   |

---

## 9. Database Schema

### 9.1 Models

| Model     | PK   | Key Fields                                                                            | Relationships           |
| --------- | ---- | ------------------------------------------------------------------------------------- | ----------------------- |
| `User`    | UUID | username (unique), hashed_password, full_name                                         | 1:N Projects            |
| `Project` | UUID | name, description, owner_id (FK)                                                      | 1:N Tasks, 1:N Messages |
| `Task`    | INT  | title, description, status, priority, assignee, start_date, end_date, project_id (FK) | N:M Tags                |
| `Message` | INT  | subject, body, sender, date, project_id (FK), task_id (FK, optional)                  | N:1 Task                |
| `Tag`     | INT  | name (unique)                                                                         | N:M Tasks               |

### 9.2 Cascade Rules

- Delete User: cascade to Projects.
- Delete Project: cascade to Tasks and Messages.
- Delete Task: SET NULL on Message.task_id.
- Tags: cascade both sides of join table.

---

## 10. Course Concept Coverage

This table maps every Solutions Development II topic to where it appears in Supersonic.

| Course Concept                    | Where It Appears                                                                                                           |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **HTML structure**                | Conceptual parallel: Flet controls map to HTML elements. Backend also serves Jinja2 templates.                             |
| **CSS styling**                   | `theme.py` centralizes all visual tokens (colors, spacing, radius) analogous to CSS custom properties.                     |
| **CSS selectors and specificity** | Theme factory functions (`heading_1`, `body_text`, `badge`) apply consistent styles like class selectors.                  |
| **JavaScript and DOM**            | Flet's `page.update()` is the DOM re-render. Event handlers (`on_click`, `on_change`, `on_submit`) are JS event listeners. |
| **DOM tree structure**            | Flet control tree: Page > Row > [NavigationRail, Container > Column > controls]. Parent-child nesting.                     |
| **Controls/Widgets**              | `Text`, `TextField`, `Button`, `Checkbox`, `Dropdown`, `IconButton`, `FloatingActionButton` used throughout.               |
| **Page object**                   | `ft.Page` as root. Properties: `title`, `bgcolor`, `padding`, `theme_mode`, `window.width/height`.                         |
| **Containers**                    | Used everywhere for backgrounds, padding, margins, borders, alignment, click handling, ink effects.                        |
| **Rows and Columns**              | Primary layout primitives. Dashboard grid, task rows, form layouts, stat bars.                                             |
| **Cards**                         | `card_container()` factory. Project cards, stat cards, analytics panels, message cards.                                    |
| **DataTable**                     | Backend serves structured tabular data; frontend renders via custom `task_row` components.                                 |
| **ListView**                      | Chat message history, task lists, and message lists are scrollable `Column` controls.                                      |
| **Alignment**                     | Page-level (`horizontal_alignment`), container-level (`ft.Alignment.CENTER`), row-level (`MainAxisAlignment`).             |
| **Event handling**                | `on_click`, `on_change`, `on_submit`, `on_route_change` callbacks throughout every view.                                   |
| **Navigation and routing**        | `page.on_route_change`, `page.go()`, route guards, `NavigationRail` with `on_change`.                                      |
| **AlertDialog and Modal**         | Create/edit/delete confirmations in dashboard and project views. Dialog pattern: create, assign to overlay, open.          |
| **SnackBar**                      | Feedback notifications on delete, import success/failure.                                                                  |
| **Dropdown**                      | Task status/priority selection, AI chat project selector.                                                                  |
| **Tabs**                          | Project detail: `TabBar` + `TabBarView` with Tasks, Messages, AI tabs.                                                     |
| **Images and Icons**              | `ft.Icon` and `ft.Icons.*` throughout nav, buttons, status indicators.                                                     |
| **NavigationBar/Rail**            | `NavigationRail` with 4 destinations: Dashboard, Analytics, AI Chat, Profile.                                              |
| **RGB color system**              | Hex colors defined in theme. Status colors, priority colors, accent palette.                                               |
| **Async patterns**                | `asyncio.create_task` for file picker. Timer concepts from course applied in loading states.                               |
| **HTTP GET vs POST**              | API client uses GET for reads, POST for creates/actions, PUT for updates, DELETE for removals.                             |
| **HTTPS and security**            | JWT bearer tokens, password hashing (bcrypt), token persistence, auto-logout on 401.                                       |
| **Server-client architecture**    | Flet frontend (client) communicates with FastAPI backend (server) over HTTP/JSON.                                          |
| **App types**                     | Flet produces a hybrid app: runs on desktop, web, and mobile from one Python codebase.                                     |
| **Flutter architecture**          | Flet communicates with the Flutter engine (not a wrapper). Three-layer architecture underneath.                            |
| **Flet project setup**            | Standard structure: `flet_app/` package with `main.py`, components, views, state, theme.                                   |
| **`page.update()` pattern**       | Called after every state change to push UI updates. Batched rendering.                                                     |
| **Objects and properties**        | Every control is an object. Properties modified at runtime (`text.value`, `container.visible`).                            |
| **Factory functions**             | Theme helpers and component factories for reusable, consistent UI elements.                                                |
| **File import**                   | `FilePicker` for CSV/Excel upload. Backend parses with pandas.                                                             |
| **Database connection**           | Backend connects to PostgreSQL via SQLAlchemy async. Full CRUD operations.                                                 |
| **Containerization**              | Docker Compose for PostgreSQL + backend. Reproducible deployment.                                                          |

---

## 11. Production Best Practices

| Practice                   | Implementation                                                          |
| -------------------------- | ----------------------------------------------------------------------- |
| **Separation of concerns** | Frontend, backend, state, theme, API client all in separate modules.    |
| **Centralized theming**    | Single `theme.py` file. No magic numbers in views.                      |
| **Reusable components**    | 6 component factories in `components/`.                                 |
| **State management**       | Single `AppState` object. Token persisted to disk.                      |
| **Error handling**         | Custom `ApiError` exception. Views catch errors and show user feedback. |
| **Auth guards**            | Every authenticated route checks token before rendering.                |
| **Token persistence**      | Auto-login on app relaunch. Secure clear on logout.                     |
| **API abstraction**        | Views never construct HTTP requests directly.                           |
| **Type safety**            | Pydantic schemas on backend. Typed function signatures.                 |
| **Environment config**     | All secrets in `.env`. Pydantic Settings reads them.                    |
| **Cascade deletes**        | Database enforces referential integrity. No orphaned records.           |
| **Loading states**         | `ProgressRing` spinners during async operations.                        |
| **Empty states**           | Meaningful UI when lists are empty (not blank screens).                 |
| **Feedback**               | SnackBar notifications on actions. Error text on failures.              |
| **Responsive layout**      | `expand=True`, percentage widths, min window constraints.               |

---

## 12. Running the Application

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Ports 8000 (backend) and 8550 (Flet) available

### Commands

```bash
# Start backend + database
cd ~/supersonic
docker compose up -d

# Verify backend
curl http://localhost:8000/health

# Run Flet frontend
python3 -m flet_app.main
```

### Environment Variables

| Variable                      | Default                    | Description                 |
| ----------------------------- | -------------------------- | --------------------------- |
| `DATABASE_URL`                | `postgresql+asyncpg://...` | Async PostgreSQL connection |
| `SECRET_KEY`                  | `change-me-...`            | JWT signing key             |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                       | Token lifetime              |

---

## 13. Known Limitations

| Issue                                     | Status    | Notes                                            |
| ----------------------------------------- | --------- | ------------------------------------------------ |
| FilePicker not supported in Flet web mode | Open      | Works in desktop mode (`ft.AppView.FLET_APP`)    |
| AI service returns stub responses         | By design | Pluggable interface ready for real LLM provider  |
| No real-time updates                      | Accepted  | Data refreshes on route entry, not via WebSocket |
| Single-user scoping                       | By design | Each user sees only their own projects           |
