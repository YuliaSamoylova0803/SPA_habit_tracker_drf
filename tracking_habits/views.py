from rest_framework import viewsets, permissions
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
        if self.action == "public":
            return Habit.objects.filter(
                is_public=True
            )  # Исправлено is_puplic на is_public
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
        # Автоматически привязываем привычку к текущему пользователю
        serializer.save(user=self.request.user)
