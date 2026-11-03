from itertools import combinations

from django.db import transaction

from rooms.models import Room
from allocations.models import ExamRoomAllocation


class RoomAllocationError(Exception):
    """Raised when an exam cannot be allocated to available rooms."""


def _find_best_combination(rooms, total_students):
    """
    Find the minimum number of rooms that can accommodate all students.

    If multiple combinations use the same number of rooms,
    prefer the combination with the least unused capacity.
    """

    for room_count in range(1, len(rooms) + 1):
        valid_combinations = []

        for combination in combinations(rooms, room_count):
            total_capacity = sum(
                room.exam_capacity for room in combination
            )

            if total_capacity >= total_students:
                unused_capacity = total_capacity - total_students

                valid_combinations.append(
                    (unused_capacity, combination)
                )

        if valid_combinations:
            valid_combinations.sort(
                key=lambda item: (
                    item[0],
                    tuple(
                        (room.building, room.name, room.id)
                        for room in item[1]
                    ),
                )
            )

            return valid_combinations[0][1]

    return None


def _select_rooms(available_rooms, total_students):
    """
    Apply the room selection priority:

    1. Classrooms only.
    2. Halls only.
    3. Mixed classrooms and halls.
    """

    classrooms = [
        room for room in available_rooms
        if room.room_type == Room.CLASSROOM
    ]

    halls = [
        room for room in available_rooms
        if room.room_type == Room.HALL
    ]

    classrooms.sort(
        key=lambda room: (-room.exam_capacity, room.building, room.name)
    )

    halls.sort(
        key=lambda room: (-room.exam_capacity, room.building, room.name)
    )

    # Stage 1: Classrooms only
    selected = _find_best_combination(classrooms, total_students)

    if selected:
        return selected, "CLASSROOMS"

    # Stage 2: Halls only
    selected = _find_best_combination(halls, total_students)

    if selected:
        return selected, "HALLS"

    # Stage 3: Mixed classrooms and halls
    mixed_rooms = classrooms + halls

    selected = _find_best_combination(mixed_rooms, total_students)

    if selected and any(
        room.room_type == Room.CLASSROOM for room in selected
    ) and any(
        room.room_type == Room.HALL for room in selected
    ):
        return selected, "MIXED"

    return None, None


@transaction.atomic
def allocate_exam_rooms(exam_schedule):
    """
    Allocate rooms for one scheduled exam.

    Returns:
        A dictionary containing allocation details.

    Raises:
        RoomAllocationError if allocation is impossible or
        the exam already has allocations.
    """

    # Protect existing allocations from accidental replacement.
    if exam_schedule.room_allocations.exists():
        raise RoomAllocationError(
            "This exam already has room allocations. "
            "Existing allocations were not changed."
        )

    total_students = exam_schedule.exam.total_students

    if total_students <= 0:
        raise RoomAllocationError(
            "Cannot allocate rooms because the exam has no students."
        )

    # Find rooms already occupied by another exam on the same
    # date and in the same session.
    occupied_room_ids = ExamRoomAllocation.objects.filter(
        exam_schedule__date=exam_schedule.date,
        exam_schedule__session=exam_schedule.session,
    ).exclude(
        exam_schedule=exam_schedule
    ).values_list(
        "room_id", flat=True
    )

    # Only active, unoccupied rooms can be allocated.
    available_rooms = list(
        Room.objects.filter(
            is_active=True,
            exam_capacity__gt=0,
        ).exclude(
            id__in=occupied_room_ids
        )
    )

    # Apply the agreed classroom/hall priority.
    selected_rooms, allocation_type = _select_rooms(
        available_rooms,
        total_students,
    )

    if not selected_rooms:
        raise RoomAllocationError(
            f"Allocation failed for {total_students} students. "
            "Available classrooms, halls, and mixed combinations "
            "cannot accommodate all students. No allocations were made."
        )

    # Distribute all students without exceeding any room's
    # exam_capacity.
    remaining_students = total_students
    allocations_to_create = []

    for room in sorted(
        selected_rooms,
        key=lambda room: (
            -room.exam_capacity,
            room.building,
            room.name,
        ),
    ):
        allocated_students = min(
            room.exam_capacity,
            remaining_students,
        )

        if allocated_students > 0:
            allocations_to_create.append(
                ExamRoomAllocation(
                    exam_schedule=exam_schedule,
                    room=room,
                    allocated_students=allocated_students,
                    is_auto=True,
                )
            )

            remaining_students -= allocated_students

    # Final safety check before writing to the database.
    if remaining_students != 0:
        raise RoomAllocationError(
            "Allocation validation failed. No allocations were made."
        )

    # Create all allocations within the database transaction.
    ExamRoomAllocation.objects.bulk_create(allocations_to_create)

    return {
        "exam_schedule_id": exam_schedule.id,
        "total_students": total_students,
        "allocation_type": allocation_type,
        "rooms_used": len(allocations_to_create),
        "allocations": [
            {
                "room_id": allocation.room.id,
                "room_name": allocation.room.name,
                "room_type": allocation.room.room_type,
                "exam_capacity": allocation.room.exam_capacity,
                "allocated_students": allocation.allocated_students,
            }
            for allocation in allocations_to_create
        ],
    }


def allocate_plan_rooms(plan_id):
    """
    Allocate rooms for all scheduled exams in a semester plan.

    Exams are processed by date, then session ID.
    Existing allocations are preserved and skipped.
    An allocation failure for one exam does not stop the batch.
    """

    from scheduling.models import ExamSchedule

    schedules = ExamSchedule.objects.filter(
        plan_id=plan_id
    ).select_related(
        "exam",
        "session",
    ).order_by(
        "date",
        "session_id",
        "id",
    )

    results = {
        "plan_id": plan_id,
        "total_exams": schedules.count(),
        "successful": [],
        "skipped": [],
        "failed": [],
    }

    for schedule in schedules:

        # Preserve existing allocations.
        if schedule.room_allocations.exists():
            results["skipped"].append({
                "schedule_id": schedule.id,
                "exam_code": str(schedule.exam),
                "reason": "Exam already has room allocations.",
            })
            continue

        try:
            allocation_result = allocate_exam_rooms(schedule)

            results["successful"].append({
                "schedule_id": schedule.id,
                "exam_code": str(schedule.exam),
                "date": str(schedule.date),
                "session": str(schedule.session),
                "data": allocation_result,
            })

        except RoomAllocationError as error:
            results["failed"].append({
                "schedule_id": schedule.id,
                "exam_code": str(schedule.exam),
                "date": str(schedule.date),
                "session": str(schedule.session),
                "reason": str(error),
            })

    results["summary"] = {
        "total": results["total_exams"],
        "successful": len(results["successful"]),
        "skipped": len(results["skipped"]),
        "failed": len(results["failed"]),
    }

    return results
