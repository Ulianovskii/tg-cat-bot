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