# app/handlers/basic.py #####
from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import logging
import random

from app.db.database import get_user, use_free_request, use_paid_request
from app.services.openai_analyzer import analyze_cat_image

router = Router()  # ← ИСПОЛЬЗУЕМ ROUTER вместо dp

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
@router.message(CommandStart())  # ← router вместо dp
async def start_handler(message: Message):
    await message.answer(
        "Привет! Я твой бот эксперт по пушистостям 😊\n"
        "Нажми кнопку 'оценить котика', чтобы получить экспертные коментарии о котистости котика",
        reply_markup=MAIN_MENU_KEYBOARD
    )

# ----------------- Callback обработчики -----------------

@router.callback_query(lambda c: c.data == "check_limit")
async def check_limit_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    
    await callback.message.answer(
        f"📊 Ваш баланс:\n\n"
        f"🆓 Бесплатных запросов: {user.free_requests}/5\n"  # ← ДОБАВЬТЕ /5
        f"⭐ Оплаченных запросов: {user.paid_requests}\n\n"
        f"💫 Бесплатные запросы обновляются каждый день!"
    )
    await callback.answer()
    
@router.callback_query(lambda c: c.data == "topup_limit")
async def topup_limit_handler(callback: types.CallbackQuery):
    """Показ меню пополнения через Stars"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="15 ⭐ - 3 запроса", callback_data="buy_15"),
                InlineKeyboardButton(text="45 ⭐ - 10 запросов", callback_data="buy_45"),
            ],
            [
                InlineKeyboardButton(text="80 ⭐ - 20 запросов", callback_data="buy_80"),
            ]
        ]
    )
    
    await callback.message.answer(
        "🎯 Выберите пакет запросов:\n\n"
        "💫 15 ⭐ = 3 запроса\n"
        "✨ 45 ⭐ = 10 запросов\n" 
        "🌟 80 ⭐ = 20 запросов\n\n"
        "⭐ Stars покупаются прямо в Telegram",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "rate_cat")  # ← router вместо dp
async def rate_cat_handler(callback: types.CallbackQuery):
    await callback.message.answer(
        "Загрузи фото котика для оценки! 📸\n\n"
        "После загрузки фото нажми 'Оценить этого котика'",
        reply_markup=ReplyKeyboardRemove()
    )
    await callback.answer()

# ----------------- Обработка фото -----------------
@router.message(F.photo)  # ← router вместо dp
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
@router.message(F.text == "Оценить этого котика")  # ← router вместо dp
async def analyze_photo_directly(message: Message):
    """Анализ сохраненного фото"""
    user_id = message.from_user.id
    
    logger.info(f"🔍 Analyze photo button pressed by user {user_id}")
    
    # Проверяем есть ли фото
    if user_id not in user_last_photos:
        await message.answer("Сначала загрузи фото котика! 📸")
        return
    
    # Проверяем баланс через новую систему
    user = get_user(user_id)
    
    if user.free_requests <= 0 and user.paid_requests <= 0:
        await message.answer(
            "❌ У вас закончились запросы!\n\n"
            "💫 Бесплатные запросы обновятся завтра\n"
            "⭐ Или пополните баланс через меню"
        )
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
        analysis_result = await analyze_cat_image(photo_bytes.getvalue())
        
        # Списываем запрос (сначала бесплатные, потом платные)
        if user.free_requests > 0:
            use_free_request(user_id)
            request_type = "бесплатный"
        else:
            use_paid_request(user_id) 
            request_type = "оплаченный"
        
        # Получаем обновленный баланс
        user = get_user(user_id)
        
        # Удаляем фото
        del user_last_photos[user_id]
        
        await processing_msg.delete()
        await message.answer(
            f"{analysis_result}\n\n"
            f"📊 Использован {request_type} запрос\n"
            f"🆓 Осталось бесплатных: {user.free_requests}\n"
            f"⭐ Осталось оплаченных: {user.paid_requests}",
            reply_markup=after_rating_keyboard
        )
        logger.info(f"✅ Photo analyzed successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error analyzing photo: {e}")
        await message.answer("Ой! Не удалось проанализировать фото. Попробуй еще раз! 😿", reply_markup=photo_received_keyboard)

# ----------------- Обработка кнопки "Оценить другого котика" -----------------
@router.message(F.text == "Оценить другого котика")  # ← router вместо dp
async def rate_another_cat_handler(message: Message):
    """Начать оценку другого котика"""
    user_id = message.from_user.id
    
    logger.info(f"🔄 User {user_id} wants to rate another cat")
    
    # Проверяем баланс через новую систему
    user = get_user(user_id)
    
    if user.free_requests <= 0 and user.paid_requests <= 0:
        await message.answer(
            "❌ У вас закончились запросы!\n\n"
            "💫 Бесплатные запросы обновятся завтра\n"
            "⭐ Или пополните баланс через меню",
            reply_markup=ReplyKeyboardRemove()
        )
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
@router.message(F.text == "Вернуться в меню")  # ← router вместо dp
async def back_to_menu_directly(message: Message):
    """Возврат в главное меню"""
    user_id = message.from_user.id
    if user_id in user_last_photos:
        del user_last_photos[user_id]
    
    await message.answer("Возвращаемся в меню! 🏠", reply_markup=ReplyKeyboardRemove())
    await message.answer("Выбери действие:", reply_markup=MAIN_MENU_KEYBOARD)

# ----------------- Обработка обычного текста -----------------
@router.message()  # ← router вместо dp
async def handle_user_request(message: Message):
    """Обработка случайного текста - не списываем запросы"""
    if message.text and not message.text.startswith('/'):
        responses = [
            "Я специализируюсь на качественной оценке котиков. Пришлите фото котика для анализа",
            "Предлагаю перейти к пушишам. Пришлите фото котика для анализа", 
            "Могу дать комментарии по мяучке. Пришлите фото котика для анализа",
            "Ожидаю загрузки котейшества. Пришлите фото котика для анализа",
            "Котикам время а перепискам час. Пришлите фото котика для анализа"
        ]
        response = random.choice(responses)
        await message.answer(response)