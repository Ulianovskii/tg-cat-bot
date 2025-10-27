from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject
from app.config import RequestConfig, ADMIN_ID
from app.services.promo_service import PromoService
from app.db.database import SessionLocal, add_paid_requests
from app.db.models import PromoCode
from datetime import datetime, timedelta
import logging

admin_router = Router()
logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    """Проверка является ли пользователь админом"""
    return user_id == ADMIN_ID

@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    """Админ панель"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещен")
        return
    
    await message.answer(
        "⚙️ **Админ панель**\n\n"
        "Доступные команды:\n"
        "/stats - Статистика\n"
        "/create_promo <запросы> - Создать промокод\n"
        "/list_promos - Список промокодов\n"
        "/add_requests <user_id> <кол-во> - Добавить запросы\n"
        "/service_code - Получить сервисный код",
        parse_mode="Markdown"
    )

@admin_router.message(Command("service_code"))
async def service_code(message: Message):
    """Генерация сервисного кода для админа"""
    if not is_admin(message.from_user.id):
        return
    
    # Добавляем запросы админу
    new_balance = add_paid_requests(message.from_user.id, RequestConfig.SERVICE_CODE_REQUESTS)
    
    await message.answer(
        f"🎯 **Сервисный код активирован!**\n\n"
        f"✅ Добавлено: {RequestConfig.SERVICE_CODE_REQUESTS} запросов\n"
        f"💰 Ваш баланс: {new_balance} оплаченных запросов"
    )

@admin_router.message(Command("create_promo"))
async def create_promo(message: Message, command: CommandObject):
    """Создание промокода"""
    if not is_admin(message.from_user.id):
        return
    
    # Если не указано количество - используем значение по умолчанию из конфига
    if not command.args:
        requests = RequestConfig.PROMO_CODE_REQUESTS
    else:
        try:
            requests = int(command.args)
        except ValueError:
            await message.answer("❌ Используйте: /create_promo <количество_запросов> или без аргументов для значения по умолчанию")
            return
    
    db = SessionLocal()
    
    try:
        promo = PromoService.create_promo_code(db, requests, message.from_user.id)
        
        expires_str = promo.expires_at.strftime("%d.%m.%Y %H:%M")
        
        await message.answer(
            f"🎫 **Промокод создан!**\n\n"
            f"📝 Код: `{promo.code}`\n"
            f"🎁 Запросов: {promo.requests}\n"
            f"⏰ Действует до: {expires_str}\n\n"
            f"Пользователь получит {promo.requests} запросов при активации.",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error creating promo: {e}")
        await message.answer("❌ Ошибка при создании промокода")
    finally:
        db.close()

@admin_router.message(Command("add_requests"))
async def add_requests_admin(message: Message, command: CommandObject):
    """Добавление запросов пользователю"""
    if not is_admin(message.from_user.id):
        return
    
    if not command.args:
        await message.answer("❌ Используйте: /add_requests <user_id> <количество>")
        return
    
    try:
        args = command.args.split()
        if len(args) != 2:
            await message.answer("❌ Используйте: /add_requests <user_id> <количество>")
            return
        
        user_id = int(args[0])
        requests = int(args[1])
        
        new_balance = add_paid_requests(user_id, requests)
        
        await message.answer(
            f"✅ **Запросы добавлены!**\n\n"
            f"👤 Пользователь: {user_id}\n"
            f"🎁 Добавлено: {requests} запросов\n"
            f"💰 Новый баланс: {new_balance}"
        )
        
    except Exception as e:
        logger.error(f"Error adding requests: {e}")
        await message.answer("❌ Ошибка при добавлении запросов")

@admin_router.message(Command("stats"))
async def show_stats(message: Message):
    """Показать статистику"""
    if not is_admin(message.from_user.id):
        return
    
    from app.db.database import SessionLocal
    from app.db.models import User, PromoCode
    from sqlalchemy import func
    
    db = SessionLocal()
    try:
        # Статистика пользователей
        total_users = db.query(User).count()
        active_today = db.query(User).filter(
            User.last_reset == datetime.now().date()
        ).count()
        
        # Статистика промокодов
        total_promos = db.query(PromoCode).count()
        used_promos = db.query(PromoCode).filter(PromoCode.used_by.isnot(None)).count()
        active_promos = db.query(PromoCode).filter(
            PromoCode.is_active == True,
            PromoCode.used_by.is_(None)
        ).count()
        
        await message.answer(
            f"📊 **Статистика системы:**\n\n"
            f"👥 **Пользователи:**\n"
            f"• Всего: {total_users}\n"
            f"• Активных сегодня: {active_today}\n\n"
            f"🎫 **Промокоды:**\n"
            f"• Всего: {total_promos}\n"
            f"• Использовано: {used_promos}\n"
            f"• Активных: {active_promos}\n\n"
            f"⚙️ **Настройки:**\n"
            f"• Бесплатных запросов: {RequestConfig.FREE_REQUESTS_DAILY if RequestConfig.RESET_TYPE == 'daily' else RequestConfig.FREE_REQUESTS_WEEKLY} ({RequestConfig.RESET_TYPE})\n"
            f"• Тарифов: {len(RequestConfig.PRICING)}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        await message.answer("❌ Ошибка при получении статистики")
    finally:
        db.close()