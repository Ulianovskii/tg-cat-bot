#!/bin/bash
echo "=== ЗАПУСК СКРИПТА ==="
echo "🛑 Останавливаю бота..."

# Проверяем есть ли процесс
if pgrep -f "python.*app.main" > /dev/null; then
    echo "📋 Найден работающий бот, останавливаю..."
    pkill -f "python.*app.main"
    sleep 2
else
    echo "ℹ️  Бот не запущен"
fi

echo "🔍 Проверяем виртуальное окружение..."
if [ -d "venv" ]; then
    echo "✅ venv найден"
else
    echo "❌ venv не найден"
    exit 1
fi

echo "🚀 Запускаю бота..."
source venv/bin/activate
echo "📝 Python путь: $(which python)"
echo "📝 Python версия: $(python --version)"
python -m app.main

echo "=== СКРИПТ ЗАВЕРШЕН ==="