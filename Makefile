.PHONY: run stop restart debug logs

# Запуск бота
run:
	source venv/bin/activate && python -m app.main

# Запуск с авто-перезагрузкой при изменениях кода
dev:
	source venv/bin/activate && watchmedo auto-restart --pattern="*.py" --recursive -- python -m app.main

# Остановка бота
stop:
	pkill -f "python.*app.main" || true

# Перезапуск бота
restart: stop
	sleep 2
	source venv/bin/activate && python -m app.main

# Просмотр логов
logs:
	tail -f bot.log 2>/dev/null || echo "Лог-файл не найден"

# Установка зависимостей
install:
	python -m pip install -r requirements.txt

# Активация venv
venv:
	source venv/bin/activate && bash