from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from config import settings


class Habit(models.Model):
    """
     Модель для отслеживания привычек по методологии "Атомные привычки".

    Описывает привычку в формате: "Я буду [ДЕЙСТВИЕ] в [ВРЕМЯ] в [МЕСТЕ]".
    Включает систему вознаграждений и связей между привычками.

    Attributes:
        user (User): Создатель привычки
        place (str): Место выполнения привычки
        time (Time): Время выполнения
        action (str): Конкретное действие
        is_pleasant (bool): Признак приятной привычки (награды)
        linked_habit (Habit): Связанная полезная привычка (только для приятных)
        periodicity (int): Периодичность выполнения в днях (1-7)
        reward (str): Вознаграждение за выполнение
        duration (int): Время на выполнение в секундах (1-120)
        is_public (bool): Доступна ли привычка другим пользователям
        created_at (DateTime): Дата создания
        last_completed (Date): Дата последнего выполнения
    """

    DAILY = 1
    WEEKLY = 7
    MONTHLY = 30

    PERIOD_CHOICES = [
        (DAILY, "Ежедневно"),
        (WEEKLY, "Еженедельно"),
        (MONTHLY, "Ежемесячно"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Пользователь, создавший привычку",
        related_name="habits",
        verbose_name="Пользователь"
    )
    place = models.CharField(
        max_length=50,
        verbose_name="Место выполнения",
        help_text="Место, где будет выполняться привычка"
    )
    time = models.TimeField(verbose_name="Время выполнения", help_text="В какое время выполнять привычку")
    action = models.CharField(
        max_length=100,
        verbose_name="Действие",
        help_text="Конкретное действие, которое нужно выполнить"
    )
    is_pleasant = models.BooleanField(default=False, verbose_name="Приятная привычка", help_text="Является ли привычка приятной (наградой)")
    linked_habit = models.ForeignKey(
        "self",  # Ссылка на эту же модель Habit
        on_delete=models.SET_NULL,  # При удалении связанной привычки ставит NULL
        null=True,  # Поле может быть пустым (необязательное)
        blank=True,  # Разрешает пустое значение в админке/формах
        verbose_name="Связанная привычка",  # Человекочитаемое название
        help_text="Приятная привычка, которая будет наградой",
        related_name="main_habit"  # Имя обратной связи
    )
    periodicity = models.PositiveSmallIntegerField(
        choices=PERIOD_CHOICES,
        default=DAILY,
        verbose_name="Периодичность",
        help_text="Как часто выполнять привычку (в днях)",
        validators=[
            MinValueValidator(1, message="Минимум 1 день"),
            MaxValueValidator(30, message="Максимум 30 дней")
        ]
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Вознаграждение",
        help_text="Чем себя наградить после выполнения (например, 'кофе', '5 минут соцсетей')"
    )
    duration = models.PositiveIntegerField(
        verbose_name="Длительность",
        help_text="Время на выполнение в секундах",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(120)
        ],
        default=60,
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичная",
        help_text="Видна ли привычка другим пользователям"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    last_completed = models.DateField(
        null=True,
        blank=True,
        verbose_name="Последнее выполнение",
        help_text="Когда привычка была выполнена в последний раз"
    )

    def __str__(self):
        return f"{self.action} в {self.time} ({self.place})"


    def clean(self):
        """
        Валидация данных привычки.

        Проверяет:
        - Соответствие времени выполнения (1-120 сек)
        - Периодичность (не реже 1 раза в 7 дней)
        - Корректность связей между привычками
        - Отсутствие циклических ссылок
        - Актуальность последнего выполнения
        """

        # Валидация времени выполнения
        if self.duration > 120:
            raise ValidationError(
                {"duration": "Время выполнения должно быть не больше 120 секунд."}
            )

        # Валидация периодичности
        if self.periodicity > 7:
            raise ValidationError(
                {"periodicity": "Нельзя выполнять привычку реже, чем 1 раз в 7 дней."}
            )

        # Валидация приятных привычек
        if self.is_pleasant:
            if self.reward:
                raise ValidationError(
                    {"reward": "У приятной привычки не может быть вознаграждения."}
                )
            if self.linked_habit:
                raise ValidationError(
                    {"linked_habit": "У приятной привычки не может быть связанной привычки."}
                )

        # Валидация полезных привычек
        else:
            if self.reward and self.linked_habit:
                raise ValidationError(
                    "Нельзя одновременно указывать и вознаграждение, и связанную привычку."
                )
            if not self.reward and not self.linked_habit:
                raise ValidationError(
                    "У полезной привычки должно быть либо вознаграждение, либо связанная привычка."
                )

        # Проверка связанной привычки
        if self.linked_habit and not self.linked_habit.is_pleasant:
            raise ValidationError(
                {"linked_habit": "В связанные привычки могут попадать только привычки с признаком приятной привычки."}
            )

        # Проверка на циклические ссылки
        if self.linked_habit:
            current = self.linked_habit
            while current:
                if current == self:
                    raise ValidationError(
                        {"linked_habit": "Обнаружена циклическая ссылка в привычках."}
                    )
                current = current.linked_habit

        # Проверка последнего выполнения
        if self.last_completed:
            days_passed = (timezone.now().date() - self.last_completed).days
            if days_passed > 7:
                raise ValidationError(
                    {"last_completed": "Нельзя не выполнять привычку более 7 дней."}
                )

    def save(self, *args, **kwargs):
        """Сохранение с обязательной предварительной валидацией"""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_reminder_message(self):
        """Генерация текста напоминания"""
        return (
            f"⏰ <b>Напоминание о привычке!</b>\n\n"
            f"<b>Действие:</b> {self.action}\n"
            f"<b>Место:</b> {self.place}\n"
            f"<b>Время выполнения:</b> {self.duration} сек.\n"
            f"<b>Периодичность:</b> {self.get_periodicity_display()}"
        )

    def mark_as_completed(self):
        """Отмечает привычку как выполненную (обновляет last_completed)."""
        self.last_completed = timezone.now().date()
        self.save()

    class Meta:
        verbose_name = "привычка"
        verbose_name_plural = "привычки"
        ordering = ["-created_at"]
