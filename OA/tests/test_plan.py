import asyncio
from app.llm import generate_plan, fallback_plan
from app.main import plan, plan_save, get_plans
from app.main import GoalIn


def test_fallback_plan_basic():
    tasks = fallback_plan('Launch X', 10)
    assert isinstance(tasks, list)
    assert len(tasks) > 0


def test_generate_plan_fallback():
    # Ensure generate_plan returns a list when OPENAI_API_KEY is not set in CI
    res = asyncio.run(generate_plan('Launch X in 7 days', 7))
    assert isinstance(res, list) or isinstance(res, dict)


def test_plan_function():
    # Call the route handler directly
    gi = GoalIn(goal='Test goal', due_days=5)
    res = asyncio.run(plan(gi))
    assert 'goal' in res and 'plan' in res


def test_save_and_list_plan():
    # Save a plan via plan_save() then list via get_plans()
    gi = GoalIn(goal='Save goal', due_days=3)
    res = asyncio.run(plan_save(gi))
    assert 'saved_id' in res
    rows = asyncio.run(get_plans())
    assert isinstance(rows, list)
    assert any(r['goal'] == 'Save goal' for r in rows)
