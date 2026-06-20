from django.urls import path
from .views import (
    planning_dashboard,
    schedule_view,
    full_schedule_view
    )

urlpatterns = [
    path("", planning_dashboard, name="dashboard"),
    path(
        "schedules/",
        schedule_view,
        name="schedule_view"
    ),
    path(
        "full-schedule/",
        full_schedule_view,
        name="full_schedule"
        ),
]