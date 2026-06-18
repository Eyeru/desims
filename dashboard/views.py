# dashboard/views.py

from django.shortcuts import render, redirect

from dashboard.services import get_dashboard_summary
from semester_setup.models import SemesterPlan
from semester_setup.services import set_active_plan

from .forms import PlanGenerationForm

from scheduling.services import generate_full_plan

from scheduling.models import ExamSchedule


def planning_dashboard(request):

    summary = get_dashboard_summary()

    return render(
        request,
        "dashboard/index.html",
        {
            "summary": summary
        }
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


