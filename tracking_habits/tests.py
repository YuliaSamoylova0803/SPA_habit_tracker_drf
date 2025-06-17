from datetime import time

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from tracking_habits.models import Habit
from users.models import User
from datetime import time, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date

User = get_user_model()


class HabitTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='admin', email="admin@example.com", password="123zxc", is_staff=True
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Тестовые привычки
        self.habit = Habit.objects.create(
            user=self.user,
            action="Пить воду",
            time=time(8, 0),
            place="Дом",
            is_pleasant=False,
            periodicity=1,
            reward="Стакан воды",
            duration=120,
            is_public=False
        )

        self.public_habit = Habit.objects.create(
            user=self.other_user,
            action="Бег по утрам",
            time=time(7, 0),
            place="Парк",
            is_pleasant=True,  # Для приятной привычки можно не указывать reward
            periodicity=1,
            duration=60,  # Уменьшаем продолжительность
            is_public=True
        )

    def get_valid_habit_data(self, habit_type='normal'):
        """Возвращает валидные данные для создания привычки"""
        data = {
            "action": "Чтение",
            "time": "09:00:00",
            "place": "Диван",
            "is_pleasant": False,
            "periodicity": 1,
            "duration": 120,
            "is_public": False
        }

        if habit_type == 'normal':
            data["reward"] = "Чай"
        elif habit_type == 'linked':
            # Используем существующую приятную привычку
            data["linked_habit"] = self.public_habit.id
            data.pop('reward', None)
        elif habit_type == 'pleasant':
            data["is_pleasant"] = True
            data.pop('periodicity', None)
            data.pop('reward', None)

        return data

    def test_habit_retrieve(self):
        """
        Тестирование извлечение привычки
        """
        url = reverse("tracking_habits:habits-detail", args=(self.habit.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("action"), self.habit.action)


    def test_create_habit(self):
        """
        Тестирование создание привычки
        :return:
        """
        url = reverse("tracking_habits:habits-list")
        data = self.get_valid_habit_data()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 3)

    # Тесты обновления привычки
    def test_update_habit(self):
        """
            Тестирование обновления привычки
            :return:
        """
        url = reverse('tracking_habits:habits-detail', args=[self.habit.id])
        data = {"action": "Пить воду утром"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.action, 'Пить воду утром')

    # Тесты удаления привычки
    def test_delete_habit(self):
        """
            Тестирование удаление привычки
            :return:
        """
        url = reverse('tracking_habits:habits-detail', args=[self.habit.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 1)

    def test_create_habit_invalid_duration(self):
        """
        Тест создания привычки с недопустимой длительностью
        """
        url = '/habits/'
        data = self.get_valid_habit_data()
        data['duration'] = 130  # Превышает лимит
        data['action'] = "Медитация"  # Меняем действие для уникальности
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('duration', response.data)

    def test_create_habit_invalid_periodicity(self):
        """
        Тест создания привычки с недопустимой периодичностью
        """
        url = '/habits/'
        data = self.get_valid_habit_data()
        data['periodicity'] = 3  # Несуществующее значение
        data['action'] = "Йога"  # Меняем действие для уникальности
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('periodicity', response.data)

    def test_public_habits_list(self):
        """Тест получения списка публичных привычек"""
        # Сначала создаем публичную привычку
        data = self.get_valid_habit_data()
        data['is_public'] = True
        Habit.objects.create(user=self.user, **data)

        url = '/habits/public/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_user_habits_list(self):
        """Тест получения списка привычек текущего пользователя"""
        url = reverse("tracking_habits:habits-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должны видеть только свои привычки и публичные чужие
        self.assertEqual(len(response.data), 4)

    def test_update_other_user_habit(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('tracking_habits:habits-detail', args=[self.habit.id])
        response = self.client.patch(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_habit_with_valid_linked_habit(self):
        """Тест создания привычки с валидной приятной связанной привычкой"""
        url = reverse("tracking_habits:habits-list")
        data = self.get_valid_habit_data('linked')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 3)

        # Проверяем, что связь установлена правильно
        new_habit = Habit.objects.get(action=data['action'])
        self.assertEqual(new_habit.linked_habit, self.public_habit)

    def test_create_habit_with_invalid_linked_habit(self):
        """Тест с не-приятной связанной привычкой (должен вернуть ошибку)"""
        url = reverse("tracking_habits:habits-list")
        data = {
            "action": "Зарядка",
            "time": "07:30:00",
            "place": "Спальня",
            "is_pleasant": False,
            "periodicity": 1,
            "duration": 90,
            "linked_habit": self.habit.id  # self.habit - не приятная привычка
        }

        try:
            response = self.client.post(url, data, format='json')
            # Если не возникло исключение, проверяем код ответа
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('linked_habit', response.data)
        except ValidationError as e:
            # Ожидаемое исключение при валидации
            self.assertIn('linked_habit', e.message_dict)

        # Проверяем, что привычка не была создана
        self.assertEqual(Habit.objects.count(), 2)

    def test_last_completed_update(self):
        """Тест обновления даты последнего выполнения."""
        today = date.today()

        # Вызываем метод, который обновляет last_completed
        self.habit.mark_as_completed()  # <-- Вот это ключевой момент!

        self.assertEqual(self.habit.last_completed, today)

    def test_last_completed_validation(self):
        """Тест валидации last_completed (не более 7 дней назад)"""
        url = reverse("tracking_habits:habits-detail", args=(self.habit.pk,))
        old_date = timezone.now().date() - timedelta(days=8)
        data = {"last_completed": old_date}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_habit_serialization(self):
        """Тест корректности сериализации данных"""
        url = reverse("tracking_habits:habits-detail", args=[self.habit.id])
        response = self.client.get(url)
        data = response.json()

        self.assertIn('id', data)
        self.assertIn('action', data)
        self.assertIn('time', data)
        self.assertEqual(data['duration'], 120)
        self.assertIn('reward', data)

    def test_habit_limit(self):
        """Тест ограничения на количество привычек у пользователя"""
        # Создаем максимальное количество привычек
        for i in range(5):  # Предположим, лимит = 5
            data = self.get_valid_habit_data()
            data['action'] = f"Привычка {i}"
            self.client.post(reverse("tracking_habits:habits-list"), data)

        # Попытка создать ещё одну
        data = self.get_valid_habit_data()
        data['action'] = "Лишняя привычка"
        response = self.client.post(reverse("tracking_habits:habits-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reward_and_linked_conflict(self):
        """Тест, что нельзя одновременно указать и вознаграждение, и связанную привычку"""
        data = self.get_valid_habit_data()
        data['reward'] = 'Кофе'
        data['linked_habit'] = self.public_habit.id

        url = reverse("tracking_habits:habits-list")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Нельзя одновременно указывать', str(response.data))
