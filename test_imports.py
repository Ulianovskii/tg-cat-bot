# test_imports.py
print("=== ТЕСТ ИМПОРТОВ ===")

try:
    from app.bot_instance import dp, bot
    print("✅ Bot instance imported")
    
    # Проверим текущие обработчики
    print(f"Обработчиков в dp до: {len(dp.message.handlers)}")
    
    # Импортируем basic
    import app.handlers.basic
    print("✅ Basic handlers imported")
    print(f"Обработчиков в dp после basic: {len(dp.message.handlers)}")
    
    # Импортируем cat_rating
    from app.handlers.cat_rating import cat_router
    print("✅ Cat router imported")
    
    # Проверим обработчики в роутере
    print(f"Обработчиков в cat_router: {len(cat_router.message.handlers)}")
    
    # Зарегистрируем роутер
    dp.include_router(cat_router)
    print("✅ Router registered")
    print(f"Обработчиков в dp после router: {len(dp.message.handlers)}")
    
    # Выведем все обработчики
    print("\n=== ВСЕ ОБРАБОТЧИКИ ===")
    for i, handler in enumerate(dp.message.handlers):
        print(f"{i+1}. {handler}")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()