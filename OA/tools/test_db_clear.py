from app.db import init_db, clear_plans, list_plans, save_plan

init_db()
print('Before:', len(list_plans()))
save_plan('temp goal', 1, '[]')
print('After add:', len(list_plans()))
count = clear_plans()
print('Cleared:', count)
print('After clear:', len(list_plans()))
