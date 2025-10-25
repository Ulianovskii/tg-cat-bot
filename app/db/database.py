# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

# sqlite: special arg
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_user(user_id: int):
    """Получить пользователя по ID"""
    from app.db.models import User
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            # Создаем нового пользователя если не существует
            user = User(id=user_id, free_requests=10, paid_requests=0)
            db.add(user)
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