from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, JSON
from app.db.database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(String, unique=True, index=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Запросы
    free_requests = Column(Integer, default=0)
    paid_requests = Column(Integer, default=0)
    total_requests_used = Column(Integer, default=0)
    
    # Сбросы
    last_reset = Column(Date, default=datetime.date.today)
    reset_counter = Column(Integer, default=0)  # Счетчик сбросов
    
    # Промокоды
    used_promo_codes = Column(JSON, default=[])  # Список использованных промокодов

class PromoCode(Base):
    __tablename__ = "promo_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    requests = Column(Integer, default=0)  # Количество запросов
    created_by = Column(Integer)  # ID админа, создавшего промокод
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime)
    used_by = Column(Integer, nullable=True)  # Кто использовал
    used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

class Watch(Base):
    __tablename__ = "watches"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    origin = Column(String)
    destination = Column(String)
    price_limit = Column(Integer)
    active = Column(Boolean, default=True)

class UserLimit(Base):
    __tablename__ = "user_limits"
    user_id = Column(Integer, primary_key=True)
    last_reset = Column(Date, nullable=False)
    used_requests = Column(Integer, default=0)