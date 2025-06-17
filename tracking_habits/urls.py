from tracking_habits.apps import TrackingHabitsConfig
from django.urls import path
from rest_framework.routers import DefaultRouter
from tracking_habits.views import HabitViewSet


app_name = TrackingHabitsConfig.name


router = DefaultRouter()
router.register(r"habits", HabitViewSet, basename="habits")

urlpatterns = [
    path(
        "habits/public/", HabitViewSet.as_view({"get": "public"}), name="public-habits"
    ),
] + router.urls
