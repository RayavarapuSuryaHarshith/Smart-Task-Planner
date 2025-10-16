from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from pydantic import BaseModel
from .llm import generate_plan
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from . import db
from .db import init_db, save_plan, list_plans
from .db import delete_plan, clear_plans
import json

app = FastAPI(title="Smart Task Planner")

# Basic logging
logging.basicConfig(level=logging.INFO)

# Allow CORS from common local dev origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


class GoalIn(BaseModel):
    goal: str
    due_days: int | None = None


@app.post("/plan")
async def plan(goal_in: GoalIn, request: Request):
    if not goal_in.goal or not goal_in.goal.strip():
        raise HTTPException(status_code=400, detail="goal is required")
    try:
        logging.info(f"/plan called with goal={goal_in.goal!r} due_days={goal_in.due_days}")
        
        # Check for API key in request header
        api_key = request.headers.get("X-Groq-Key")
        if api_key:
            # Temporarily set the API key for this request
            import os
            original_key = os.environ.get("GROQ_API_KEY")
            os.environ["GROQ_API_KEY"] = api_key
            
        import time
        start = time.time()
        plan = await generate_plan(goal_in.goal, goal_in.due_days)
        elapsed = time.time() - start
        
        # Restore original API key
        if api_key:
            if original_key:
                os.environ["GROQ_API_KEY"] = original_key
            else:
                os.environ.pop("GROQ_API_KEY", None)
        
        logging.info(f"/plan finished in {elapsed:.3f}s with {'AI' if api_key else 'fallback'}")
        return {"goal": goal_in.goal, "plan": plan, "ai_used": bool(api_key)}
    except Exception as e:
        logging.exception("Error generating plan")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plan/save")
async def plan_save(goal_in: GoalIn, request: Request):
    try:
        logging.info(f"/plan/save called with goal={goal_in.goal!r} due_days={goal_in.due_days}")
        
        # Check for API key in request header
        api_key = request.headers.get("X-Groq-Key")
        if api_key:
            import os
            original_key = os.environ.get("GROQ_API_KEY")
            os.environ["GROQ_API_KEY"] = api_key
            
        plan = await generate_plan(goal_in.goal, goal_in.due_days)
        
        # Restore original API key
        if api_key:
            if original_key:
                os.environ["GROQ_API_KEY"] = original_key
            else:
                os.environ.pop("GROQ_API_KEY", None)
        
        # ensure DB exists
        init_db()
        saved = save_plan(goal_in.goal, goal_in.due_days, json.dumps(plan))
        logging.info(f"/plan/save saved id={saved.id}")
        return {"saved_id": saved.id, "goal": saved.goal, "ai_used": bool(api_key)}
    except Exception as e:
        logging.exception("Error generating or saving plan")
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/plans')
async def get_plans():
    init_db()
    rows = list_plans()
    logging.info(f"/plans returning {len(rows)} rows")
    return [{"id": r.id, "goal": r.goal, "due_days": r.due_days, "created_at": r.created_at.isoformat(), "data": json.loads(r.data)} for r in rows]


@app.delete('/plans/{plan_id}')
async def remove_plan(plan_id: int):
    init_db()
    ok = delete_plan(plan_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"deleted": plan_id}


@app.delete('/plans')
async def remove_all_plans():
    init_db()
    count = clear_plans()
    return {"deleted_count": count}


@app.get('/health')
async def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
