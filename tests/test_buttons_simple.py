# test_buttons_simple.py (в папке tg_bot_0_1)
import sys
import os

# Добавляем текущую папку в путь
sys.path.append(os.getcwd())

from app.handlers.basic import MAIN_MENU_KEYBOARD

print("=== ТЕСТ КНОПОК ===")
print("MAIN_MENU_KEYBOARD:")
for row in MAIN_MENU_KEYBOARD.inline_keyboard:
    for button in row:
        print(f" - '{button.text}' -> {button.callback_data}")