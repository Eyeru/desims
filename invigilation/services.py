from django.db.models import Count
from staff.models import Staff
from rooms.models import Room

from allocations.models import ExamRoomAllocation
from .models import InvigilationAssignment


# -----------------------------
# REQUIRED INVIGILATORS RULE
# -----------------------------
def required_invigilators(schedule):
    """
    Classroom = 1 invigilator
    Hall = 2 invigilators
    """

    total = 0

    allocations = ExamRoomAllocation.objects.filter(
        exam_schedule=schedule
    )

    for allocation in allocations:
        if allocation.room.room_type == Room.HALL:
            total += 2
        else:
            total += 1

    return total


# -----------------------------
# STAFF AVAILABILITY CHECK
# -----------------------------
def busy_staff(date, session):
    """
    Staff already assigned in same slot
    cannot be reused.
    """

    return Staff.objects.filter(
        invigilationassignment__exam_schedule__date=date,
        invigilationassignment__exam_schedule__session=session
    ).distinct()


# -----------------------------
# ELIGIBLE STAFF RULE (FIXED)
# -----------------------------
def eligible_staff(program_type):
    """
    Only active staff for now.
    (Program filtering removed until Staff model supports it properly)
    """

    return Staff.objects.filter(is_active=True)


# -----------------------------
# STAFF SELECTION WITH LOAD LIMIT
# -----------------------------
def available_staff(schedule, max_per_day=2):
    """
    Prevent staff overload per day.
    """

    return Staff.objects.filter(is_active=True).exclude(
        id__in=Staff.objects.filter(
            invigilationassignment__exam_schedule__date=schedule.date
        ).annotate(
            total=Count("invigilationassignment")
        ).filter(total__gte=max_per_day).values_list("id", flat=True)
    )


# -----------------------------
# ASSIGN INVIGILATORS (FIXED)
# -----------------------------
def assign_invigilators(schedule):

    if not schedule.exam.semesterplan_set.filter(is_active=True).exists():
        return

    required = required_invigilators(schedule)

    available = available_staff(schedule)

    available = available.exclude(
        id__in=busy_staff(
            schedule.date,
            schedule.session
        )
    ).annotate(
        assignment_count=Count("invigilationassignment")
    ).order_by("assignment_count")

    assignments = []

    for staff in available[:required]:

        assignment = InvigilationAssignment.objects.create(
            exam_schedule=schedule,
            staff=staff,
            is_auto=True
        )

        assignments.append(assignment)

    return assignments


# -----------------------------
# BATCH ASSIGNMENT
# -----------------------------
def assign_all_invigilators(exam_schedules):

    results = []

    for schedule in exam_schedules:

        assignments = assign_invigilators(schedule)

        results.append((schedule, assignments))

    return results