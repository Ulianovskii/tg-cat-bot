# test_router_handlers.py
import sys
import os
sys.path.append(os.getcwd())

from app.handlers.cat_rating import cat_router

print("=== ОБРАБОТЧИКИ В CAT_ROUTER ===")
print(f"Всего обработчиков: {len(cat_router.message.handlers)}")
for i, handler in enumerate(cat_router.message.handlers):
    print(f"{i+1}. {handler}")