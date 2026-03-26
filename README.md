# Supersonic

An AI-powered project planning platform built with a **Flet (Python) desktop frontend** and a **FastAPI backend**. Users can create projects, manage tasks, attach messages, import data from spreadsheets, view analytics with visual charts, and interact with a Claude-powered AI assistant for project insights.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Application Screens](#application-screens)
4. [Key Features](#key-features)
5. [Database Schema](#database-schema)
6. [API Reference](#api-reference)
7. [Design System](#design-system)
8. [Frontend Requirements Coverage](#frontend-requirements-coverage)
9. [Project Structure](#project-structure)
10. [Setup and Deployment](#setup-and-deployment)

## Architecture Overview

Supersonic follows a layered client/server architecture. The Flet desktop frontend communicates with a FastAPI backend over HTTP/JSON. All state is managed through a centralized `AppState` object with JWT persistence.

```
+-----------------------------------------------------+
|               Flet Desktop Application               |
|                                                       |
|  +----------+   +-----------+   +------------------+ |
|  |  Views   |   |Components |   |   AppState       | |
|  | login    |   | nav_rail  |   | token (persisted)| |
|  | dashboard|   | stat_card |   | user (in-memory) | |
|  | project  |   | task_row  |   | selected_project | |
|  | analytics|   | gantt     |   +------------------+ |
|  | ai_chat  |   | chat_bubble|          |            |
|  +----------+   | file_import|          |            |
|       |         +-----------+           |            |
|       v                                 v            |
|  +----------------------------------------------+   |
|  |           ApiClient (httpx + JWT)             |   |
|  +----------------------------------------------+   |
+------------------------||----------------------------+
                         || HTTP / JSON
+------------------------||----------------------------+
|                   FastAPI Server                      |
|                                                       |
|  +-------------+  +----------+  +-----------------+  |
|  |   Routes    |  | Services |  |    Security     |  |
|  | auth        |  | ai_client|  | JWT (python-jose)|  |
|  | projects    |  | (Claude) |  | bcrypt (passlib) |  |
|  | tasks       |  | importer |  +-----------------+  |
|  | messages    |  | (pandas) |                       |
|  | ai          |  +----------+                       |
|  +-------------+       |                             |
|                        v                             |
|  +----------------------------------------------+   |
|  |         SQLAlchemy ORM (Async)                |   |
|  |   Models: User, Project, Task, Tag, Message   |   |
|  +----------------------------------------------+   |
+------------------------||----------------------------+
                         || asyncpg
              +----------||----------+
              |     PostgreSQL 16    |
              |   (Docker volume)    |
              +----------------------+
```

**Request lifecycle:**

1. User interacts with a Flet control (button click, form submit, tab switch).
2. The view handler calls `ApiClient`, which sends an HTTP request with a JWT bearer token.
3. FastAPI validates the token, queries PostgreSQL through SQLAlchemy, and returns JSON.
4. The view handler updates Flet controls with the response data and calls `page.update()`.

## Technology Stack

| Layer                | Technology                 | Purpose                                                         |
| -------------------- | -------------------------- | --------------------------------------------------------------- |
| **Frontend**         | Flet 0.82.x (Python)       | Desktop UI with controls, layouts, navigation, state management |
| **API Client**       | httpx                      | HTTP communication with backend, JWT handling                   |
| **Backend**          | FastAPI 0.115              | Async REST API with automatic OpenAPI docs                      |
| **ORM**              | SQLAlchemy 2.0 (async)     | Database models, queries, relationships                         |
| **Database**         | PostgreSQL 16 (Docker)     | Persistent data storage with UUID primary keys                  |
| **Auth**             | JWT (python-jose) + bcrypt | Stateless token authentication and password hashing             |
| **AI Service**       | Anthropic Claude (Sonnet)  | Project summaries and scheduling suggestions                    |
| **File Parsing**     | pandas + openpyxl          | Excel and CSV import for bulk task creation                     |
| **Containerization** | Docker + Docker Compose    | Reproducible backend deployment with health checks              |

## Application Screens

### 1. Login / Register (`/login`)

Full-viewport centered sign-in screen with brand logo and tagline.

- Toggle between Sign In and Create Account modes without page reload
- Username + password fields (register adds optional full name)
- Submit via button click or Enter key (`on_submit`)
- Error text displayed on failed auth
- Submit button disables during API call to prevent double-submit
- On success: JWT persisted to `~/.supersonic/token.json`, user profile fetched, navigate to dashboard
- Auto-login on app relaunch if saved token is valid

### 2. Dashboard (`/dashboard`)

Project portfolio overview with aggregate statistics.

- **NavigationRail** sidebar with Dashboard, Analytics, AI Chat, Profile destinations and sign-out button
- **Stats row**: total projects, active tasks, completed tasks, blocked tasks (using `stat_card` component)
- **Project grid**: 2-column layout of clickable `project_card` components
- Each card shows: name (truncated), description, task counts (done/active/blocked as colored dots), creation date
- **New Project** button opens `AlertDialog` with name and description fields
- **Import CSV/XLSX** button opens native OS file picker via `FilePicker` (desktop mode)
- Delete button on each card
- Empty state with CTA buttons when no projects exist
- Data reloads on every route entry

### 3. Project Detail (`/project/{id}`)

Single project workspace with tabbed interface.

**Header:**

- Breadcrumb: "Projects / {project name}" with clickable back link
- Progress bar showing percentage of completed tasks
- Edit and Delete project buttons

**Tasks tab:**

- Filter chips: All, Not Started, In Progress, Completed, Blocked (active chip highlighted)
- Task list using `task_row` component: status dot, title, status/priority badges, assignee avatar, end date
- Edit and delete icon buttons per task row
- Add Task dialog with: title, description, status dropdown, priority dropdown, assignee, start/end dates
- Empty state when no tasks exist

**Gantt tab:**

- Horizontal bar chart with tasks as rows, positioned by start/end dates
- Color-coded bars by task status (green=completed, blue=in progress, gray=not started, red=blocked)
- Date range header with month markers
- Tooltip on hover showing task details
- Unscheduled tasks listed separately below the chart

**Messages tab:**

- Chronological message list with subject, sender, date, and body
- New Message dialog with subject, sender, body fields
- Empty state when no messages exist

**AI Assistant tab:**

- Summary section with focus area buttons: Overview, Risks, Timeline, Workload
- Suggestions section with free-text prompt input
- Results displayed in styled containers

### 4. Analytics (`/analytics`)

Data visualization dashboard with portfolio-level metrics.

- Summary stats: total tasks, completion rate (%), at-risk count, active projects
- Stacked horizontal bar chart for task status distribution (built from Container widths)
- Per-project progress bars using `Stack` (background + foreground layers)
- Priority distribution horizontal bars with labels and counts
- AI risk analysis section: iterates all projects, calls Claude, displays results
- Loading spinner (`ProgressRing`) during data loads
- Color legend for status categories

### 5. AI Chat (`/ai-chat`)

Conversational interface for AI-powered project insights.

- Project selector dropdown (loaded from API)
- Chat message history rendered as bubbles (user = accent/right, bot = surface/left)
- Text input with send button and Enter key support (`on_submit`)
- Quick-action chips: Overview, Risks, Timeline, Workload (auto-send with focus)
- Typing indicator (`ProgressRing` + "Thinking..." text) during API calls
- Messages appended dynamically to the column
- Routes to `ai_summary` (focus areas) or `ai_suggestions` (free text) based on input

### 6. Profile (`/profile`)

User information display.

- Avatar circle with user initial, accent background
- Full name, @username, member since date
- Info card with labeled rows
- Redirect to login on API error (expired token)

## Key Features

### Authentication and Security

- User registration with username (min 3 chars), password (min 6 chars), optional full name
- bcrypt password hashing via passlib
- JWT access tokens with configurable expiration (default 60 minutes)
- Token persisted to `~/.supersonic/token.json` for auto-login across sessions
- Automatic redirect to login on 401 responses
- All API endpoints (except register, login, health, policy) require Bearer token

### Project Management

- Full CRUD on projects, each scoped to its owner
- Cascade deletion removes all child tasks and messages
- Import from CSV/XLSX/XLS via native OS file picker (desktop mode `FilePicker`)

### Task Management

- Full CRUD with status (not_started, in_progress, completed, blocked) and priority (low, medium, high, critical)
- Optional assignee, start date, end date
- Filter chips for instant status filtering
- Gantt chart visualization for scheduled tasks

### AI Assistant (Claude)

- Project summary generation with focus areas (risks, timeline, workload)
- Scheduling and priority suggestions with free-text prompts
- Conversational chat interface with quick-action chips
- Powered by Claude Sonnet via Anthropic SDK
- Falls back to stub responses if no API key configured

### Data Import

- Upload .xlsx, .xls, or .csv files via OS file dialog
- Auto-detects columns: Task Name (required), Project Name, Owner/Assignee, Start Date, End Date, Status, Priority, Description
- Creates project and all tasks in a single database transaction

## Database Schema

```
+----------------+       +----------------+       +----------------+
|     users      |       |    projects    |       |     tasks      |
+----------------+       +----------------+       +----------------+
| id (UUID, PK)  |<------| id (UUID, PK)  |<------| id (INT, PK)   |
| username (UQ)  |       | name           |       | project_id (FK)|
| hashed_password|       | description    |       | title          |
| full_name      |       | owner_id (FK)  |       | description    |
| created_at     |       | created_at     |       | status (enum)  |
+----------------+       | updated_at     |       | priority (enum)|
                         +----------------+       | assignee       |
                              |                   | start_date     |
                              |                   | end_date       |
                              |                   | created_at     |
                              |                   | updated_at     |
                              |                   +----------------+
                              |                        |
                              v                        v
                         +----------------+       +----------------+
                         |   messages     |       |   task_tags    |
                         +----------------+       +----------------+
                         | id (INT, PK)   |       | task_id (FK)   |
                         | project_id (FK)|       | tag_id (FK)    |
                         | task_id (FK)   |       +----------------+
                         | subject        |            |
                         | body           |            v
                         | sender         |       +----------------+
                         | date           |       |     tags       |
                         +----------------+       +----------------+
                                                  | id (INT, PK)   |
                                                  | name (UQ)      |
                                                  +----------------+
```

**Relationships:**

- User 1:N Project (owner, cascade delete)
- Project 1:N Task (cascade delete)
- Project 1:N Message (cascade delete)
- Task N:M Tag (via task_tags, cascade both sides)
- Message N:1 Task (optional, SET NULL on task delete)

## API Reference

All endpoints return JSON. Authentication via `Authorization: Bearer <token>` header.

| Method | Path                      | Description                | Auth |
| ------ | ------------------------- | -------------------------- | ---- |
| POST   | `/auth/register`          | Create user account        | No   |
| POST   | `/auth/login`             | Get JWT access token       | No   |
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
| GET    | `/policy`                 | Ethics/security policy     | No   |

Interactive API docs at `/docs` (Swagger UI) and `/redoc` (ReDoc).

## Design System

All visual tokens centralized in `flet_app/theme.py`. No hardcoded colors, fonts, or spacing in views.

### Color Palette

| Token              | Hex       | Usage                          |
| ------------------ | --------- | ------------------------------ |
| `BG`               | `#f8f9fa` | Page background                |
| `SURFACE` / `CARD` | `#ffffff` | Elevated surfaces, cards       |
| `SIDEBAR`          | `#f1f3f5` | NavigationRail background      |
| `ACCENT`           | `#7c3aed` | Primary action color (violet)  |
| `ACCENT_LIGHT`     | `#ede9fe` | Accent tints, active states    |
| `SUCCESS`          | `#16a34a` | Completed status               |
| `WARNING`          | `#d97706` | High priority                  |
| `ERROR`            | `#dc2626` | Blocked status, delete actions |
| `INFO`             | `#2563eb` | In progress status             |
| `TEXT_PRIMARY`     | `#111827` | Headings and body              |
| `TEXT_SECONDARY`   | `#6b7280` | Descriptions                   |
| `TEXT_TERTIARY`    | `#9ca3af` | Tertiary labels                |

### Typography

Font: **Inter** (Google Fonts). Factory functions: `heading_1()` (28/700), `heading_2()` (20/600), `heading_3()` (16/600), `body_text()` (14/400), `body_secondary()` (13/400), `label_text()` (12/600 uppercase).

### Component Factories

Pre-styled controls from `theme.py`: `badge()`, `status_badge()`, `priority_badge()`, `card_container()`, `accent_button()`, `outlined_button()`, `styled_textfield()`, `styled_dropdown()`, `snackbar()`.

## Frontend Requirements Coverage

This table maps every course requirement to where it is implemented in the Flet frontend.

| Course Concept                 | Implementation                                                                                                                                |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Controls/Widgets**           | `Text`, `TextField`, `Button`, `Dropdown`, `IconButton`, `ProgressBar`, `ProgressRing`, `FilePicker`, `Divider`, `Tab` used across all views  |
| **Page object**                | `ft.Page` as root: `title`, `bgcolor`, `padding`, `theme_mode`, `window.width`, `window.height`, `window.min_width`                           |
| **Containers**                 | Used everywhere for backgrounds, padding, borders, alignment, click handling, ink effects                                                     |
| **Rows and Columns**           | Primary layout primitives: dashboard grid, task rows, form layouts, stat bars, Gantt rows                                                     |
| **Cards**                      | `card_container()` factory: project cards, stat cards, analytics panels, message cards, AI results                                            |
| **ListView / Scrollable**      | Chat message history, task lists, message lists, analytics content as scrollable `Column(scroll=AUTO)`                                        |
| **Alignment**                  | Page-level (`horizontal_alignment`), container-level (`ft.Alignment.CENTER`), row-level (`MainAxisAlignment`)                                 |
| **Event handling**             | `on_click`, `on_select`, `on_submit`, `on_route_change`, `on_change` callbacks in every view                                                  |
| **Navigation and routing**     | `page.on_route_change`, `page.go()`, route guards checking `state.is_authenticated()`, `NavigationRail` with `on_change`                      |
| **AlertDialog and Modal**      | Create/edit/delete dialogs in dashboard and project views: `AlertDialog(modal=True)`, overlay append, `.open = True`                          |
| **SnackBar**                   | `theme.snackbar()` helper for feedback on delete, import, create, update actions                                                              |
| **Dropdown**                   | Task status/priority selection (`styled_dropdown`), AI chat project selector (`ft.Dropdown`)                                                  |
| **Tabs**                       | Project detail: `TabBar` + `TabBarView` with Tasks, Gantt, Messages, AI Assistant tabs                                                        |
| **Images and Icons**           | `ft.Icon` and `ft.Icons.*` throughout nav rail, buttons, status indicators, empty states                                                      |
| **NavigationRail**             | `NavigationRail` with 4 destinations (Dashboard, Analytics, AI Chat, Profile) + sign-out trailing button                                      |
| **RGB color system**           | Hex colors defined in `theme.py`: status colors, priority colors, accent palette                                                              |
| **Async patterns**             | `asyncio.create_task` for `FilePicker.pick_files()` (async in Flet 0.82.x)                                                                    |
| **HTTP methods**               | ApiClient: GET for reads, POST for creates/AI, PUT for updates, DELETE for removals                                                           |
| **Security (HTTPS/JWT)**       | JWT bearer tokens, bcrypt password hashing, token persistence to disk, auto-logout on 401                                                     |
| **Server-client architecture** | Flet frontend (client) communicates with FastAPI backend (server) over HTTP/JSON                                                              |
| **Flutter architecture**       | Flet communicates with the Flutter engine underneath (three-layer architecture)                                                               |
| **Flet project setup**         | Standard structure: `flet_app/` package with `main.py`, `state.py`, `theme.py`, `api_client.py`, `components/`, `views/`                      |
| **`page.update()` pattern**    | Called after every state change to push UI updates to the Flutter engine                                                                      |
| **Objects and properties**     | Every control is an object with mutable properties (`text.value`, `container.visible`, `dialog.open`)                                         |
| **Factory functions**          | Theme helpers (`heading_1`, `accent_button`, `status_badge`) and component factories (`project_card`, `stat_card`, `task_row`, `gantt_chart`) |
| **File import**                | `FilePicker` for CSV/Excel upload (desktop mode). Backend parses with pandas.                                                                 |
| **Database connection**        | Backend connects to PostgreSQL via SQLAlchemy async. Full CRUD across 20 endpoints.                                                           |
| **Containerization**           | Docker Compose for PostgreSQL + backend. Reproducible deployment with health checks.                                                          |
| **CSS styling (parallel)**     | `theme.py` centralizes all visual tokens (colors, spacing, radius) analogous to CSS custom properties                                         |
| **DOM tree (parallel)**        | Flet control tree: Page > Row > [NavigationRail, Container > Column > controls]. Parent-child nesting mirrors DOM.                            |
| **JavaScript/DOM (parallel)**  | `page.update()` is the re-render. Event handlers (`on_click`, `on_submit`) are the event listener equivalent.                                 |

## Project Structure

```
supersonic/
|
|   .env.example            # Environment variable template
|   docker-compose.yml      # PostgreSQL + backend services
|   Dockerfile              # Python 3.12 slim container
|   requirements.txt        # Python dependencies
|   REQUIREMENTS.md         # Detailed course requirements specification
|   README.md               # This file
|
+-- flet_app/               # Desktop frontend (Flet 0.82.x)
|   |   __init__.py
|   |   main.py             # App entry, routing, NavigationRail layout
|   |   state.py            # Centralized state (token, user, project)
|   |   theme.py            # Design system (colors, typography, factories)
|   |   api_client.py       # httpx HTTP client with JWT auth
|   |
|   +-- components/
|   |       __init__.py
|   |       nav_rail.py     # NavigationRail with 4 destinations + sign-out
|   |       project_card.py # Clickable project card with stats
|   |       stat_card.py    # KPI display card (label + value)
|   |       task_row.py     # Task list item with badges and actions
|   |       gantt_chart.py  # Gantt chart built from Containers
|   |       chat_bubble.py  # User/bot chat message bubble
|   |       file_importer.py# FilePicker wrapper for CSV/Excel import
|   |
|   +-- views/
|           __init__.py
|           login_view.py   # Sign in / register screen
|           dashboard_view.py # Project portfolio overview
|           project_view.py # Project detail (Tasks, Gantt, Messages, AI)
|           analytics_view.py # Data visualization dashboard
|           ai_chat_view.py # Conversational AI interface
|
+-- app/                    # Backend (FastAPI)
|   |   __init__.py
|   |   main.py             # FastAPI app, router registration, CORS, lifespan
|   |
|   +-- api/
|   |   |   __init__.py
|   |   |   deps.py         # Dependency injection (get_db, get_current_user)
|   |   +-- routes/
|   |           __init__.py
|   |           auth.py     # Register, login, get current user
|   |           projects.py # Project CRUD + spreadsheet import
|   |           tasks.py    # Task CRUD with status/priority filtering
|   |           messages.py # Message create and list
|   |           ai.py       # AI summary and suggestions (Claude)
|   |           policy.py   # Ethics policy endpoint
|   |
|   +-- core/
|   |       __init__.py
|   |       config.py       # Pydantic Settings (reads from .env)
|   |       security.py     # Password hashing, JWT encode/decode
|   |
|   +-- db/
|   |       __init__.py
|   |       base.py         # SQLAlchemy DeclarativeBase
|   |       models.py       # ORM models (User, Project, Task, Tag, Message)
|   |       session.py      # Async engine and session factory
|   |
|   +-- schemas/
|   |       __init__.py
|   |       auth.py         # UserRegister, UserLogin, UserOut, Token
|   |       project.py      # ProjectCreate, ProjectUpdate, ProjectOut
|   |       task.py         # TaskCreate, TaskUpdate, TaskOut
|   |       message.py      # MessageCreate, MessageOut
|   |       ai.py           # AISummaryRequest, AISuggestionsRequest, AIResponse
|   |
|   +-- services/
|           __init__.py
|           ai_client.py    # Claude API integration (Anthropic SDK)
|           project_importer.py  # Excel/CSV parser
|
+-- tests/
        __init__.py
```

## Setup and Deployment

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Ports 8000 (backend) and 5432 (database) available

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/em-ech/supersonic.git
cd supersonic

# 2. Create environment file
cp .env.example .env
# Edit .env: set AI_API_KEY to your Anthropic API key for Claude integration

# 3. Start backend + database
docker compose up --build -d

# 4. Verify backend
curl http://localhost:8000/health

# 5. Run Flet frontend
python3 -m flet_app.main
```

### Environment Variables

| Variable                      | Default                        | Description                               |
| ----------------------------- | ------------------------------ | ----------------------------------------- |
| `DATABASE_URL`                | `postgresql+asyncpg://...`     | Async PostgreSQL connection string        |
| `SECRET_KEY`                  | `change-me-to-a-random-secret` | JWT signing key (change in production)    |
| `ALGORITHM`                   | `HS256`                        | JWT algorithm                             |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                           | Token lifetime in minutes                 |
| `AI_API_KEY`                  | `not-needed-for-stub`          | Anthropic API key for Claude AI assistant |

### Stopping the Application

```bash
docker compose down        # Stop containers
docker compose down -v     # Stop and remove database volume
```
