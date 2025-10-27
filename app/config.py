from dotenv import load_dotenv
import os

load_dotenv()

# ✅ ИСПРАВЛЯЕМ:
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # ← Было "BOT_TOKEN"
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./flight_bot.db")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # ← ДОБАВЛЯЕМ!

# ⚙️ КОНФИГУРАЦИЯ ЗАПРОСОВ
class RequestConfig:
    # Бесплатные запросы
    FREE_REQUESTS_DAILY = 5  # Бесплатных запросов в день
    FREE_REQUESTS_WEEKLY = 20  # Бесплатных запросов в неделю
    RESET_TYPE = "daily"  # "daily" или "weekly"
    
    # Тарифы (Stars -> запросы)
    PRICING = {
        1: 3,   # 15 звезд = 3 запроса 1 для теста! сбросить на 15 после проверки
        45: 10,  # 45 звезд = 10 запросов
        80: 20,  # 80 звезд = 20 запросов
        150: 50, # 150 звезд = 50 запросов
    }
    
    # Промокоды
    PROMO_CODE_LENGTH = 8
    PROMO_CODE_DURATION_DAYS = 30  # Срок действия промокода
    PROMO_CODE_REQUESTS = 5  # Количество запросов за промокод по умолчанию
    
    # Сервисные коды
    SERVICE_CODE_REQUESTS = 10  # Запросов за сервисный код

# Генерация описания тарифов для интерфейса
def get_pricing_display():
    """Возвращает отформатированные тарифы для отображения"""
    return "\n".join([
        f"• {stars} ⭐ → {requests} запросов"
        for stars, requests in RequestConfig.PRICING.items()
    ])

def get_free_requests_info():
    """Возвращает информацию о бесплатных запросах"""
    if RequestConfig.RESET_TYPE == "daily":
        return f"🆓 {RequestConfig.FREE_REQUESTS_DAILY} бесплатных запросов в день"
    else:
        return f"🆓 {RequestConfig.FREE_REQUESTS_WEEKLY} бесплатных запросов в неделю"

def get_promo_info():
    """Возвращает информацию о промокодах"""
    return f"🎁 Промокод дает {RequestConfig.PROMO_CODE_REQUESTS} запросов"