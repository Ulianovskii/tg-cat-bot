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