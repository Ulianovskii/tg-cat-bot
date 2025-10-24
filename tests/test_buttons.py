# tests/test_buttons.py
from app.bot_instance import bot
from app.handlers.basic import MAIN_MENU_KEYBOARD
import asyncio

async def test_buttons():
    print("=== ТЕСТ КНОПОК ===")
    print("MAIN_MENU_KEYBOARD:")
    for row in MAIN_MENU_KEYBOARD.inline_keyboard:
        for button in row:
            print(f" - '{button.text}' -> {button.callback_data}")
    
    # Проверим обработчики
    from app.bot_instance import dp
    print(f"\nОбработчиков callback_query: {len(dp.callback_query.handlers)}")
    for handler in dp.callback_query.handlers:
        print(f" - {handler}")

if __name__ == "__main__":
    asyncio.run(test_buttons())
    