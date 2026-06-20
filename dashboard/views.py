from django.shortcuts import render

from semester_setup.models import SemesterPlan
from exams.models import Exam
from scheduling.models import ExamSchedule
from allocations.models import ExamRoomAllocation
from invigilation.models import InvigilationAssignment


def planning_dashboard(request):

    active_plan = SemesterPlan.objects.filter(
        is_active=True
    ).first()

    context = {
        "active_plan": active_plan,
        "exam_count": 0,
        "schedule_count": 0,
        "allocation_count": 0,
        "invigilation_count": 0,
        "recent_schedules": [],
    }

    if active_plan:

        exams = Exam.objects.filter(
            course__year_level=active_plan.year_level,
            course__semester=active_plan.semester,
            course__program_type=active_plan.program_type,
        )

        schedules = ExamSchedule.objects.filter(
            exam__in=exams
        ).select_related(
            "exam",
            "exam__course",
            "session"
        )

        allocations = ExamRoomAllocation.objects.filter(
            exam_schedule__in=schedules
        )

        invigilations = InvigilationAssignment.objects.filter(
            exam_schedule__in=schedules
        )

        context.update({
            "exam_count": exams.count(),
            "schedule_count": schedules.count(),
            "allocation_count": allocations.count(),
            "invigilation_count": invigilations.count(),
            "recent_schedules": schedules.order_by("date")[:5],
        })

    return render(
        request,
        "dashboard/index.html",
        context
    )


def schedule_view(request):

    schedules = (
        ExamSchedule.objects
        .select_related(
            "exam",
            "exam__course",
            "session"
        )
        .order_by(
            "date",
            "session__start_time"
        )
    )

    return render(
        request,
        "dashboard/schedules.html",
        {
            "schedules": schedules
        }
    )

def full_schedule_view(request):

    schedules = ExamSchedule.objects.select_related(
        "exam",
        "exam__course",
        "session"
    ).order_by(
        "date",
        "session__start_time"
    )

    rows = []

    for schedule in schedules:

        rooms = ExamRoomAllocation.objects.filter(
            exam_schedule=schedule
        )

        invigilators = InvigilationAssignment.objects.filter(
            exam_schedule=schedule
        )

        rows.append({
            "schedule": schedule,
            "rooms": rooms,
            "invigilators": invigilators,
        })

    return render(
        request,
        "dashboard/full_schedule.html",
        {
            "rows": rows
        }
    )