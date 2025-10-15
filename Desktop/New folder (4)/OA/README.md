# Smart Task Planner (minimal)

This repository contains a minimal implementation of a Smart Task Planner: a backend API that breaks a user goal into actionable tasks with timelines and dependencies. It uses an LLM when `OPENAI_API_KEY` is set, otherwise a deterministic fallback heuristic.

Files created:
- `app/main.py` - FastAPI app with `POST /plan` and a simple frontend
- `app/llm.py` - LLM helper with OpenAI integration and fallback
- `app/templates/index.html` - Simple UI to submit a goal and view the plan
- `tests/test_plan.py` - pytest tests for the API
- `requirements.txt` - Python dependencies


## Quick Start

**Option 1: Simple run script (recommended)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Optional: Set OpenAI key (restart shell after setx)
setx OPENAI_API_KEY "your_key_here"
python run.py
```

**Option 2: Direct uvicorn**
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000 to use the UI.

Database (SQLite)
- By default an SQLite file `plans.db` will be created in the repo root when you first save a plan.
- You can override by setting `TASKPLANNER_DB_URL` to another SQLAlchemy URL.

API endpoints
- POST /plan — generate a plan (body: {"goal":..., "due_days": ...})
- POST /plan/save — generate and save a plan to the DB; returns saved id
- GET /plans — list saved plans (latest first)

Example: save a plan (PowerShell)

```powershell
$body = @{ goal = 'Launch MVP in 10 days'; due_days = 10 } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/plan/save -Method Post -Body $body -ContentType 'application/json'
```

Testing

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q
```

Notes on security and keys
- Never paste your OpenAI API key in public repositories or chat. Set it in your shell using `setx` or place it in a local `.env` and load it securely.

Next deliverables
- Add a short demo video showing the UI and the save/list endpoints (I can provide a script for recording).
- Improve prompt engineering and JSON parsing/validation for production-ready usage.

Frontend (React + Vite)
- Frontend source lives in `frontend/`. It builds into `app/static` so the FastAPI app can serve the built assets.
- To build locally:

```powershell
cd frontend
npm install
npm run build
```

Continuous Integration
- A GitHub Actions workflow is included at `.github/workflows/ci.yml`. It will build the frontend and run Python tests on push/PR to `main`.


Deliverables to produce next:
- Demo video showing creating a plan in the UI and explaining prompt design
- Expand plan parser/validation and add DB storage (SQLite)

Deployment
----------

There are two recommended ways to deploy this project: a Docker image (recommended for reproducible deployment) and local development with docker-compose.

1) Build & run locally with docker-compose

Make sure you have Docker and docker-compose installed. From the repo root run:

```powershell
docker compose build
docker compose up
```

The service will be available at http://localhost:8000. To stop:

```powershell
docker compose down
```

2) Build and publish to GitHub Container Registry (GHCR)

The repository includes a GitHub Actions workflow at `.github/workflows/docker-publish.yml` that builds and publishes an image to GHCR on pushes to `main`.

To enable it:
- Create a repository on GitHub and push your code (do not push any `.env` containing secrets).
- Make sure `GITHUB_TOKEN` is available (it's provided automatically for Actions). The workflow pushes to `ghcr.io/<owner>/<repo>` by default.

3) Environment variables

Create a `.env` or set system environment variables for production secrets. Important variables:
- `OPENAI_API_KEY` — (optional) OpenAI API key for AI planning
- `TASKPLANNER_DB_URL` — (optional) full SQLAlchemy URL; defaults to `sqlite:///./plans.db`

Notes
- The Dockerfile builds the frontend during image build using Node + Vite and copies the output into `app/static` so FastAPI serves it.
- For production use, consider running uvicorn with multiple workers behind a process manager (Gunicorn with uvicorn workers) and mounting persistent volumes for the SQLite DB or using a managed database.

