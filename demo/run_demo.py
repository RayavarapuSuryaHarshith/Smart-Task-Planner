"""
Small demo script that calls the serverless generate_plan function locally.
Set OPENAI_API_KEY in your shell before running to use the LLM; otherwise the
fallback plan will be used.

Usage (PowerShell):
    .\.venv\Scripts\Activate.ps1
    python demo/run_demo.py
"""
import asyncio
from app.llm import generate_plan


async def main():
    goal = "Launch an MVP product in 14 days"
    plan = await generate_plan(goal, 14)
    import json
    print(json.dumps({"goal": goal, "plan": plan}, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
