from rooms.models import Room
from .models import ExamRoomAllocation


def allocate_rooms(exam):
    students = exam.total_students

    # available rooms sorted by capacity
    rooms = Room.objects.all().order_by('-exam_capacity')

    allocations = []

    remaining = students

    for room in rooms:
        if remaining <= 0:
            break

        capacity = room.exam_capacity

        if capacity <= 0:
            continue

        take = min(capacity, remaining)

        allocation = ExamRoomAllocation(
            exam=exam,
            room=room,
            allocated_students=take,
            is_auto=True
        )
        allocation.save()

        allocations.append(allocation)

        remaining -= take

    if remaining > 0:
        return False, f"Not enough capacity for {remaining} students"

    return True, allocations