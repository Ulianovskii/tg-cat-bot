# app/handlers/payment_handler.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice, SuccessfulPayment
from aiogram.filters import Command
import logging
import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.database import get_user, update_user_balance, add_paid_requests
from app.config import RequestConfig, get_pricing_display, get_free_requests_info
from app.services.promo_service import PromoService
from app.db.models import PromoCode
import logging

payment_router = Router()
logger = logging.getLogger(__name__)

class PromoService:
    
    @staticmethod
    def generate_promo_code(length: int = None) -> str:
        """Генерация промокода"""
        if length is None:
            length = RequestConfig.PROMO_CODE_LENGTH
        
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    @staticmethod
    def create_promo_code(db: Session, requests: int, created_by: int, days_valid: int = None):
        """Создание нового промокода"""
        if days_valid is None:
            days_valid = RequestConfig.PROMO_CODE_DURATION_DAYS
        
        code = PromoService.generate_promo_code()
        expires_at = datetime.now() + timedelta(days=days_valid)
        
        promo = PromoCode(
            code=code,
            requests=requests,
            created_by=created_by,
            expires_at=expires_at
        )
        
        db.add(promo)
        db.commit()
        db.refresh(promo)
        
        logger.info(f"Created promo code: {code} for {requests} requests")
        return promo
    
    @staticmethod
    def use_promo_code(db: Session, code: str, user_id: int):
        """Использование промокода"""
        promo = db.query(PromoCode).filter(
            PromoCode.code == code,
            PromoCode.is_active == True
        ).first()
        
        if not promo:
            return False, "Промокод не найден"
        
        if promo.used_by is not None:
            return False, "Промокод уже использован"
        
        if promo.expires_at < datetime.now():
            return False, "Промокод истек"
        
        # Помечаем как использованный
        promo.used_by = user_id
        promo.used_at = datetime.now()
        promo.is_active = False
        
        db.commit()
        
        logger.info(f"User {user_id} used promo code: {code}")
        return True, promo.requests
    
    @staticmethod
    def get_active_promos(db: Session):
        """Получить активные промокоды"""
        return db.query(PromoCode).filter(
            PromoCode.is_active == True,
            PromoCode.used_by.is_(None),
            PromoCode.expires_at > datetime.now()
        ).all()


@payment_router.message(Command("replenish"))
async def replenish_balance(message: Message):
    """Показ меню пополнения через Stars"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    # Динамически создаем кнопки из конфига
    keyboard = []
    row = []
    
    for i, (stars, requests) in enumerate(RequestConfig.PRICING.items()):
        button = InlineKeyboardButton(
            text=f"{stars} ⭐ - {requests} запросов", 
            callback_data=f"buy_{stars}"
        )
        row.append(button)
        
        if len(row) == 2 or i == len(RequestConfig.PRICING.items()) - 1:
            keyboard.append(row)
            row = []
    
    # Добавляем кнопку промокода
    keyboard.append([InlineKeyboardButton(text="🎁 Ввести промокод", callback_data="enter_promo")])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(
        f"💫 **Доступные тарифы:**\n{get_pricing_display()}\n\n"
        f"{get_free_requests_info()}\n"
        f"{get_promo_info()}\n\n"
        f"Выберите вариант пополнения:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

@payment_router.callback_query(F.data == "enter_promo")
async def enter_promo_handler(callback: CallbackQuery):
    """Обработчик ввода промокода"""
    await callback.message.answer(
        "🎁 **Введите промокод:**\n\n"
        "Отправьте мне промокод, чтобы получить бонусные запросы!"
    )
    await callback.answer()

@payment_router.message(F.text & ~F.text.startswith('/'))
async def handle_promo_code(message: Message):
    """Обработка введенного промокода"""
    from app.db.database import SessionLocal
    
    promo_code = message.text.strip().upper()
    
    # Проверяем длину промокода
    if len(promo_code) != RequestConfig.PROMO_CODE_LENGTH:
        return  # Не промокод
    
    db = SessionLocal()
    try:
        success, result = PromoService.use_promo_code(db, promo_code, message.from_user.id)
        
        if success:
            requests_added = result
            new_balance = add_paid_requests(message.from_user.id, requests_added)
            
            await message.answer(
                f"🎉 **Промокод активирован!**\n\n"
                f"✅ Получено: {requests_added} запросов\n"
                f"💰 Теперь у вас: {new_balance} оплаченных запросов\n\n"
                f"Спасибо за использование промокода! 🎁"
            )
        else:
            await message.answer(f"❌ {result}")
            
    except Exception as e:
        logger.error(f"Error processing promo code: {e}")
        await message.answer("❌ Ошибка при обработке промокода")
    finally:
        db.close()

@payment_router.callback_query(F.data.startswith("buy_"))
async def handle_buy_callback(callback: CallbackQuery):
    """Создание инвойса с Stars"""
    try:
        stars_count = int(callback.data.replace("buy_", ""))
        
        # Проверяем что тариф существует в конфиге
        if stars_count not in RequestConfig.PRICING:
            await callback.answer("❌ Тариф не найден", show_alert=True)
            return
        
        requests_count = RequestConfig.PRICING[stars_count]
        
        await callback.bot.send_invoice(
            chat_id=callback.message.chat.id,
            title=f"Пакет {requests_count} запросов",
            description=f"{requests_count} AI анализов фотографий котиков",
            payload=f"stars_{stars_count}_{callback.from_user.id}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Stars", amount=stars_count)],
            start_parameter="cat_ai_analyzer",
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        await callback.answer("❌ Ошибка при создании платежа", show_alert=True)

@payment_router.pre_checkout_query()
async def precheckout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@payment_router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    """Обработка успешного платежа через Stars"""
    try:
        payment = message.successful_payment
        payload = payment.invoice_payload
        user_id = message.from_user.id
        
        logger.info(f"Processing payment: {payload} for user {user_id}")
        
        parts = payload.split('_')
        if len(parts) >= 3:
            stars_count = int(parts[1])
            
            # Получаем количество запросов из конфига
            requests_granted = RequestConfig.PRICING.get(stars_count, stars_count // 5)
            
            user = get_user(user_id)
            logger.info(f"User found: ID={user.id}, Paid={user.paid_requests}")
            
            new_balance = add_paid_requests(user_id, requests_granted)
            
            await message.answer(
                f"✅ **Спасибо за покупку!**\n\n"
                f"🎁 Получено: {requests_granted} запросов\n"
                f"💫 Использовано: {stars_count} Stars\n"
                f"💰 Баланс: {new_balance} оплаченных запросов\n\n"
                f"Отправьте фото котика для анализа! 🐱"
            )
            
            logger.info(f"Added {requests_granted} requests to user {user_id}")
                
        else:
            await message.answer("❌ Ошибка обработки платежа")
            
    except Exception as e:
        logger.error(f"❌ Error processing payment: {e}")
        await message.answer("❌ Произошла ошибка при обработке платежа")

@payment_router.message(Command("balance"))
async def check_balance(message: Message):
    """Проверить текущий баланс запросов"""
    user = get_user(message.from_user.id)
    
    reset_info = "ежедневно" if RequestConfig.RESET_TYPE == "daily" else "еженедельно"
    max_free = RequestConfig.FREE_REQUESTS_DAILY if RequestConfig.RESET_TYPE == "daily" else RequestConfig.FREE_REQUESTS_WEEKLY
    
    await message.answer(
        f"💰 **Ваш баланс запросов:**\n\n"
        f"• 🆓 Бесплатных: {user.free_requests}/{max_free} (сброс {reset_info})\n"
        f"• 💰 Оплаченных: {user.paid_requests}\n"
        f"• 📊 Всего использовано: {user.total_requests_used}\n"
        f"• 📅 Последний сброс: {user.last_reset}",
        parse_mode="Markdown"
    )