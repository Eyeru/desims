
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
    Assign invigilators to individual room allocations.

    Classroom = 1 invigilator
    Hall = 2 invigilators

    Preserve existing assignments and fill only remaining positions.
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

    allocations = list(
        ExamRoomAllocation.objects.filter(
            exam_schedule=schedule
        ).select_related("room").order_by("id")
    )

    if not allocations:
        return {
            "status": "failed",
            "message": "No room allocations found for this exam.",
            "assignments": [],
        }

    existing = list(
        InvigilationAssignment.objects.filter(
            exam_schedule=schedule
        ).select_related("staff", "room_allocation__room")
    )

    # Build the required positions for each room.
    room_slots = []

    for allocation in allocations:
        required_for_room = (
            2 if allocation.room.room_type == Room.HALL else 1
        )

        room_slots.extend([allocation] * required_for_room)

    required = len(room_slots)

    if len(existing) > required:
        return {
            "status": "failed",
            "message":
            "Existing assignments exceed the required number of invigilators.",
            "assignments": existing,
        }

    # Count positions already occupied by linked assignments.
    occupied = {}

    for assignment in existing:
        allocation = assignment.room_allocation

        if allocation is not None:
            if allocation.exam_schedule_id != schedule.id:
                return {
                    "status": "failed",
                    "message":
                    "An assignment is linked to a room from another exam.",
                    "assignments": existing,
                }

            occupied[allocation.id] = (
                occupied.get(allocation.id, 0) + 1
            )

    # Create the list of unoccupied room positions.
    remaining_slots = []

    for allocation in allocations:
        required_for_room = (
            2 if allocation.room.room_type == Room.HALL else 1
        )

        already_assigned = occupied.get(allocation.id, 0)

        if already_assigned > required_for_room:
            return {
                "status": "failed",
                "message":
                f"Too many invigilators assigned to {allocation.room.name}.",
                "assignments": existing,
            }

        remaining_slots.extend(
            [allocation] * (required_for_room - already_assigned)
        )

    # Link any existing unlinked assignments to available room positions.
    unlinked = [
        assignment
        for assignment in existing
        if assignment.room_allocation_id is None
    ]

    if len(unlinked) > len(remaining_slots):
        return {
            "status": "failed",
            "message":
            "Existing unlinked assignments exceed available room positions.",
            "assignments": existing,
        }

    for assignment, allocation in zip(unlinked, remaining_slots):
        assignment.room_allocation = allocation
        assignment.save(update_fields=["room_allocation"])

        occupied[allocation.id] = occupied.get(allocation.id, 0) + 1

    remaining_slots = remaining_slots[len(unlinked):]

    existing_count = len(existing)

    if not remaining_slots:
        return {
            "status": "skipped",
            "message": "The exam already has enough invigilators.",
            "assignments": existing,
        }

    assigned_staff_ids = [
        assignment.staff_id for assignment in existing
    ]

    # Exclude staff assigned to another exam in the same date/session.
    busy_staff_ids = InvigilationAssignment.objects.filter(
        exam_schedule__date=schedule.date,
        exam_schedule__session=schedule.session,
    ).exclude(
        exam_schedule=schedule
    ).values_list("staff_id", flat=True)

    # Exclude staff who already have two assignments that day.
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

    selected_staff = list(candidates[:len(remaining_slots)])

    if len(selected_staff) < len(remaining_slots):
        return {
            "status": "failed",
            "message": (
                f"Not enough eligible staff. Required "
                f"{len(remaining_slots)} additional invigilators, "
                f"but only {len(selected_staff)} are available."
            ),
            "assignments": [],
        }

    # Create each assignment with its specific room allocation.
    assignments = [
        InvigilationAssignment(
            exam_schedule=schedule,
            staff=staff,
            room_allocation=allocation,
            is_auto=True,
        )
        for staff, allocation in zip(
            selected_staff, remaining_slots
        )
    ]

    created = InvigilationAssignment.objects.bulk_create(assignments)

    return {
        "status": "success",
        "message": f"Assigned {len(created)} additional invigilators.",
        "assignments": existing + created,
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
