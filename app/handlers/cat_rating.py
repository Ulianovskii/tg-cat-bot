# app/handlers/cat_rating.py
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from app.services.cat_analyzer import cat_analyzer
from app.db.database import SessionLocal
from app.db.models import UserLimit
from datetime import date
import logging

logger = logging.getLogger(__name__)

cat_router = Router()
MAX_REQUESTS = 10

user_last_photos = {}

# Клавиатуры
empty_rating_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Перейти в меню")]],
    resize_keyboard=True
)

photo_received_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оценить этого котика")],
        [KeyboardButton(text="Перейти в меню")]
    ],
    resize_keyboard=True
)

# ДИАГНОСТИКА: Простой обработчик фото
@cat_router.message(F.photo)
async def handle_photo(message: Message):
    """Обработка загруженного фото"""
    user_id = message.from_user.id
    logger.info(f"✅ Photo received from user {user_id}")
    
    try:
        # Сохраняем file_id последнего фото
        photo = message.photo[-1]
        user_last_photos[user_id] = photo.file_id
        
        await message.answer(
            "✅ Фото получено! Нажми 'Оценить этого котика' для анализа 🐱",
            reply_markup=photo_received_keyboard
        )
        logger.info(f"✅ Photo saved for user {user_id}, keyboard sent")
    except Exception as e:
        logger.error(f"❌ Error saving photo: {e}")
        await message.answer("Ой! Не удалось сохранить фото. Попробуй еще раз! 😿", reply_markup=empty_rating_keyboard)

@cat_router.message(F.text == "Оценить этого котика")
async def analyze_photo(message: Message):
    """Анализ сохраненного фото"""
    user_id = message.from_user.id
    today = date.today()
    
    logger.info(f"🔍 Analyze photo button pressed by user {user_id}")
    
    # Проверяем есть ли фото
    if user_id not in user_last_photos:
        await message.answer("Сначала загрузи фото котика! 📸", reply_markup=empty_rating_keyboard)
        return
    
    # Проверяем лимит
    with SessionLocal() as db:
        user = db.query(UserLimit).filter(UserLimit.user_id == user_id).first()
        
        if not user:
            await message.answer("Сначала активируй лимит в главном меню!", reply_markup=empty_rating_keyboard)
            return
        
        if user.last_reset < today:
            user.used_requests = 0
            user.last_reset = today
            db.commit()
        
        if user.used_requests >= MAX_REQUESTS:
            await message.answer("Бесплатные запросы закончились! Приходи завтра! 🐾", reply_markup=empty_rating_keyboard)
            return
    
    try:
        processing_msg = await message.answer("Анализирую котика... 🔍")
        
        # Получаем сохраненное фото
        file_id = user_last_photos[user_id]
        from app.bot_instance import bot
        file = await bot.get_file(file_id)
        photo_bytes = await bot.download_file(file.file_path)
        
        logger.info(f"✅ Photo downloaded for analysis, size: {len(photo_bytes.getvalue())} bytes")
        
        # Анализируем
        analysis_result = await cat_analyzer.analyze_cat_image(photo_bytes.getvalue())
        
        # Списываем запрос
        with SessionLocal() as db:
            user = db.query(UserLimit).filter(UserLimit.user_id == user_id).first()
            if user:
                user.used_requests += 1
                db.commit()
                remaining = MAX_REQUESTS - user.used_requests
        
        # Удаляем фото
        del user_last_photos[user_id]
        
        await processing_msg.delete()
        await message.answer(
            f"{analysis_result}\n\n📊 Осталось запросов: {remaining}",
            reply_markup=empty_rating_keyboard
        )
        logger.info(f"✅ Photo analyzed successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error analyzing photo: {e}")
        await message.answer("Ой! Не удалось проанализировать фото. Попробуй еще раз! 😿", reply_markup=empty_rating_keyboard)

@cat_router.message(F.text == "Перейти в меню")
async def back_to_menu(message: Message):
    """Возврат в главное меню"""
    user_id = message.from_user.id
    if user_id in user_last_photos:
        del user_last_photos[user_id]
    
    await message.answer("Возвращаемся в меню!", reply_markup=ReplyKeyboardRemove())
    from app.handlers.basic import MAIN_MENU_KEYBOARD
    await message.answer("Выбери действие:", reply_markup=MAIN_MENU_KEYBOARD)

# ДИАГНОСТИКА: Обработчик всех сообщений в роутере
@cat_router.message()
async def debug_all_messages(message: Message):
    """Диагностический обработчик всех сообщений в роутере"""
    logger.info(f"DEBUG: Message in cat_router: '{message.text}' from user {message.from_user.id}")