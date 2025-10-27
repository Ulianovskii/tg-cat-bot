# app/db/simple_migrate.py
import logging
from sqlalchemy import text
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)

def simple_migrate():
    """Простая миграция - добавляет недостающие колонки"""
    session = SessionLocal()
    
    try:
        # Проверяем существующие колонки
        result = session.execute(text("PRAGMA table_info(users)"))
        existing_columns = [row[1] for row in result]
        
        print("🔍 Existing columns:", existing_columns)
        
        # Добавляем отсутствующие колонки
        if 'total_requests_used' not in existing_columns:
            session.execute(text('ALTER TABLE users ADD COLUMN total_requests_used INTEGER DEFAULT 0'))
            print("✅ Added total_requests_used column")
        
        if 'reset_counter' not in existing_columns:
            session.execute(text('ALTER TABLE users ADD COLUMN reset_counter INTEGER DEFAULT 0'))
            print("✅ Added reset_counter column")
            
        if 'reset_type' not in existing_columns:
            session.execute(text('ALTER TABLE users ADD COLUMN reset_type TEXT DEFAULT "daily"'))
            print("✅ Added reset_type column")
            
        if 'used_promo_codes' not in existing_columns:
            session.execute(text('ALTER TABLE users ADD COLUMN used_promo_codes TEXT DEFAULT "[]"'))
            print("✅ Added used_promo_codes column")
        
        session.commit()
        print("✅ Simple migration completed")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()

# Добавляем эту строку для прямого запуска
if __name__ == "__main__":
    simple_migrate()