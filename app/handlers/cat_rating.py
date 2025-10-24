# app/handlers/cat_rating.py
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.services.cat_analyzer import cat_analyzer
from app.bot_instance import bot
from app.db.database import SessionLocal
from app.db.models import UserLimit
from datetime import date
import logging

logger = logging.getLogger(__name__)

cat_router = Router()
MAX_REQUESTS = 10

# Храним последние фото пользователей {user_id: file_id}
user_last_photos = {}

# Клавиатура после получения фото
photo_received_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оценить этого котика")],
        [KeyboardButton(text="Оценить другого котика")]
    ],
    resize_keyboard=True
)

# Главное меню
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
        # Сохраняем file_id последнего фото
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
    
    # Проверяем есть ли фото
    if user_id not in user_last_photos:
        await message.answer("📸 Сначала загрузи фото котика!", reply_markup=main_menu_keyboard)
        return
    
    # Проверяем лимит запросов
    with SessionLocal() as db:
        user = db.query(UserLimit).filter(UserLimit.user_id == user_id).first()
        
        if not user:
            await message.answer("❌ Сначала активируй лимит в главном меню!", reply_markup=main_menu_keyboard)
            return
        
        # Сбрасываем лимит если новый день
        if user.last_reset < today:
            user.used_requests = 0
            user.last_reset = today
            db.commit()
        
        # Проверяем не превышен ли лимит
        if user.used_requests >= MAX_REQUESTS:
            await message.answer("😿 Бесплатные запросы закончились! Приходи завтра! 🐾", reply_markup=main_menu_keyboard)
            return
    
    try:
        # Сообщение о начале анализа
        processing_msg = await message.answer("🔍 Нейросеть анализирует котика...")
        
        # Получаем сохраненное фото
        file_id = user_last_photos[user_id]
        file = await bot.get_file(file_id)
        photo_bytes = await bot.download_file(file.file_path)
        
        logger.info(f"✅ Photo downloaded for analysis, size: {len(photo_bytes.getvalue())} bytes")
        
        # Анализируем через нейросеть
        analysis_result = await cat_analyzer.analyze_cat_image(photo_bytes.getvalue())
        
        # Обновляем счетчик запросов
        with SessionLocal() as db:
            user = db.query(UserLimit).filter(UserLimit.user_id == user_id).first()
            if user:
                user.used_requests += 1
                db.commit()
                remaining = MAX_REQUESTS - user.used_requests
        
        # Удаляем сообщение "анализируем"
        await processing_msg.delete()
        
        # Отправляем результат от нейросети
        await message.answer(
            f"😸 {analysis_result}\n\n📊 Осталось запросов: {remaining}",
            reply_markup=main_menu_keyboard
        )
        
        # Очищаем сохраненное фото
        del user_last_photos[user_id]
        
        logger.info(f"✅ Photo analyzed successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error analyzing photo: {e}")
        await message.answer("😿 Не удалось проанализировать фото. Попробуй еще раз!", reply_markup=main_menu_keyboard)

@cat_router.message(F.text == "Оценить другого котика")
async def analyze_different_photo(message: Message):
    """Запрос нового фото котика"""
    user_id = message.from_user.id
    
    # Очищаем предыдущее фото
    if user_id in user_last_photos:
        del user_last_photos[user_id]
    
    await message.answer(
        "📸 Отправь фото нового котика для оценки!",
        reply_markup=ReplyKeyboardRemove()
    )
    logger.info(f"🔄 User {user_id} requested new photo")

@cat_router.message(F.text == "Перейти в меню")
async def back_to_menu(message: Message):
    """Возврат в главное меню"""
    user_id = message.from_user.id
    
    # Очищаем сохраненное фото
    if user_id in user_last_photos:
        del user_last_photos[user_id]
    
    await message.answer(
        "🏠 Возвращаемся в главное меню!",
        reply_markup=main_menu_keyboard
    )
    logger.info(f"🏠 User {user_id} returned to main menu")

# Обработчик для главного меню "Оценить котика"
@cat_router.message(F.text == "Оценить котика")
async def start_cat_rating(message: Message):
    """Начало процесса оценки котика"""
    await message.answer(
        "📸 Отправь фото котика для оценки!",
        reply_markup=ReplyKeyboardRemove()
    )
    logger.info(f"📸 User {user_id} started cat rating process")