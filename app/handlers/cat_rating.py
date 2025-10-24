# app/handlers/cat_rating.py
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from app.bot_instance import bot
from app.db.database import SessionLocal
from app.db.models import UserLimit
from datetime import date
import logging
from app.services.openai_analyzer import analyze_cat_image

logger = logging.getLogger(__name__)

cat_router = Router()
MAX_REQUESTS = 10

user_last_photos = {}

photo_received_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оценить этого котика")],
        [KeyboardButton(text="Оценить другого котика")]
    ],
    resize_keyboard=True
)

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оценить котика")],
        [KeyboardButton(text="Мой профиль")],
        [KeyboardButton(text="Помощь")]
    ],
    resize_keyboard=True
)

@cat_router.message(F.photo)
async def handle_cat_photo(message: Message):
    """Обработчик загрузки фото котика"""
    user_id = message.from_user.id
    logger.info(f"✅ Photo received from user {user_id}")
    
    try:
        photo = message.photo[-1]
        user_last_photos[user_id] = photo.file_id
        
        await message.answer(
            "✅ Фото получено! Что хотите сделать?",
            reply_markup=photo_received_keyboard
        )
        logger.info(f"✅ Photo saved for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error saving photo: {e}")
        await message.answer("😿 Не удалось сохранить фото. Попробуй еще раз!", reply_markup=main_menu_keyboard)

@cat_router.message(F.text == "Оценить этого котика")
async def analyze_current_photo(message: Message):
    """Анализ текущего сохраненного фото через нейросеть"""
    user_id = message.from_user.id
    today = date.today()
    
    logger.info(f"🔍 Analyze current photo by user {user_id}")
    
    if user_id not in user_last_photos:
        await message.answer("📸 Сначала загрузи фото котика!", reply_markup=main_menu_keyboard)
        return
    
    with SessionLocal() as db:
        user = db.query(UserLimit).filter(UserLimit.user_id == user_id).first()
        