from django.urls import path
from .views import download_invigilation_sheet

urlpatterns = [
    path("invigilation/<int:schedule_id>/", download_invigilation_sheet),
]