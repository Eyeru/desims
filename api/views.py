from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from courses.models import Course
from rooms.models import Room
from staff.models import Staff
from exams.models import Exam
from scheduling.models import ExamSchedule
from semester_setup.models import SemesterPlan
from datetime import date, timedelta
from django.db import transaction, IntegrityError
from academics.models import ExamSession, Holiday, AcademicYear
from allocations.models import ExamRoomAllocation
from allocations.services import (
    allocate_exam_rooms,
    allocate_plan_rooms,
    RoomAllocationError,
)


@api_view(["GET"])
def dashboard(request):

    plan = SemesterPlan.objects.filter(is_active=True,
                                       academic_year__is_active=True).first()

    active_plan = None

    if plan:
        active_plan = {
            "id": plan.id,
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


@api_view(["GET", "POST"])
def course_list(request):
    if request.method == "POST":
        data = request.data

        required_fields = [
            "code",
            "title",
            "year_level",
            "semester",
            "program_type",
        ]

        for field in required_fields:
            if field not in data or data[field] in ("", None):
                return Response(
                    {"error": f"{field} is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        code = str(data["code"]).strip().upper()
        title = str(data["title"]).strip()
        program_type = data["program_type"]

        if not code or not title:
            return Response(
                {"error": "Course code and title cannot be blank."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if program_type not in ["REGULAR", "EXTENSION"]:
            return Response(
                {"error": "Invalid program type."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            year_level = int(data["year_level"])
            semester = int(data["semester"])
        except (ValueError, TypeError):
            return Response(
                {"error": "Year level and semester must be numbers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if year_level < 1 or semester not in [1, 2]:
            return Response(
                {"error": "Invalid year level or semester."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_department_owned = data.get("is_department_owned", True)

        if not isinstance(is_department_owned, bool):
            return Response(
                {"error": "Course ownership must be true or false."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            course = Course.objects.create(
                code=code,
                title=title,
                year_level=year_level,
                semester=semester,
                program_type=program_type,
                is_department_owned=is_department_owned,
            )
        except IntegrityError:
            return Response(
                {
                    "error": (
                        "A course with this code, program type, "
                        "year level, and semester already exists."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "id": course.id,
                "code": course.code,
                "title": course.title,
                "year_level": course.year_level,
                "semester": course.semester,
                "program_type": course.program_type,
                "is_department_owned": course.is_department_owned,
            },
            status=status.HTTP_201_CREATED,
        )

    courses = Course.objects.all().order_by(
        "program_type", "year_level", "semester", "code"
    )

    response_data = [
        {
            "id": course.id,
            "code": course.code,
            "title": course.title,
            "year_level": course.year_level,
            "semester": course.semester,
            "program_type": course.program_type,
            "is_department_owned": course.is_department_owned,
        }
        for course in courses
    ]

    return Response(response_data)


@api_view(["PUT", "PATCH"])
def update_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    data = request.data

    allowed_fields = [
        "code",
        "title",
        "year_level",
        "semester",
        "program_type",
        "is_department_owned",
    ]

    for field in data:
        if field not in allowed_fields:
            return Response(
                {"error": f"Invalid field: {field}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    if request.method == "PUT":
        required_fields = [
            "code",
            "title",
            "year_level",
            "semester",
            "program_type",
        ]

        for field in required_fields:
            if field not in data or data[field] in ("", None):
                return Response(
                    {"error": f"{field} is required for a PUT request."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    updated_values = {
        "code": course.code,
        "title": course.title,
        "year_level": course.year_level,
        "semester": course.semester,
        "program_type": course.program_type,
        "is_department_owned": course.is_department_owned,
    }

    if "code" in data:
        updated_values["code"] = str(data["code"]).strip().upper()

    if "title" in data:
        updated_values["title"] = str(data["title"]).strip()

    if not updated_values["code"] or not updated_values["title"]:
        return Response(
            {"error": "Course code and title cannot be blank."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if "year_level" in data:
        try:
            updated_values["year_level"] = int(data["year_level"])
        except (ValueError, TypeError):
            return Response(
                {"error": "Year level must be a number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    if "semester" in data:
        try:
            updated_values["semester"] = int(data["semester"])
        except (ValueError, TypeError):
            return Response(
                {"error": "Semester must be a number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    if updated_values["year_level"] < 1:
        return Response(
            {"error": "Year level must be at least 1."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if updated_values["semester"] not in [1, 2]:
        return Response(
            {"error": "Semester must be 1 or 2."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if "program_type" in data:
        updated_values["program_type"] = data["program_type"]

    if updated_values["program_type"] not in ["REGULAR", "EXTENSION"]:
        return Response(
            {"error": "Invalid program type."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if "is_department_owned" in data:
        updated_values["is_department_owned"] = data["is_department_owned"]

    if not isinstance(updated_values["is_department_owned"], bool):
        return Response(
            {"error": "Course ownership must be true or false."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    for field, value in updated_values.items():
        setattr(course, field, value)

    try:
        course.save()
    except IntegrityError:
        return Response(
            {
                "error": (
                    "Another course already has this code, program type, "
                    "year level, and semester."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "id": course.id,
            "code": course.code,
            "title": course.title,
            "year_level": course.year_level,
            "semester": course.semester,
            "program_type": course.program_type,
            "is_department_owned": course.is_department_owned,
        }
    )


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
            {
                "error": (
                    "Please provide valid numbers and dates in YYYY-MM-DD "
                    "format."
                )
            },
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

    # Deactivate every active semester plan,
    # regardless of its academic year.
    SemesterPlan.objects.filter(
        is_active=True,
    ).update(is_active=False)

    # Activate only the selected plan.
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


@api_view(["GET"])
def semester_plan_courses(request, plan_id):
    plan = get_object_or_404(
        SemesterPlan,
        id=plan_id,
    )

    courses = Course.objects.filter(
        year_level=plan.year_level,
        semester=plan.semester,
        program_type=plan.program_type,
    ).order_by("code")

    data = [
        {
            "id": course.id,
            "code": course.code,
            "title": course.title,
            "year_level": course.year_level,
            "semester": course.semester,
            "program_type": course.program_type,
        }
        for course in courses
    ]

    return Response({
        "plan_id": plan.id,
        "academic_year": plan.academic_year.name,
        "year_level": plan.year_level,
        "semester": plan.semester,
        "program_type": plan.program_type,
        "course_count": len(data),
        "courses": data,
    })


@api_view(["POST"])
def generate_plan_exams(request, plan_id):
    plan = get_object_or_404(
        SemesterPlan.objects.select_related("academic_year"),
        id=plan_id,
    )

    courses = Course.objects.filter(
        year_level=plan.year_level,
        semester=plan.semester,
        program_type=plan.program_type,
    ).order_by("code")

    if not courses.exists():
        return Response(
            {
                "error": (
                    "No matching courses found. "
                    "Add or correct the course records first."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    created_count = 0
    existing_count = 0

    for course in courses:
        exam, created = Exam.objects.get_or_create(
            academic_year=plan.academic_year,
            course=course,
            semester=plan.semester,
            defaults={
                "total_students": plan.student_count,
            },
        )

        if created:
            created_count += 1
        else:
            existing_count += 1
    if not plan.is_generated:
        plan.is_generated = True
        plan.save(update_fields=["is_generated"])
    return Response(
        {
            "plan_id": plan.id,
            "academic_year": plan.academic_year.name,
            "year_level": plan.year_level,
            "semester": plan.semester,
            "program_type": plan.program_type,
            "created_count": created_count,
            "existing_count": existing_count,
            "message": (
                f"{created_count} exam record(s) created; "
                f"{existing_count} already existed."
            ),
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def generate_plan_schedule(request, plan_id):
    plan = get_object_or_404(
        SemesterPlan.objects.select_related("academic_year"),
        id=plan_id,
    )

    # Get all exams belonging to this plan.
    exams = Exam.objects.filter(
        academic_year=plan.academic_year,
        semester=plan.semester,
        course__year_level=plan.year_level,
        course__program_type=plan.program_type,
    ).order_by("course__code")

    if not exams.exists():
        return Response(
            {"error": "Generate exam records before scheduling."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Do not overwrite existing schedules.
    existing_schedules = ExamSchedule.objects.filter(plan=plan)

    if existing_schedules.exists():
        return Response(
            {
                "error": (
                    "This plan already has schedules. "
                    "Existing schedules were not changed."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Find eligible sessions.
    if plan.session_policy == "MORNING":
        sessions = ExamSession.objects.filter(name="MORNING")
    elif plan.session_policy == "AFTERNOON":
        sessions = ExamSession.objects.filter(name="AFTERNOON")
    else:
        sessions = ExamSession.objects.all().order_by("id")

    if not sessions.exists():
        return Response(
            {"error": "No suitable exam sessions are configured."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Find holidays.
    holidays = set(
        Holiday.objects.filter(
            date__range=(plan.start_date, plan.end_date)
        ).values_list("date", flat=True)
    )

    # Find eligible dates.
    eligible_dates = []
    current_date = plan.start_date

    while current_date <= plan.end_date:
        is_weekend = current_date.weekday() >= 5
        is_holiday = current_date in holidays

        if plan.program_type == "REGULAR":
            if not is_weekend and not is_holiday:
                eligible_dates.append(current_date)
        else:
            if not is_holiday:
                eligible_dates.append(current_date)

        current_date += timedelta(days=1)

    # Apply one-day gap between exam dates.
    selected_dates = eligible_dates[::2]

    if len(selected_dates) < exams.count():
        return Response(
            {
                "error": (
                    "Not enough eligible dates for all exams. "
                    "Extend the exam period or review the scheduling rules."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create schedules safely.
    created_schedules = []

    try:
        with transaction.atomic():
            for index, exam in enumerate(exams):
                session = sessions[index % len(sessions)]

                schedule = ExamSchedule.objects.create(
                    plan=plan,
                    exam=exam,
                    date=selected_dates[index],
                    session=session,
                    is_auto=True,
                    is_final=False,
                )

                created_schedules.append({
                    "exam_code": exam.course.code,
                    "exam_title": exam.course.title,
                    "date": schedule.date,
                    "session": schedule.session.name,
                })

    except Exception as exc:
        return Response(
            {"error": f"Schedule generation failed: {str(exc)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "plan_id": plan.id,
            "scheduled_count": len(created_schedules),
            "schedules": created_schedules,
            "message": (
                f"{len(created_schedules)} exam(s) scheduled successfully."
            ),
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def semester_plan_schedule(request, plan_id):
    plan = get_object_or_404(SemesterPlan, id=plan_id)

    schedules = ExamSchedule.objects.filter(
        plan=plan
    ).select_related(
        "exam__course",
        "session",
    ).order_by("date", "session__start_time")

    schedule_data = []

    for schedule in schedules:
        schedule_data.append({
            "id": schedule.id,
            "exam_code": schedule.exam.course.code,
            "exam_title": schedule.exam.course.title,
            "date": schedule.date,
            "session": schedule.session.name,
            "is_auto": schedule.is_auto,
            "is_final": schedule.is_final,
        })

    return Response({
        "plan_id": plan.id,
        "scheduled_count": len(schedule_data),
        "schedules": schedule_data,
    })


def room_response_data(room):
    return {
        "id": room.id,
        "name": room.name,
        "building": room.building,
        "physical_capacity": room.physical_capacity,
        "exam_capacity": room.exam_capacity,
        "room_type": room.room_type,
        "is_active": room.is_active,
        "department": room.department,
    }


@api_view(["GET", "POST"])
def room_list(request):
    if request.method == "POST":
        data = request.data

        required_fields = [
            "name",
            "building",
            "physical_capacity",
            "exam_capacity",
            "room_type",
        ]

        for field in required_fields:
            if field not in data or data[field] in ("", None):
                return Response(
                    {"error": f"{field} is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        name = str(data["name"]).strip()
        building = str(data["building"]).strip()
        department = data.get("department")

        if not name or not building:
            return Response(
                {"error": "Room name and building cannot be blank."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if department is not None:
            department = str(department).strip() or None

        room_type = data["room_type"]

        if room_type not in ["CLASSROOM", "HALL"]:
            return Response(
                {"error": "Room type must be CLASSROOM or HALL."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            physical_capacity = int(data["physical_capacity"])
            exam_capacity = int(data["exam_capacity"])
        except (ValueError, TypeError):
            return Response(
                {"error": "Room capacities must be whole numbers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if physical_capacity < 1 or exam_capacity < 1:
            return Response(
                {"error": "Room capacities must be greater than zero."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if exam_capacity > physical_capacity:
            return Response(
                {"error": "Exam capacity cannot exceed physical capacity."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_active = data.get("is_active", True)

        if not isinstance(is_active, bool):
            return Response(
                {"error": "Room active status must be true or false."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        room = Room.objects.create(
            name=name,
            building=building,
            physical_capacity=physical_capacity,
            exam_capacity=exam_capacity,
            room_type=room_type,
            is_active=is_active,
            department=department,
        )

        return Response(
            room_response_data(room),
            status=status.HTTP_201_CREATED,
        )

    rooms = Room.objects.all().order_by("building", "name")

    return Response([
        room_response_data(room)
        for room in rooms
    ])


@api_view(["PATCH"])
def update_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    data = request.data

    allowed_fields = [
        "name",
        "building",
        "physical_capacity",
        "exam_capacity",
        "room_type",
        "is_active",
        "department",
    ]

    for field in data:
        if field not in allowed_fields:
            return Response(
                {"error": f"Invalid field: {field}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    if not data:
        return Response(
            {"error": "No update data provided."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    updated = {
        "name": room.name,
        "building": room.building,
        "physical_capacity": room.physical_capacity,
        "exam_capacity": room.exam_capacity,
        "room_type": room.room_type,
        "is_active": room.is_active,
        "department": room.department,
    }

    if "name" in data:
        updated["name"] = str(data["name"]).strip()

    if "building" in data:
        updated["building"] = str(data["building"]).strip()

    if not updated["name"] or not updated["building"]:
        return Response(
            {"error": "Room name and building cannot be blank."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    for field in ["physical_capacity", "exam_capacity"]:
        if field in data:
            try:
                updated[field] = int(data[field])
            except (ValueError, TypeError):
                return Response(
                    {"error": f"{field} must be a whole number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    if updated["physical_capacity"] < 1 or updated["exam_capacity"] < 1:
        return Response(
            {"error": "Room capacities must be greater than zero."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if updated["exam_capacity"] > updated["physical_capacity"]:
        return Response(
            {"error": "Exam capacity cannot exceed physical capacity."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if "room_type" in data:
        updated["room_type"] = data["room_type"]

    if updated["room_type"] not in ["CLASSROOM", "HALL"]:
        return Response(
            {"error": "Room type must be CLASSROOM or HALL."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if "is_active" in data:
        updated["is_active"] = data["is_active"]

        # Prevent deactivation when future or today's exams use this room.
        if room.is_active and updated["is_active"] is False:
            has_upcoming_exams = ExamRoomAllocation.objects.filter(
                room=room,
                exam_schedule__isnull=False,
                exam_schedule__date__gte=date.today(),
            ).exists()

            if has_upcoming_exams:
                return Response(
                    {
                        "error": (
                            "This room cannot be deactivated because it "
                            "is assigned to an upcoming exam. "
                            "Reassign the exam first."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

    if not isinstance(updated["is_active"], bool):
        return Response(
            {"error": "Room active status must be true or false."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if "department" in data:
        department = data["department"]
        updated["department"] = (
            str(department).strip() or None
            if department is not None
            else None
        )

    for field, value in updated.items():
        setattr(room, field, value)

    room.save()

    return Response(room_response_data(room))


@api_view(["POST"])
def allocate_exam_rooms_view(request, schedule_id):
    exam_schedule = get_object_or_404(
        ExamSchedule,
        id=schedule_id,
    )

    try:
        result = allocate_exam_rooms(exam_schedule)

        return Response(
            {
                "message": "Rooms allocated successfully.",
                "data": result,
            },
            status=status.HTTP_200_OK,
        )

    except RoomAllocationError as error:
        return Response(
            {"error": str(error)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def allocate_plan_rooms_view(request, plan_id):
    plan = get_object_or_404(
        SemesterPlan,
        id=plan_id,
    )

    result = allocate_plan_rooms(plan.id)

    return Response(
        {
            "message": "Batch room allocation completed.",
            "data": result,
        },
        status=status.HTTP_200_OK,
    )
