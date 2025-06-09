from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError

from config import settings


class Habit(models.Model):
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
        help_text="Cоздатель привычки",
        related_name="habits"
    )
    place = models.CharField(
        max_length=50,
        verbose_name="Место",
        help_text="Где выполнять привычку"
    )
    time = models.TimeField(verbose_name="Время выполнения")
    action = models.CharField(
        max_length=100,
        verbose_name="Действие",
        help_text="Что именно нужно делать"
    )
    is_pleasant = models.BooleanField(default=False, verbose_name="Признак приятной привычки")
    linked_habit = models.ForeignKey(
        "self",  # Ссылка на эту же модель Habit
        on_delete=models.SET_NULL,  # При удалении связанной привычки ставит NULL
        null=True,  # Поле может быть пустым (необязательное)
        blank=True,  # Разрешает пустое значение в админке/формах
        verbose_name="Связанная привычка",  # Человекочитаемое название
        related_name="main_habit"  # Имя обратной связи
    )
    periodicity = models.PositiveSmallIntegerField(
        choices=PERIOD_CHOICES,
        default=DAILY,
        verbose_name="Периодичность (дни)"
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Вознаграждение",
        help_text="Чем себя наградить после выполнения (например, 'кофе', '5 минут соцсетей')"
    )
    duration = models.PositiveIntegerField(
        verbose_name="Время на выполнение (в секундах)",
        validators=[
            MinValueValidator(1, message="Минимальное время — 1 секунда.",),
            MaxValueValidator(120, message="Привычка не должна занимать больше 2 минут (120 сек).")
        ],
        default=60,
        help_text="Время в секундах (не более 120)"
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.user.email}: {self.action} в {self.time} ({self.place})"

    class Meta:
        verbose_name = "привычка"
        verbose_name_plural = "привычки"
        ordering = ["-created_at"]

    def clean(self):
        """Валидация на уровне модели (вызывается в save() или при full_clean())"""
        # 1. У приятной привычки не может быть вознаграждения или связанной привычки
        if self.is_pleasant:
            if self.reward or self.linked_habit:
                raise ValidationError(
                    "У приятной привычки не может быть вознаграждения или связанной привычки."
                )
        # 2. У полезной привычки должно быть либо вознаграждение, либо связанная привычка
        if not self.is_pleasant:
            if not (self.reward or self.linked_habit):
                raise ValidationError(
                    "У полезной привычки должно быть либо вознаграждение, либо связанная привычка."
                )
            if self.reward and self.linked_habit:
                raise ValidationError(
                    "Можно указать только вознаграждение ИЛИ связанную привычку, но не оба варианта."
                )
        # 3. Связанная привычка должна быть приятной
        if self.linked_habit and not self.linked_habit.is_pleasant:
            raise ValidationError(
                "Связанная привычка должна быть приятной (is_pleasant=True)."
            )
        # 4. Проверка на циклы
        if self.linked_habit:
            current = self.linked_habit
            while current:
                if current == self:
                    raise ValidationError("Обнаружена циклическая ссылка в привычках.")
                current = current.linked_habit

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)