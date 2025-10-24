# app/config.py
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./flight_bot.db")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")