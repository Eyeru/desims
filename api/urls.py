from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard),
    path("courses/", views.course_list),
    path("courses/<int:course_id>/", views.update_course),
    path("rooms/", views.room_list),
    path("rooms/<int:room_id>/", views.update_room),
    path("staff/", views.staff_list),
    path("staff/<int:staff_id>/", views.update_staff),
    path("academic-years/", views.academic_year_list),
    path("academic-years/<int:year_id>/activate/",
         views.activate_academic_year,),
    path("semester-plans/", views.semester_plan_list),
    path("semester-plans/create/", views.create_semester_plan),
    path("semester-plans/<int:plan_id>/activate/",
         views.activate_semester_plan,),
    path(
        "semester-plans/<int:plan_id>/courses/",
        views.semester_plan_courses,
     ),
    path(
          "semester-plans/<int:plan_id>/generate-exams/",
          views.generate_plan_exams,
     ),
    path(
          "semester-plans/<int:plan_id>/generate-schedule/",
          views.generate_plan_schedule,
     ),
    path(
          "semester-plans/<int:plan_id>/schedule/",
          views.semester_plan_schedule,
     ),
    path(
        "exam-schedules/<int:schedule_id>/allocate-rooms/",
        views.allocate_exam_rooms_view,
    ),
    path(
        "semester-plans/<int:plan_id>/allocate-rooms/",
        views.allocate_plan_rooms_view,
    ),

]
