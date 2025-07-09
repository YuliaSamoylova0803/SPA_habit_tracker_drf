from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from tracking_habits.models import Habit
from tracking_habits.paginators import TrackingHabitsPaginator
from tracking_habits.serializers import HabitSerializer, PublicHabitSerializer
from users.permissions import IsOwner


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    pagination_class = TrackingHabitsPaginator
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        """Возвращает только привычки текущего пользователя"""
        if getattr(self, "swagger_fake_view", False):
            # Для генерации схемы Swagger возвращаем пустой queryset
            return Habit.objects.none()

        if self.action == "public":
            return Habit.objects.filter(is_public=True)
        return Habit.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def public(self, request):
        """Список публичных привычек (только для чтения)"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PublicHabitSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PublicHabitSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
