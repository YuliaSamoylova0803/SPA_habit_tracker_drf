from celery import shared_task
from django.utils import timezone
from tracking_habits.models import Habit
from .services import send_telegram_message
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def send_habit_reminder(self, habit_id):
    """
    Задача для отправки напоминания о конкретной привычке
    с автоматическими повторами при ошибках.
    """
    try:
        habit = Habit.objects.get(id=habit_id)
        if not habit.user.tg_chat_id:
            logger.warning(f"У пользователя {habit.user} не указан chat_id")
            return False

        message = (
            f"⏰ <b>Напоминание о привычке!</b>\n\n"
            f"<b>Действие:</b> {habit.action}\n"
            f"<b>Место:</b> {habit.place}\n"
            f"<b>Время выполнения:</b> {habit.duration} сек.\n"
            f"<b>Периодичность:</b> {habit.get_periodicity_display()}"
        )

        if send_telegram_message(habit.user.tg_chat_id, message):
            logger.info(f"Напоминание для привычки {habit_id} отправлено")
            return True
        else:
            # Повторная попытка через 1 минуту
            raise self.retry(countdown=60)

    except Habit.DoesNotExist as e:
        logger.error(f"Привычка {habit_id} не найдена: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task
def check_due_habits():
    """Проверка привычек, для которых нужно отправить напоминание.
    Запускается по расписанию каждую минуту.
    """
    now = timezone.now()
    current_time = now.time()

    habits = Habit.objects.filter(
        time__hour=current_time.hour, time__minute=current_time.minute
    ).select_related("user")

    logger.info(f"Найдено {habits.count()} привычек для напоминания")

    for habit in habits:
        send_habit_reminder.delay(habit.id)

    return f"Проверка завершена. Обработано {habits.count()} привычек"
