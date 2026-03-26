# Supersonic

An AI powered project planning platform built as a full stack web application. Supersonic lets teams create projects, break them into tasks, attach messages, and get intelligent summaries and scheduling suggestions from an AI assistant.

Live at `http://localhost:8000` after deployment.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Application Screens](#application-screens)
4. [Feature Breakdown](#feature-breakdown)
5. [Database Schema](#database-schema)
6. [API Reference](#api-reference)
7. [Design System](#design-system)
8. [Accessibility](#accessibility)
9. [Project Structure](#project-structure)
10. [Setup and Deployment](#setup-and-deployment)

## Architecture Overview

Supersonic follows a layered client/server architecture with clear separation between the frontend presentation layer and the backend API.

```
+--------------------------------------------------+
|                   Browser Client                  |
|                                                   |
|  +--------+   +-----------+   +---------------+  |
|  |  HTML   |   |    CSS    |   |  JavaScript   |  |
|  | Jinja2  |   |  Design   |   |   API Client  |  |
|  |Templates|   |  System   |   |  + UI Logic   |  |
|  +--------+   +-----------+   +---------------+  |
+------------------------||------------------------+
                         || HTTP / JSON
+------------------------||------------------------+
|                   FastAPI Server                  |
|                                                   |
|  +-------------+  +----------+  +-------------+  |
|  |    Page     |  |   API    |  |   Static     |  |
|  |   Routes    |  |  Routes  |  |   Files      |  |
|  | (HTML views)|  | (JSON)   |  | (CSS/JS)     |  |
|  +-------------+  +----------+  +-------------+  |
|                        ||                         |
|  +-------------+  +----------+  +-------------+  |
|  |   Schemas   |  | Services |  |  Security    |  |
|  |  (Pydantic) |  | (AI, Im- |  | (JWT, Hash)  |  |
|  |             |  |  porter) |  |              |  |
|  +-------------+  +----------+  +-------------+  |
|                        ||                         |
|  +--------------------------------------------+  |
|  |         SQLAlchemy ORM (Async)              |  |
|  |   Models: User, Project, Task, Tag, Message |  |
|  +--------------------------------------------+  |
+------------------------||------------------------+
                         || asyncpg
              +----------||----------+
              |     PostgreSQL 16    |
              |   (Docker volume)    |
              +----------------------+
```

**Request lifecycle:**

1. User opens a page in the browser. FastAPI serves an HTML template.
2. On page load, JavaScript calls the REST API with a JWT bearer token.
3. FastAPI validates the token, queries the database through SQLAlchemy, and returns JSON.
4. JavaScript renders the data into the page using DOM manipulation.
5. User actions (create, edit, delete) send JSON payloads back to the API.
6. The database persists all changes. The UI updates immediately.

## Technology Stack

| Layer                | Technology                           | Purpose                                                     |
| -------------------- | ------------------------------------ | ----------------------------------------------------------- |
| **Frontend**         | HTML5 + Jinja2                       | Page structure and server side templating                   |
| **Styling**          | CSS3 (custom properties)             | Design system with variables, animations, responsive layout |
| **Interactivity**    | Vanilla JavaScript                   | DOM manipulation, API calls, modals, toast notifications    |
| **Backend**          | FastAPI 0.115                        | Async REST API framework with automatic OpenAPI docs        |
| **ORM**              | SQLAlchemy 2.0 (async)               | Database models, queries, and relationships                 |
| **Database**         | PostgreSQL 16                        | Persistent data storage with UUID primary keys              |
| **Auth**             | JWT (python jose) + bcrypt (passlib) | Stateless token authentication and password hashing         |
| **AI Service**       | Pluggable client (stub)              | Project summaries and scheduling suggestions                |
| **File Parsing**     | pandas + openpyxl                    | Excel and CSV import for bulk task creation                 |
| **Containerization** | Docker + Docker Compose              | Reproducible deployment with health checks                  |

## Application Screens

### 1. Authentication (`/`)

Full viewport sign in and registration screen. Features:

- Animated gradient orbs and a subtle grid overlay in the background
- Glassmorphism card with backdrop blur
- Toggle between Sign In and Create Account modes
- Form validation with animated error messages
- Automatic redirect to dashboard on successful authentication
- JWT token stored in localStorage for subsequent API calls

### 2. Dashboard (`/dashboard`)

Project portfolio overview. Features:

- **Sidebar navigation** with brand logo, project list (up to 8), and user card with sign out
- **Stats bar** showing total projects, active tasks, completed tasks, and blocked tasks
- **Project cards** displayed in a responsive grid, each showing name, description, task breakdown (done / active / blocked), and creation date
- **New Project modal** with name and description fields
- **Import modal** with drag and drop file upload (supports .xlsx, .xls, .csv)
- **Delete** capability on each project card with confirmation
- Staggered entrance animations on all cards
- Empty state with call to action when no projects exist
- Mobile responsive: sidebar collapses behind a hamburger menu

### 3. Project Detail (`/project/{id}`)

Single project workspace with tabbed interface. Features:

- **Breadcrumb** navigation back to dashboard
- **Progress bar** showing percentage of tasks completed
- **Edit** and **Delete** project actions
- **Three tabs**: Tasks, Messages, AI Assistant

**Tasks tab:**

- Filter chips: All, Not Started, In Progress, Completed, Blocked
- Task rows with status dot, title, status/priority badges, assignee avatar, and due date
- Inline edit and delete actions (appear on hover)
- Add Task modal with fields for title, description, status, priority, assignee, start/end dates

**Messages tab:**

- Chronological message list with subject, sender, date, and body
- New Message modal for attaching notes and emails to the project

**AI Assistant tab:**

- Two card layout: Summary and Suggestions
- Summary card with focus area buttons (Overview, Risks, Timeline, Workload)
- Suggestions card with free text prompt input
- Loading spinners during AI generation
- Disclaimer display for AI generated content

## Feature Breakdown

### Authentication and Security

- User registration with username (min 3 chars), password (min 6 chars), optional full name
- bcrypt password hashing via passlib
- JWT access tokens with configurable expiration (default 60 minutes)
- All API endpoints (except register, login, health, policy) require Bearer token
- Automatic redirect to login on 401 responses

### Project Management

- Create, read, update, delete projects
- Each project scoped to its owner (no cross user access)
- Cascade deletion removes all child tasks and messages
- Import projects from spreadsheets: column auto detection, flexible date parsing, status/priority validation with fallback defaults

### Task Management

- Full CRUD operations on tasks within a project
- Status tracking: not_started, in_progress, completed, blocked
- Priority levels: low, medium, high, critical
- Optional assignee, start date, and end date
- Server side filtering by status and priority (query params)
- Client side filter chips for instant switching

### Messages

- Attach notes and emails to any project
- Optional task linkage for context
- Chronological listing (newest first)

### AI Assistant

- Project summary generation with optional focus areas (risks, timeline, workload)
- Scheduling and priority suggestions with optional user prompt
- Pluggable AI client: currently a deterministic stub, designed for swap to any LLM provider without changing route code

### Data Import

- Upload .xlsx, .xls, or .csv files
- Auto detects columns: Task Name (required), Project Name, Owner, Start Date, End Date, Status, Priority, Description
- Case insensitive column matching with whitespace trimming
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

- User 1:N Project (owner)
- Project 1:N Task (cascade delete)
- Project 1:N Message (cascade delete)
- Task N:M Tag (via task_tags, cascade both sides)
- Message N:1 Task (optional, SET NULL on task delete)

## API Reference

All endpoints return JSON. Authentication via `Authorization: Bearer <token>` header.

### Auth

| Method | Path             | Description                    | Auth |
| ------ | ---------------- | ------------------------------ | ---- |
| POST   | `/auth/register` | Create a new user account      | No   |
| POST   | `/auth/login`    | Get JWT access token           | No   |
| GET    | `/auth/me`       | Get current authenticated user | Yes  |

### Projects

| Method | Path               | Description                      | Auth |
| ------ | ------------------ | -------------------------------- | ---- |
| POST   | `/projects`        | Create a new project             | Yes  |
| GET    | `/projects`        | List all projects (newest first) | Yes  |
| GET    | `/projects/{id}`   | Get a single project             | Yes  |
| PUT    | `/projects/{id}`   | Update project name/description  | Yes  |
| DELETE | `/projects/{id}`   | Delete project and all children  | Yes  |
| POST   | `/projects/import` | Import project from spreadsheet  | Yes  |

### Tasks

| Method | Path                   | Description             | Auth |
| ------ | ---------------------- | ----------------------- | ---- |
| POST   | `/projects/{id}/tasks` | Create a task           | Yes  |
| GET    | `/projects/{id}/tasks` | List tasks (filterable) | Yes  |
| GET    | `/tasks/{id}`          | Get a single task       | Yes  |
| PUT    | `/tasks/{id}`          | Update task fields      | Yes  |
| DELETE | `/tasks/{id}`          | Delete a task           | Yes  |

### Messages

| Method | Path                      | Description           | Auth |
| ------ | ------------------------- | --------------------- | ---- |
| POST   | `/projects/{id}/messages` | Create a message      | Yes  |
| GET    | `/projects/{id}/messages` | List project messages | Yes  |

### AI

| Method | Path              | Description                | Auth |
| ------ | ----------------- | -------------------------- | ---- |
| POST   | `/ai/summary`     | Generate project summary   | Yes  |
| POST   | `/ai/suggestions` | Get scheduling suggestions | Yes  |

### Other

| Method | Path      | Description                | Auth |
| ------ | --------- | -------------------------- | ---- |
| GET    | `/health` | Health check               | No   |
| GET    | `/policy` | Ethics and security policy | No   |

Interactive API documentation available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

## Design System

### Color Palette

All colors are defined as CSS custom properties in `:root` for consistency across every screen.

| Token              | Value     | Usage                                                |
| ------------------ | --------- | ---------------------------------------------------- |
| `--bg-root`        | `#050508` | Page background                                      |
| `--bg-surface`     | `#0e0e12` | Sidebar, modals                                      |
| `--bg-elevated`    | `#161619` | Raised surfaces                                      |
| `--bg-card`        | `#1c1c21` | Cards, task rows                                     |
| `--bg-card-hover`  | `#222228` | Hover state for cards                                |
| `--accent`         | `#8b5cf6` | Primary action color (violet)                        |
| `--accent-hover`   | `#7c3aed` | Hover state for accent                               |
| `--success`        | `#22c55e` | Completed status, success toasts                     |
| `--warning`        | `#f59e0b` | High priority badge                                  |
| `--error`          | `#ef4444` | Blocked status, error toasts, delete actions         |
| `--info`           | `#3b82f6` | In progress status                                   |
| `--text-primary`   | `#fafafa` | Headings and body text                               |
| `--text-secondary` | `#a1a1aa` | Descriptions and secondary labels                    |
| `--text-tertiary`  | `#8b8b95` | Tertiary labels and placeholders (WCAG AA compliant) |

### Typography

Font: **Inter** (Google Fonts) with system fallbacks.

| Class              | Size                     | Weight | Use                       |
| ------------------ | ------------------------ | ------ | ------------------------- |
| `.heading-display` | 2.5rem to 4.5rem (fluid) | 700    | Hero headings             |
| `.heading-1`       | 2rem                     | 600    | Page titles               |
| `.heading-2`       | 1.5rem                   | 600    | Section titles            |
| `.heading-3`       | 1.125rem                 | 600    | Card titles               |
| `.body-large`      | 1.125rem                 | 400    | Lead paragraphs           |
| `.body`            | 0.9375rem                | 400    | Default body text         |
| `.body-small`      | 0.8125rem                | 400    | Secondary descriptions    |
| `.label`           | 0.8125rem                | 500    | Uppercase category labels |

### Component Library

- **Buttons**: primary (violet fill), secondary (outlined), ghost (text only), danger (red tint), icon only (44x44px touch target)
- **Inputs**: dark backgrounds with accent border on focus, 3px glow ring, error state variant
- **Cards**: surface color with 1px border, interactive variant with hover lift and gradient top accent
- **Badges**: status (not_started / in_progress / completed / blocked) and priority (low / medium / high / critical)
- **Modals**: overlay with backdrop blur, spring eased entrance, focus trap, escape to close
- **Toast notifications**: slide in from right, auto dismiss after 4 seconds, success / error / info variants
- **Dropzone**: dashed border area with drag and drop support, accent highlight on hover/dragover
- **Progress bar**: gradient fill from accent to purple
- **Tabs**: underline style with accent indicator on active tab
- **Filter chips**: pill shaped toggles with accent highlight when active

### Layout

Three page layouts:

1. **Auth**: centered card on full viewport, no sidebar
2. **Dashboard**: fixed sidebar (260px) + scrollable main content
3. **Project**: same sidebar + breadcrumb header + tabbed body

Responsive breakpoints:

- Below 1024px: sidebar collapses, hamburger menu appears
- Below 640px: single column project grid, stacked stats

### Animations

- **Entrance**: staggered `fadeSlideUp` on cards and task rows (30ms to 60ms delay per item)
- **Hover**: translateY lift on project cards and primary buttons
- **Modals**: scale + translateY with spring easing on open
- **Toasts**: slideInRight with fade out on dismiss
- **Auth background**: three floating gradient orbs with 20s drift animation
- **Loading**: spinner rotation, skeleton shimmer for loading states
- **Error shake**: horizontal shake on failed authentication
- All animations respect `prefers-reduced-motion: reduce`

## Accessibility

The application meets WCAG 2.1 AA guidelines:

- **Color contrast**: all text/background combinations meet 4.5:1 minimum ratio
- **Focus indicators**: visible `:focus-visible` outlines (2px accent) on all interactive elements
- **Touch targets**: all buttons and interactive elements meet the 44x44px minimum (WCAG 2.5.5)
- **Reduced motion**: `@media (prefers-reduced-motion: reduce)` disables all non essential animations
- **Modal accessibility**: `role="dialog"`, `aria-modal="true"`, `aria-labelledby` linked to title, focus trap (Tab/Shift+Tab cycles within modal), focus restore on close
- **ARIA attributes**: `role="alert"` and `aria-live="assertive"` on error messages, `role="tab"` and `aria-selected` on auth toggle, `aria-label` on all icon only buttons, `aria-hidden="true"` on decorative SVGs
- **Semantic forms**: all inputs have associated `<label>` elements with `for` attributes
- **Keyboard navigation**: full Tab order, Escape closes modals, overlay click dismisses modals
- **Font sizing**: minimum 12px (0.75rem) across all text elements
- **Custom scrollbar**: subtle styling that does not remove native scrollbar functionality

## Project Structure

```
supersonic/
|
|   .env.example          # Environment variable template
|   docker-compose.yml    # PostgreSQL + backend services
|   Dockerfile            # Python 3.12 slim container
|   requirements.txt      # Python dependencies
|   README.md             # This file
|
+-- app/
|   |   __init__.py
|   |   main.py            # FastAPI app, router registration, lifespan hook
|   |
|   +-- api/
|   |   |   __init__.py
|   |   |   deps.py         # Dependency injection (get_db, get_current_user)
|   |   |
|   |   +-- routes/
|   |       |   __init__.py
|   |       |   auth.py      # Register, login, get current user
|   |       |   projects.py  # Project CRUD + spreadsheet import
|   |       |   tasks.py     # Task CRUD with status/priority filtering
|   |       |   messages.py  # Message create and list
|   |       |   ai.py        # AI summary and suggestions
|   |       |   policy.py    # Ethics policy endpoint
|   |       |   pages.py     # HTML page routes (auth, dashboard, project)
|   |
|   +-- core/
|   |       __init__.py
|   |       config.py        # Pydantic Settings (reads from .env)
|   |       security.py      # Password hashing, JWT encode/decode
|   |
|   +-- db/
|   |       __init__.py
|   |       base.py          # SQLAlchemy DeclarativeBase
|   |       models.py        # ORM models (User, Project, Task, Tag, Message)
|   |       session.py       # Async engine and session factory
|   |
|   +-- schemas/
|   |       __init__.py
|   |       auth.py          # UserRegister, UserLogin, UserOut, Token
|   |       project.py       # ProjectCreate, ProjectUpdate, ProjectOut
|   |       task.py          # TaskCreate, TaskUpdate, TaskOut
|   |       message.py       # MessageCreate, MessageOut
|   |       ai.py            # AISummaryRequest, AISuggestionsRequest, AIResponse
|   |
|   +-- services/
|   |       __init__.py
|   |       ai_client.py     # Pluggable AI interface (stub implementation)
|   |       project_importer.py  # Excel/CSV parser
|   |
|   +-- static/
|   |   +-- css/
|   |   |       style.css    # Complete design system (1900+ lines)
|   |   +-- js/
|   |           api.js       # Fetch wrapper with JWT auth
|   |           app.js       # UI utilities (modals, toasts, focus trap)
|   |
|   +-- templates/
|           base.html        # Base template (fonts, noise overlay, scripts)
|           auth.html        # Sign in / create account page
|           dashboard.html   # Project portfolio view
|           project.html     # Project detail with tasks/messages/AI
|
+-- tests/
        __init__.py
```

## Setup and Deployment

### Prerequisites

- Docker and Docker Compose installed
- Port 8000 and 5432 available

### Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd supersonic

# 2. Create environment file
cp .env.example .env

# 3. Build and start
docker compose up --build -d

# 4. Open in browser
open http://localhost:8000
```

### Environment Variables

| Variable                      | Default                                                                      | Description                            |
| ----------------------------- | ---------------------------------------------------------------------------- | -------------------------------------- |
| `DATABASE_URL`                | `postgresql+asyncpg://supersonic_user:supersonic_pass@db:5432/supersonic_db` | Async PostgreSQL connection string     |
| `SECRET_KEY`                  | `change-me-to-a-random-secret`                                               | JWT signing key (change in production) |
| `ALGORITHM`                   | `HS256`                                                                      | JWT algorithm                          |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                                                                         | Token lifetime                         |
| `AI_API_BASE_URL`             | `http://localhost:8000/ai`                                                   | AI provider endpoint                   |
| `AI_API_KEY`                  | `not-needed-for-stub`                                                        | AI provider API key                    |

### Stopping the Application

```bash
docker compose down        # Stop containers
docker compose down -v     # Stop and remove database volume
```

### Running Without Docker

```bash
# Requires a running PostgreSQL instance
# Update DATABASE_URL in .env to point to your database

pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Course Alignment

This project demonstrates the following Solutions Development II concepts:

| Concept                  | Where It Appears                                                           |
| ------------------------ | -------------------------------------------------------------------------- |
| **HTML structure**       | Jinja2 templates with semantic elements, forms, labels                     |
| **CSS styling**          | Custom properties, selectors, specificity, responsive design               |
| **JavaScript and DOM**   | Dynamic rendering, event handling, fetch API, DOM manipulation             |
| **Layouts**              | Sidebar + main content, tabbed views, modal overlays, responsive grid      |
| **Controls and widgets** | Buttons, inputs, selects, checkboxes (filter chips), dropzone, navigation  |
| **Color system**         | 14 CSS custom properties with consistent application across all screens    |
| **Navigation**           | Sidebar with project list, breadcrumbs, tab switching between views        |
| **Backend connection**   | REST API with 18 endpoints, JWT authentication, PostgreSQL database        |
| **Multiple screens**     | Auth, Dashboard, Project Detail (3 distinct layouts, all fully functional) |
| **Containerization**     | Docker Compose with PostgreSQL and backend services                        |
