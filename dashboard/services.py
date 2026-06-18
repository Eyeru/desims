from semester_setup.models import SemesterPlan
from scheduling.models import ExamSchedule
from allocations.models import ExamRoomAllocation
from invigilation.models import InvigilationAssignment


def get_dashboard_summary():

    plan = SemesterPlan.objects.filter(is_active=True).first()

    if not plan:
        return None

    schedules = ExamSchedule.objects.filter(plan=plan)

    allocations = ExamRoomAllocation.objects.filter(
        exam_schedule__in=schedules
    )

    invigilations = InvigilationAssignment.objects.filter(
        exam_schedule__in=schedules
    )

    return {
        "plan": plan,
        "exams": schedules.values("exam").distinct().count(),
        "schedules": schedules.count(),
        "allocations": allocations.count(),
        "invigilations": invigilations.count(),
    }