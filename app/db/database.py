# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL
import datetime

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ⬇️ ФУНКЦИИ БАЗЫ ДАННЫХ
def get_user(user_id: int):
    """Получить пользователя по ID"""
    from app.db.models import User
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(
                id=user_id, 
                tg_id=str(user_id),
                free_requests=10, 
                paid_requests=0,
                last_reset=datetime.date.today()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            if user.last_reset < datetime.date.today():
                user.free_requests = 10
                user.last_reset = datetime.date.today()
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