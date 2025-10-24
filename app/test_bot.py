cat > test_bot.py << 'EOF'
#!/usr/bin/env python3
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

print("=== ТЕСТ БОТА ===")
print(f"BOT_TOKEN: {bool(os.getenv('BOT_TOKEN'))}")
print(f"HUGGINGFACE_API_KEY: {bool(os.getenv('HUGGINGFACE_API_KEY'))}")

# Проверим импорты
try:
    from app.bot_instance import bot, dp
    print("✅ Bot instance загружен")
    
    from app.services.cat_analyzer import cat_analyzer
    print("✅ CatAnalyzer загружен")
    
    from app.handlers.cat_rating import cat_router
    print("✅ Cat router загружен")
    
    print("=== ВСЕ ИМПОРТЫ РАБОТАЮТ ===")
    
except Exception as e:
    print(f"❌ Ошибка импорта: {e}")
EOF