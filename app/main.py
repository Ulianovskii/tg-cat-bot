# app/main.py
import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

print("=== НАСТРОЙКА БОТА ===")

from app.bot_instance import dp, bot
print("✅ Bot instance loaded")

# Импортируем роутеры
from app.handlers.payment_handler import payment_router
from app.handlers.basic import router as basic_router
from app.handlers.photo_handler import router as photo_router

# Подключаем роутеры
dp.include_router(payment_router)
dp.include_router(basic_router)  
dp.include_router(photo_router)
print("✅ All routers loaded")

from app.db.models import Base
from app.db.database import engine

Base.metadata.create_all(bind=engine)

print(f"Итоговое количество обработчиков в dp: {len(dp.message.handlers)}")

print("=== ДИАГНОСТИКА ОБРАБОТЧИКОВ ===")
print(f"Callback handlers: {len(dp.callback_query.handlers)}")
print(f"Message handlers: {len(dp.message.handlers)}")

print("=== ЗАПУСК БОТА ===")

async def main():
    logging.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())