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

# Импортируем bot и dp
from app.bot_instance import bot, dp
print("✅ Bot instance loaded")

# Импортируем ВСЕ роутеры
from app.handlers.basic import router as basic_router
from app.handlers.payment_handler import payment_router
from app.handlers.admin_handler import admin_router

# Подключаем роутеры в правильном порядке
dp.include_router(basic_router)    # Основные команды и обработка текста
dp.include_router(payment_router)  # Платежи
dp.include_router(admin_router)    # Админка
print("✅ All routers loaded")

from app.db.models import Base
from app.db.database import engine

# Создаем только НОВЫЕ таблицы
try:
    Base.metadata.create_all(bind=engine)
except:
    pass

print("=== ЗАПУСК БОТА ===")

# ПРОВЕРКА КОНФИГА
from app.config import RequestConfig
print("✅ Config loaded")
print(f"PRICING: {RequestConfig.PRICING}")

async def main():
    logging.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())