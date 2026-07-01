from rest_framework.decorators import api_view
from rest_framework.response import Response

from courses.models import Course
from rooms.models import Room
from staff.models import Staff
from scheduling.models import ExamSchedule
from semester_setup.models import SemesterPlan

@api_view(["GET"])
def dashboard(request):

    plan = SemesterPlan.objects.filter(is_active=True).first()

    active_plan = None

    if plan:
        active_plan = {
            "academic_year": plan.academic_year.name,
            "year_level": plan.year_level,
            "semester": plan.semester,
            "program_type": plan.program_type,
            "session_policy": plan.session_policy,
        }

    data = {
        "active_plan": active_plan,
        "statistics": {
            "courses": Course.objects.count(),
            "rooms": Room.objects.count(),
            "staff": Staff.objects.count(),
            "schedules": ExamSchedule.objects.count(),
        },
    }

    return Response(data)
