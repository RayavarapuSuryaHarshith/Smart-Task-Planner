from app.llm import fallback_plan
import json

plan = fallback_plan('prepare for exams of subjects like maths, physics, chemistry', 7)
print(json.dumps(plan, indent=2))
