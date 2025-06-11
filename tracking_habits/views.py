from django.shortcuts import render
from rest_framework import viewsets

from tracking_habits.models import Habit
from tracking_habits.paginators import TrackingHabitsPaginator


# Create your views here.
class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    pagination_class = TrackingHabitsPaginator
