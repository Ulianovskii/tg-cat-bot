import logging
import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.models import PromoCode
from app.config import RequestConfig

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