# app/handlers/basic.py

from aiogram import types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from datetime import date
import logging
import random

from app.bot_instance import dp
from app.db.database import SessionLocal
from app.db.models import UserLimit
from app.services.cat_analyzer import cat_analyzer

MAX_REQUESTS = 10
logger = logging.getLogger(__name__)

# Храним последние фото пользователей
user_last_photos = {}

# Главное меню с 3 кнопками
MAIN_MENU_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Узнать оставшийся лимит", callback_data="check_limit")],
        [InlineKeyboardButton(text="Пополнить лимит", callback_data="topup_limit")],
        [InlineKeyboardButton(text="Оценить котика", callback_data="rate_cat")]
    ]
)

# Клавиатура когда фото загружено
photo_received_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оценить этого котика")],
        [KeyboardButton(text="Оценить другого котика")],
        [KeyboardButton(text="Вернуться в меню")]
    ],
    resize_keyboard=True
)

# Клавиатура после оценки
after_rating_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оценить другого котика")],
        [KeyboardButton(text="Вернуться в меню")]
    ],
    resize_keyboard=True
)

# ----------------- Обработка команды /start -----------------
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Привет! Я твой бот эксперт по пушистостям 😊\n"
        "Нажми кнопку 'оценить котика', чтобы получить экспертные коментарии о котистости котика",
        reply_markup=MAIN_MENU_KEYBOARD
    )

# ----------------- Callback обработчики -----------------

@dp.callback_query(lambda c: c.data == "check_limit")
async def check_limit_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    today = date.today()

    with SessionLocal() as db:
        user = db.query(UserLimit).filter(UserLimit.user_id == user_id).first()

        if not user:
            remaining = MAX_REQUESTS
        else:
            if user.last_reset < today:
                user.used_requests = 0
                user.last_reset = today
                db.commit()
            remaining = MAX_REQUESTS - user.used_requests

        await callback.message.answer(f"У тебя осталось {remaining} бесплатных запросов!")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "topup_limit")
async def topup_limit_handler(callback: types.CallbackQuery):
    await callback.message.answer(
        "Пополните баланс на 10 запросов\n\n"
        "Отправьте сообщение 'cat lover' чтобы сбросить лимит"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "rate_cat")
async def rate_cat_handler(callback: types.CallbackQuery):
    await callback.message.answer(
        "Загрузи фото котика для оценки! 📸\n\n"
        "После загрузки фото нажми 'Оценить этого котика'",
        reply_markup=ReplyKeyboardRemove()
    )
    await callback.answer()

# ----------------- Обработка сообщения "cat lover" -----------------
@dp.message(lambda message: message.text and message.text.lower() == "cat lover")
async def reset_limit_handler(message: Message):
    user_id = message.from_user.id
    today = date.today()

    with SessionLocal() as db:
        user = db.query(UserLimit).filter(UserLimit.user_id == user_id).first()
        
        if not user:
            user = UserLimit(user_id=user_id, last_reset=today, used_requests=0)
            db.add(user)
        else:
            user.used_requests = 0
            user.last_reset = today
        
        db.commit()

    await message.answer("✅ Лимит сброшен! У тебя снова 10 бесплатных запросов!")

# ----------------- Обработка фото -----------------
@dp.message(F.photo)
async def handle_photo_directly(message: Message):
    """Обработчик загруженного фото"""
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
    except Exception as e:
        logger.error(f"❌ Error saving photo: {e}")
        await message.answer("Ой! Не удалось сохранить фото. Попробуй еще раз! 😿")

# ----------------- Обработка кнопки "Оценить этого котика" -----------------
@dp.message(F.text == "Оценить этого котика")
async def analyze_photo_directly(message: Message):
    """Анализ сохраненного фото"""
    user_id = message.from_user.id
    today = date.today()
    
    logger.info(f"🔍 Analyze photo button pressed by user {user_id}")
    
    # Проверяем есть ли фото
    if user_id not in user_last_photos:
        await message.answer("Сначала загрузи фото котика! 📸")
        return
    
    # Проверяем лимит
    with SessionLocal() as db:
        user = db.query(UserLimit).filter(UserLimit.user_id == user_id).first()
        
        if not user:
            await message.answer("Сначала активируй лимит в главном меню!")
            return
        
        if user.last_reset < today:
            user.used_requests = 0
            user.last_reset = today
            db.commit()
        
        if user.used_requests >= MAX_REQUESTS:
            await message.answer("Бесплатные запросы закончились! Приходи завтра! 🐾")
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
            reply_markup=after_rating_keyboard
        )
        logger.info(f"✅ Photo analyzed successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error analyzing photo: {e}")
        await message.answer("Ой! Не удалось проанализировать фото. Попробуй еще раз! 😿", reply_markup=photo_received_keyboard)

# ----------------- Обработка кнопки "Оценить другого котика" -----------------
@dp.message(F.text == "Оценить другого котика")
async def rate_another_cat_handler(message: Message):
    """Начать оценку другого котика"""
    user_id = message.from_user.id
    today = date.today()
    
    logger.info(f"🔄 User {user_id} wants to rate another cat")
    
    # Проверяем лимит
    with SessionLocal() as db:
        user = db.query(UserLimit).filter(UserLimit.user_id == user_id).first()
        
        if not user:
            await message.answer("Сначала активируй лимит в главном меню!", reply_markup=ReplyKeyboardRemove())
            await message.answer("Выбери действие:", reply_markup=MAIN_MENU_KEYBOARD)
            return
        
        if user.last_reset < today:
            user.used_requests = 0
            user.last_reset = today
            db.commit()
        
        if user.used_requests >= MAX_REQUESTS:
            await message.answer("Бесплатные запросы закончились! Приходи завтра! 🐾", reply_markup=ReplyKeyboardRemove())
            await message.answer("Выбери действие:", reply_markup=MAIN_MENU_KEYBOARD)
            return
    
    # Очищаем старое фото если есть
    if user_id in user_last_photos:
        del user_last_photos[user_id]
    
    await message.answer(
        "Загрузи фото следующего котика для оценки! 📸\n\n"
        "После загрузки фото нажми 'Оценить этого котика'",
        reply_markup=ReplyKeyboardRemove()
    )

# ----------------- Обработка кнопки "Вернуться в меню" -----------------
@dp.message(F.text == "Вернуться в меню")
async def back_to_menu_directly(message: Message):
    """Возврат в главное меню"""
    user_id = message.from_user.id
    if user_id in user_last_photos:
        del user_last_photos[user_id]
    
    await message.answer("Возвращаемся в меню! 🏠", reply_markup=ReplyKeyboardRemove())
    await message.answer("Выбери действие:", reply_markup=MAIN_MENU_KEYBOARD)

# ----------------- Обработка обычного текста -----------------
@dp.message()
async def handle_user_request(message: Message):
    """Обработка случайного текста - не списываем запросы"""
    if message.text and not message.text.startswith('/'):
        responses = [
            "Я специализируюсь на качественной оценке котиков",
            "Предлагаю перейти к пушишам", 
            "Могу дать комментарии по мяучке",
            "Ожидаю загрузки котейшества",
            "Котикам время а перепискам час"
        ]
        response = random.choice(responses)
        await message.answer(response)

# ----------------- Диагностический обработчик -----------------
@dp.callback_query()
async def debug_callback_handler(callback: types.CallbackQuery):
    """Диагностический обработчик всех callback"""
    print(f"DEBUG: Callback received: {callback.data}")
    await callback.answer(f"Callback: {callback.data}")