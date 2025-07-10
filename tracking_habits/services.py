import requests
from celery.utils.log import get_task_logger

from config import settings

logger = get_task_logger(__name__)


def send_telegram_message(chat_id, message):
    """
    Отправка сообщения в Telegram с обработкой ошибок.

    Args:
        chat_id (str): ID чата пользователя в Telegram
        message (str): Текст сообщения (поддерживает HTML-разметку)

    Returns:
        bool: True если сообщение отправлено успешно, False в случае ошибки
    """
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        response = requests.post(url, json=params, timeout=10)
        response.raise_for_status()
        logger.info(f"Сообщение отправлено в чат {chat_id}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка отправки в Telegram (chat_id: {chat_id}): {str(e)}")
        return False
