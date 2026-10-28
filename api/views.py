from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from academics.models import AcademicYear
from courses.models import Course
from rooms.models import Room
from staff.models import Staff
from scheduling.models import ExamSchedule
from semester_setup.models import SemesterPlan


@api_view(["GET"])
def dashboard(request):

    plan = SemesterPlan.objects.filter(is_active=True,
                                       academic_year__is_active=True).first()

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


@api_view(["GET", "POST"])
def academic_year_list(request):
    if request.method == "POST":
        name = request.data.get("name", "").strip()

        if not name:
            return Response(
                {"error": "Academic year name is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if AcademicYear.objects.filter(name=name).exists():
            return Response(
                {"error": "This academic year already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        year = AcademicYear.objects.create(name=name)

        return Response(
            {
                "id": year.id,
                "name": year.name,
                "is_active": year.is_active,
            },
            status=status.HTTP_201_CREATED,
        )

    years = AcademicYear.objects.all().order_by("-name")

    data = [
        {
            "id": year.id,
            "name": year.name,
            "is_active": year.is_active,
        }
        for year in years
    ]

    return Response(data)


@api_view(["POST"])
def activate_academic_year(request, year_id):
    year = get_object_or_404(AcademicYear, id=year_id)

    # Deactivate any currently active academic year.
    AcademicYear.objects.filter(is_active=True).update(is_active=False)

    # Activate the selected academic year.
    year.is_active = True
    year.save(update_fields=["is_active"])

    return Response({
        "id": year.id,
        "name": year.name,
        "is_active": year.is_active,
        "message": f"Academic year {year.name} is now active.",
    })
