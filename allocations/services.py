from rooms.models import Room
from .models import ExamRoomAllocation


def get_available_rooms(date, session):

    occupied = ExamRoomAllocation.objects.filter(
        exam_schedule__date=date,
        exam_schedule__session=session
    ).values_list("room_id", flat=True)

    return Room.objects.filter(
        is_active=True
    ).exclude(
        id__in=occupied
    )


def split_rooms(rooms):

    classrooms = rooms.filter(
        room_type=Room.CLASSROOM
    ).order_by("-exam_capacity")

    halls = rooms.filter(
        room_type=Room.HALL
    ).order_by("-exam_capacity")

    return classrooms, halls


def allocate_exam(schedule):

    students = schedule.exam.total_students

    available_rooms = get_available_rooms(
        schedule.date,
        schedule.session
    )

    classrooms, halls = split_rooms(available_rooms)

    allocations = []

    # STEP 1: use classrooms first
    for room in classrooms:

        if students <= 0:
            break

        assigned = min(room.exam_capacity, students)

        allocations.append(
            ExamRoomAllocation.objects.create(
                exam_schedule=schedule,
                room=room,
                allocated_students=assigned
            )
        )

        students -= assigned

    # STEP 2: halls only if needed
    if students > 0:

        for hall in halls:

            if students <= 0:
                break

            assigned = min(hall.exam_capacity, students)

            allocations.append(
                ExamRoomAllocation.objects.create(
                    exam_schedule=schedule,
                    room=hall,
                    allocated_students=assigned
                )
            )

            students -= assigned

    return allocations


def allocate_all_exams(exam_schedules):

    results = []

    for schedule in exam_schedules:

        allocations = allocate_exam(schedule)

        results.append((schedule, allocations))

    return results