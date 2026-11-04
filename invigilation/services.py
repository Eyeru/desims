
from django.db import transaction
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
    ).select_related("room")

    for allocation in allocations:
        if allocation.room.room_type == Room.HALL:
            total += 2
        else:
            total += 1

    return total


# -----------------------------
# ELIGIBLE STAFF RULE
# -----------------------------
def eligible_staff(program_type):
    """
    Regular exams:
        All active staff are eligible.

    Extension exams:
        Only active EXTENSION and BOTH staff are eligible.
    """
    staff = Staff.objects.filter(is_active=True)

    if program_type == "EXTENSION":
        staff = staff.filter(
            program_type__in=["EXTENSION", "BOTH"]
        )

    return staff


# -----------------------------
# STAFF SELECTION
# -----------------------------
def available_staff(schedule, max_per_day=2):
    """
    Return active staff who have not reached the daily assignment limit.
    """
    overloaded_staff = (
        Staff.objects.filter(
            invigilationassignment__exam_schedule__date=schedule.date
        )
        .values("id")
        .annotate(total=Count("invigilationassignment"))
        .filter(total__gte=max_per_day)
        .values_list("id", flat=True)
    )

    return Staff.objects.filter(is_active=True).exclude(
        id__in=overloaded_staff
    )


# -----------------------------
# ASSIGN INVIGILATORS
# -----------------------------
@transaction.atomic
def assign_invigilators(schedule):
    """
    Preserve manual assignments and automatically fill remaining positions.

    Automatic assignments are all-or-nothing.
    """

    if not schedule.plan:
        return {
            "status": "failed",
            "message": "This exam schedule has no semester plan.",
            "assignments": [],
        }

    if not schedule.plan.is_active:
        return {
            "status": "failed",
            "message": "The semester plan is not active.",
            "assignments": [],
        }

    required = required_invigilators(schedule)

    if required == 0:
        return {
            "status": "failed",
            "message": "No room allocations found for this exam.",
            "assignments": [],
        }

    existing = list(InvigilationAssignment.objects.filter(
        exam_schedule=schedule
    ).select_related("staff"))

    existing_count = len(existing)

    if existing_count >= required:
        return {
            "status": "skipped",
            "message": "The exam already has enough invigilators.",
            "assignments": list(existing),
        }

    remaining = required - existing_count

    assigned_staff_ids = existing.values_list("staff_id", flat=True)

    # Exclude staff assigned to another exam in the same date/session.
    busy_staff_ids = InvigilationAssignment.objects.filter(
        exam_schedule__date=schedule.date,
        exam_schedule__session=schedule.session,
    ).exclude(
        exam_schedule=schedule
    ).values_list("staff_id", flat=True)

    # Count each staff member's assignments on this date,
    # excluding this exam's existing assignments.
    daily_load = (
        InvigilationAssignment.objects.filter(
            exam_schedule__date=schedule.date
        )
        .exclude(exam_schedule=schedule)
        .values("staff_id")
        .annotate(total=Count("id"))
    )

    overloaded_ids = [
        item["staff_id"]
        for item in daily_load
        if item["total"] >= 2
    ]

    candidates = (
        eligible_staff(schedule.plan.program_type)
        .exclude(id__in=assigned_staff_ids)
        .exclude(id__in=busy_staff_ids)
        .exclude(id__in=overloaded_ids)
        .annotate(
            assignment_count=Count("invigilationassignment")
        )
        .order_by("assignment_count", "id")
    )

    selected_staff = list(candidates[:remaining])

    if len(selected_staff) < remaining:
        return {
            "status": "failed",
            "message": (
                f"Not enough eligible staff. Required {remaining} "
                f"additional invigilators, but only "
                f"{len(selected_staff)} are available."
            ),
            "assignments": [],
        }

    assignments = [
        InvigilationAssignment(
            exam_schedule=schedule,
            staff=staff,
            is_auto=True,
        )
        for staff in selected_staff
    ]

    created = InvigilationAssignment.objects.bulk_create(assignments)

    return {
        "status": "success",
        "message": f"Assigned {len(created)} additional invigilators.",
        "assignments": list(existing) + created,
    }


# -----------------------------
# BATCH ASSIGNMENT
# -----------------------------
def assign_all_invigilators(exam_schedules):
    results = []

    for schedule in exam_schedules:
        try:
            result = assign_invigilators(schedule)
        except Exception as exc:
            result = {
                "status": "failed",
                "message": str(exc),
                "assignments": [],
            }

        results.append({
            "schedule": schedule,
            **result,
        })

    return results
