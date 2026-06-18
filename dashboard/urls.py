from django.urls import path
from .views import planning_dashboard, schedule_view

urlpatterns = [
    path("", planning_dashboard, name="dashboard"),
    path(
        "schedules/",
        schedule_view,
        name="schedule_view"
    ),
]