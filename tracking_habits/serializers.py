from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("user", "created_at", "last_completed")


class PublicHabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ["id", "place", "time", "action", "duration", "is_public"]
        read_only_fields = fields
