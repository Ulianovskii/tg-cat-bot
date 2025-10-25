source venv/bin/activate
# Заходим в Python
python
# Импортируем функцию
from app.handlers.basic import reset_user_limit
# Сбрасываем лимит для себя
reset_user_limit(103181087)


source venv/bin/activate && python -m app.main

Установите watchfiles для автоматического перезапуска:

bash restart_bot.sh


# 1. Проверить что изменилось
git status

# 2. Добавить изменения
git add .                          # все файлы
git add app/main.py               # конкретный файл

# 3. Закоммитить с понятным сообщением
git commit -m "feat: улучшено определение котиков"

# 4. Запушить в свою ветку
git push origin feature/cat-detection


# 1. Проверить статус
git status

# 2. Если файл есть в "Untracked files" - добавить его
git add app/handlers/payment_handler.py

# 3. Проверить что файл добавлен в staged changes
git status

# 4. Закоммитить
git commit -m "add: payment handler for Telegram Stars"

# 5. Запушить
git push origin main