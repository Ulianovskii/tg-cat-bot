import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

print("=== НАСТРОЙКА БОТА ===")

# ЗАПУСКАЕМ ПРОСТУЮ МИГРАЦИЮ
try:
    from app.db.simple_migrate import simple_migrate
    simple_migrate()
    print("✅ Database migration completed")
except Exception as e:
    print(f"⚠️ Migration warning: {e}")
    # Продолжаем работу даже если миграция не удалась

from app.bot_instance import dp, bot
print("✅ Bot instance loaded")

# Импортируем роутеры
from app.handlers.payment_handler import payment_router
from app.handlers.basic import router as basic_router
from app.handlers.photo_handler import router as photo_router
from app.handlers.admin_handler import admin_router

# Подключаем роутеры
dp.include_router(payment_router)
dp.include_router(basic_router)
dp.include_router(photo_router)
dp.include_router(admin_router)
print("✅ All routers loaded")

from app.db.models import Base
from app.db.database import engine

# Создаем только НОВЫЕ таблицы (не пересоздаем users)
try:
    Base.metadata.create_all(bind=engine)
except:
    pass  # Таблицы уже существуют

print("=== ЗАПУСК БОТА ===")


print("=== НАСТРОЙКА БОТА ===")

# ПРОВЕРКА КОНФИГА
from app.config import RequestConfig
print("✅ Config loaded")
print(f"PRICING: {RequestConfig.PRICING}")
print(f"CONFIG FILE: {__file__}")

from app.bot_instance import dp, bot
print("✅ Bot instance loaded")

async def main():
    logging.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())