from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard),
    path("academic-years/", views.academic_year_list),
    path("academic-years/<int:year_id>/activate/",
         views.activate_academic_year,),
]
