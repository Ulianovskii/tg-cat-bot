from dotenv import load_dotenv
import os

load_dotenv()

# ✅ ИСПРАВЛЯЕМ:
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # ← Было "BOT_TOKEN"
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./flight_bot.db")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # ← ДОБАВЛЯЕМ!