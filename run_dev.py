#!/usr/bin/env python3
# run_dev.py - для разработки с авто-перезапуском
import subprocess
import sys
from watchfiles import run_process

def main():
    """Запускает бота с авто-перезапуском при изменениях файлов"""
    print("🚀 Запуск бота в режиме разработки...")
    print("📁 Отслеживаются изменения в файлах .py")
    print("⏹️  Остановка: Ctrl+C")
    
    run_process(
        './app',  # папка для отслеживания изменений
        target=run_bot,
        args=(),
        callback=on_change
    )

def run_bot():
    """Функция запуска бота"""
    try:
        subprocess.run([
            sys.executable, "-m", "app.main"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при запуске: {e}")
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
        sys.exit(0)

def on_change(changes):
    """Вызывается при изменении файлов"""
    print(f"🔄 Обнаружены изменения: {len(changes)} файлов. Перезапуск...")

if __name__ == "__main__":
    main()