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


from datetime import date


@api_view(["GET"])
def semester_plan_list(request):
    plans = SemesterPlan.objects.select_related(
        "academic_year"
    ).order_by("-created_at")

    data = [
        {
            "id": plan.id,
            "academic_year_id": plan.academic_year.id,
            "academic_year": plan.academic_year.name,
            "year_level": plan.year_level,
            "semester": plan.semester,
            "program_type": plan.program_type,
            "student_count": plan.student_count,
            "start_date": plan.start_date,
            "end_date": plan.end_date,
            "session_policy": plan.session_policy,
            "is_active": plan.is_active,
            "is_generated": plan.is_generated,
        }
        for plan in plans
    ]

    return Response(data)


@api_view(["POST"])
def create_semester_plan(request):
    data = request.data

    required_fields = [
        "academic_year_id",
        "year_level",
        "semester",
        "program_type",
        "student_count",
        "start_date",
        "end_date",
    ]

    for field in required_fields:
        if data.get(field) in (None, ""):
            return Response(
                {"error": f"{field} is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    try:
        year_level = int(data["year_level"])
        semester = int(data["semester"])
        student_count = int(data["student_count"])
        start_date = date.fromisoformat(data["start_date"])
        end_date = date.fromisoformat(data["end_date"])
    except (ValueError, TypeError):
        return Response(
            {"error": "Please provide valid numbers and dates in YYYY-MM-DD format."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if year_level < 1 or semester not in (1, 2) or student_count < 1:
        return Response(
            {"error": "Year level, semester, or student count is invalid."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if end_date < start_date:
        return Response(
            {"error": "End date cannot be before start date."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    program_type = data["program_type"]
    if program_type not in ("REGULAR", "EXTENSION"):
        return Response(
            {"error": "Program type must be REGULAR or EXTENSION."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    session_policy = data.get("session_policy", "MIXED")
    if session_policy not in ("MORNING", "AFTERNOON", "MIXED"):
        return Response(
            {"error": "Invalid session policy."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    academic_year = get_object_or_404(
        AcademicYear,
        id=data["academic_year_id"],
    )
    if SemesterPlan.objects.filter(
        academic_year=academic_year,
        year_level=year_level,
        semester=semester,
        program_type=program_type,
    ).exists():
        return Response(
            {
                "error": (
                    "A semester plan already exists for this "
                    "academic year, year level, semester, "
                    "and program type."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    plan = SemesterPlan.objects.create(
        academic_year=academic_year,
        year_level=year_level,
        semester=semester,
        program_type=program_type,
        student_count=student_count,
        start_date=start_date,
        end_date=end_date,
        session_policy=session_policy,
        is_active=False,
    )

    return Response(
        {
            "id": plan.id,
            "academic_year_id": plan.academic_year_id,
            "academic_year": plan.academic_year.name,
            "year_level": plan.year_level,
            "semester": plan.semester,
            "program_type": plan.program_type,
            "student_count": plan.student_count,
            "start_date": plan.start_date,
            "end_date": plan.end_date,
            "session_policy": plan.session_policy,
            "is_active": plan.is_active,
            "is_generated": plan.is_generated,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def activate_semester_plan(request, plan_id):
    plan = get_object_or_404(
        SemesterPlan,
        id=plan_id,
    )

    # Deactivate other plans for the same academic year.
    SemesterPlan.objects.filter(
        academic_year=plan.academic_year,
        is_active=True,
    ).update(is_active=False)

    # Activate the selected plan.
    plan.is_active = True
    plan.save(update_fields=["is_active"])

    return Response({
        "id": plan.id,
        "academic_year": plan.academic_year.name,
        "year_level": plan.year_level,
        "semester": plan.semester,
        "program_type": plan.program_type,
        "is_active": plan.is_active,
        "message": "Semester plan activated successfully.",
    })