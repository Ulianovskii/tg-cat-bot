from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL, RequestConfig
import datetime
import json

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_user(user_id: int):
    """Получить пользователя по ID с автоматическим сбросом"""
    from app.db.models import User
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        today = datetime.date.today()
        
        if not user:
            # Создаем нового пользователя
            free_requests = RequestConfig.FREE_REQUESTS_DAILY if RequestConfig.RESET_TYPE == "daily" else RequestConfig.FREE_REQUESTS_WEEKLY
            user = User(
                id=user_id, 
                tg_id=str(user_id),
                free_requests=free_requests,
                paid_requests=0,
                last_reset=today,
                used_promo_codes=json.dumps([])
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Проверяем нужно ли сбросить бесплатные запросы
            needs_reset = False
            if RequestConfig.RESET_TYPE == "daily":
                needs_reset = user.last_reset < today
            else:  # weekly
                days_since_reset = (today - user.last_reset).days
                needs_reset = days_since_reset >= 7
            
            if needs_reset:
                free_requests = RequestConfig.FREE_REQUESTS_DAILY if RequestConfig.RESET_TYPE == "daily" else RequestConfig.FREE_REQUESTS_WEEKLY
                user.free_requests = free_requests
                user.last_reset = today
                user.reset_counter += 1
                db.commit()
                db.refresh(user)
        
        return user
    finally:
        db.close()

def update_user_balance(user_id: int, new_paid_balance: int):
    """Обновить баланс оплаченных запросов"""
    from app.db.models import User
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.paid_requests = new_paid_balance
            db.commit()
    finally:
        db.close()

def add_paid_requests(user_id: int, requests_to_add: int):
    """Добавить оплаченные запросы"""
    from app.db.models import User
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.paid_requests += requests_to_add
            db.commit()
            return user.paid_requests
        return 0
    finally:
        db.close()

def use_free_request(user_id: int):
    """Использовать один бесплатный запрос"""
    from app.db.models import User
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.free_requests > 0:
            user.free_requests -= 1
            user.total_requests_used += 1
            db.commit()
            return True
        return False
    finally:
        db.close()

def use_paid_request(user_id: int):
    """Использовать один оплаченный запрос"""
    from app.db.models import User
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.paid_requests > 0:
            user.paid_requests -= 1
            user.total_requests_used += 1
            db.commit()
            return True
        return False
    finally:
        db.close()