from django.urls import path
from . import views

urlpatterns = [
    path("plans/", views.plans),
    path("plans/<int:plan_id>/", views.plan_detail),
]