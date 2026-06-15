from .models import Conflict
from scheduling.models import ExamSchedule
from invigilation.models import InvigilationAssignment


def detect_staff_conflict(staff, exam_schedule):
    """
    Checks if staff has teaching or invigilation clash
    """

    # Check invigilation overlap
    existing = InvigilationAssignment.objects.filter(
        staff=staff,
        exam__exam__exam_date=exam_schedule.date
    )

    if existing.exists():
        return Conflict.objects.create(
            conflict_type="STAFF_CONFLICT",
            severity="BLOCKER",
            staff=staff,
            exam=exam_schedule.exam,
            message="Staff already assigned to another invigilation duty."
        )

    return None


def detect_room_conflict(room, exam_schedule):
    existing = ExamSchedule.objects.filter(
        date=exam_schedule.date,
        session=exam_schedule.session,
        exam__allocations__room=room
    )

    if existing.exists():
        return Conflict.objects.create(
            conflict_type="ROOM_CONFLICT",
            severity="BLOCKER",
            room=room,
            exam=exam_schedule.exam,
            message="Room already occupied in this session."
        )

    return None


def detect_teaching_conflict(staff, exam_schedule):
    # simplified placeholder (later we link teaching schedule app)
    return None


def run_all_conflicts(exam_schedule, staff_list, room_list):

    conflicts = []

    for staff in staff_list:
        c = detect_staff_conflict(staff, exam_schedule)
        if c:
            conflicts.append(c)

    for room in room_list:
        c = detect_room_conflict(room, exam_schedule)
        if c:
            conflicts.append(c)

    return conflicts