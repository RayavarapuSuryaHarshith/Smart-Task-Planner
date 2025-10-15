from app.llm import fallback_plan
import json
plan = fallback_plan('get fit in 30 days', 30)
print(json.dumps(plan, indent=2))
