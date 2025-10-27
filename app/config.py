from dotenv import load_dotenv
import os

load_dotenv()

# ✅ ИСПРАВЛЯЕМ:
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # ← Было "BOT_TOKEN"
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./flight_bot.db")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # ← ДОБАВЛЯЕМ!

import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 103181087))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./flight_bot.db")

class RequestConfig:
    # Бесплатные запросы
    FREE_REQUESTS_DAILY = 5
    FREE_REQUESTS_WEEKLY = 20
    RESET_TYPE = "daily"  # "daily" или "weekly"
    
    # Тарифы (Stars -> запросы) - МЕНЯЕМ ЗДЕСЬ!
    PRICING = {
        2: 16,   # БЫЛО: 15:3, СТАЛО: 15:10 - кнопка ОБНОВИТСЯ
        45: 10,   # без изменений
        80: 20,   # без изменений
        200: 50,  # НОВЫЙ тариф - кнопка ДОБАВИТСЯ
    }
    
    # Промокоды
    PROMO_CODE_LENGTH = 8
    PROMO_CODE_DURATION_DAYS = 30
    PROMO_CODE_REQUESTS = 5
    
    # Сервисные коды
    SERVICE_CODE_REQUESTS = 10

def get_pricing_display():
    """Возвращает отформатированные тарифы для отображения"""
    display_lines = []
    for stars, requests in RequestConfig.PRICING.items():
        display_lines.append(f"• {stars} ⭐ → {requests} запросов")
    return "\n".join(display_lines)

def get_free_requests_info():
    if RequestConfig.RESET_TYPE == "daily":
        return f"🆓 {RequestConfig.FREE_REQUESTS_DAILY} бесплатных запросов в день"
    else:
        return f"🆓 {RequestConfig.FREE_REQUESTS_WEEKLY} бесплатных запросов в неделю"