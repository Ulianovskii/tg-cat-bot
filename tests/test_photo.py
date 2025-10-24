# test_photo.py
from app.bot_instance import dp, bot
from app.handlers.cat_rating import cat_router

print("=== ТЕСТ ФОТО ОБРАБОТЧИКОВ ===")

# Проверим обработчики в роутере
print(f"Обработчиков в cat_router: {len(cat_router.message.handlers)}")
for i, handler in enumerate(cat_router.message.handlers):
    print(f"{i+1}. {handler}")

# Зарегистрируем
dp.include_router(cat_router)

print(f"Обработчиков в dp после регистрации: {len(dp.message.handlers)}")
for i, handler in enumerate(dp.message.handlers):
    print(f"{i+1}. {handler}")

print("=== ТЕСТ ЗАВЕРШЕН ===")