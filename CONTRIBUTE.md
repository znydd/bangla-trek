# Contributing to Bangla Trek

Welcome to the Bangla Trek codebase! This document outlines the architecture of the project, how to precisely set up your local development environment using `uv` and Docker, and the strict guidelines for contributing to this fullstack application.

## 1. Architecture Overview

Bangla Trek is a highly-performant fullstack web application consisting of a modern Python 3.12+ backend and a React 19 frontend.

- **Backend:** Powered by **FastAPI**, with **SQLAlchemy 2.0 (Async)** for ORM, **Alembic** for database migrations, and **PostgreSQL 17** as the database. It uses **Pydantic Settings** for configuration and **PyJWT** for custom JWT authentication logic. External file storage is handled by **Cloudinary**. Fast dependency management is driven by **uv**.
- **Frontend:** Built with **React 19** and **Vite 6**. It utilizes the **TanStack suite** (Router for type-safe routing and Query for server state management) and **Zustand** for lightweight global state. Styling is constructed completely with **Tailwind CSS v4** coupled with **Base UI** and **shadcn/ui** components. 

---

## 2. Prerequisites

Before you start, ensure you have the following installed on your machine:
- **Python** 3.12+
- **[uv](https://github.com/astral-sh/uv)** (The hyper-fast Python package installer and resolver)
- **Node.js** 18+ and **npm** (or yarn/pnpm)
- **Docker Compose** (for running the local PostgreSQL database)
- **Git**

---

## 3. Local Setup & Installation

### Step 1: Start the Database via Docker
The application relies on PostgreSQL. A configured `docker-compose.yml` is provided at the root containing the Postgres 17 database structure.
1. From the project root, start the database detached:
   ```bash
   docker compose up -d
   ```
   *(This launches the `db` service on port 5432 with the database named `bangla_trek` and user credentials `postgres` / `postgres`).*

### Step 2: Backend Setup (using `uv`)

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```
2. **Install exact dependencies:**
   Since we use `pyproject.toml`, `uv` simplifies the virtual environment creation and package installation into one ultra-fast command:
   ```bash
   uv sync
   ```
   *(This automatically creates a `.venv` directory and installs FastAPI, SQLAlchemy, Alembic, psycopg2-binary, and other dependencies declared in pyproject).*
3. **Environment Variables:**
   Copy the example environment variables and fill in your actual credentials. Ensure your `DATABASE_URL` matches the Docker Compose configuration (`postgresql+psycopg://postgres:postgres@localhost:5432/bangla_trek`).
   ```bash
   cp .env.example .env
   ```
4. **Run Migrations:**
   Apply Alembic migrations to build the database schema. Use `uv run` to execute within the managed context:
   ```bash
   uv run alembic upgrade head
   ```

### Step 3: Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```
2. **Install dependencies:**
   ```bash
   npm install
   ```
3. **Generate Routes (TanStack Router):**
   *(If route files have changed without the dev server running, manually regenerate the route tree)*
   ```bash
   npm run routes:generate
   ```

---

## 4. Running the Application

To run the application locally, you will need two terminal windows:

**Terminal 1 (Backend):**
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```
*The backend API will be available at http://localhost:8000. You can view the automated Swagger docs at http://localhost:8000/docs.*

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```
*The frontend application will be running at http://localhost:5173.*

---

## 5. Project Structure

### Backend Modules (`/backend`)
- **`app/api/v1/`**: API endpoint definitions (e.g., `community.py`, `auth.py`, `router.py`).
- **`app/models/`**: SQLAlchemy database models.
- **`app/schemas/`**: Pydantic models for incoming payload validation and outgoing responses.
- **`app/services/`**: Core business logic separating API controllers from database actions (e.g., `community_service.py`).
- **`alembic/`**: Configuration and version scripts for database migrations.

### Frontend Modules (`/frontend`)
- **`src/routes/`**: File-based routing structured through TanStack Router. Includes layout wrappers like `_authenticated/`.
- **`src/components/`**: Reusable React components. Includes domains (`community/`, `layout/`) and primitives (`ui/` using Base UI).
- **`src/services/`**: API logic abstracting backend network requests (fetches/Axios).
- **`src/types/`**: Frontend TypeScript definitions.
- **`src/lib/`**: Utility functions like `cn()` for Tailwind styling.

---

## 6. Development Guidelines

- **Backend:**
  - Fast execution: Always prefix tools with `uv run` (e.g., `uv run pytest`).
  - Always validate incoming API requests and outgoing responses using **Pydantic schemas** (`app/schemas`).
  - Keep controllers thin in `app/api`. Push core logic down to `app/services/`.
  - Treat SQLAlchemy database models strictly as domain structures; avoid leaking SQLAlchemy logic into the routing tier.

- **Frontend:**
  - Utilize **TanStack Query** (`useQuery`, `useMutation`) for syncing server state, utilizing its automatic caching mechanisms.
  - Apply global UI state (like modales or themes) through **Zustand**.
  - Construct styling utilizing **Tailwind v4** utility classes entirely.
  - When utilizing primitive UI components, refer to our `src/components/ui/` elements powered by **Base UI**. Notably, for composition, Base UI often applies the `render` prop (e.g., `<Button render={<Link />} />`) over the typical Shadcn/Radix `asChild` prop.

---

## 7. Git Workflow & Commits (Strict)

When collaborating on this repository, **you must strictly follow this Git branch and Pull Request workflow**.

1. **Never commit directly to `dev` or `master`.**
   - The `dev` branch is the protected integration branch.
   - The `master` branch is for production releases only.

2. **Always work on a Feature Branch:**
   Branch off of `dev`:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   # Or bugfix/your-bugfix-name
   ```

3. **Make Small, Related Commits:**
   Instead of humongous monolithic commits, group your logic into smaller, descriptive commits containing only the related alterations. Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) standard:
   - `feat(frontend): add responsive image gallery`
   - `fix(backend): resolve community model relation type error`
   - `chore: update dependencies and typescript configs`

4. **Pull Request (PR) to Dev:**
   Once your feature is complete and tested:
   ```bash
   git push origin feature/your-feature-name
   ```
   - Open a Pull Request pointing to the `dev` branch.
   - Describe what your PR accomplishes.
   - Wait for a code review before it can be merged into `dev`.

---
*Happy routing and hacking! Submit an issue if you encounter roadblocks setting up.*
