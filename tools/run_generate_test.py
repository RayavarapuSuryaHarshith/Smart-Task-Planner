import asyncio
from app.llm import generate_plan, get_openai_key

async def main():
    print('OpenAI key:', bool(get_openai_key()))
    plan = await generate_plan('prepare for exams of subjects like maths, physics, chemistry', 7)
    import json
    print(json.dumps(plan, indent=2))

asyncio.run(main())
