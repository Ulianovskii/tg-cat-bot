# app/db/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from app.db.database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(String, unique=True, index=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # ⬇️⬇️⬇️ ДОБАВЬТЕ ЭТИ 3 СТРОЧКИ ⬇️⬇️⬇️
    free_requests = Column(Integer, default=10)
    paid_requests = Column(Integer, default=0)
    last_reset = Column(Date, default=datetime.date.today)
    # ⬆️⬆️⬆️ КОНЕЦ ДОБАВЛЕНИЯ ⬆️⬆️⬆️
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