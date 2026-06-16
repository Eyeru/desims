from scheduling.models import ExamSchedule
from allocations.models import ExamRoomAllocation
from invigilation.models import InvigilationAssignment
from django.db.models import Count

def detect_room_conflicts():
    conflicts = []

    schedules = ExamSchedule.objects.all()

    for schedule in schedules:
        rooms = ExamRoomAllocation.objects.filter(
            exam_schedule=schedule
        )

        room_ids = list(rooms.values_list("room_id", flat=True))

        # check duplicates in same date/session
        overlap = ExamRoomAllocation.objects.filter(
            exam_schedule__date=schedule.date,
            exam_schedule__session=schedule.session,
            room_id__in=room_ids
        ).exclude(exam_schedule=schedule)

        if overlap.exists():
            conflicts.append({
                "type": "ROOM_CONFLICT",
                "schedule": str(schedule)
            })

    return conflicts


def detect_staff_overload(max_per_day=2):
    """
    Correct rule:
    Each staff can only invigilate max N exams per DAY
    """

    conflicts = []

    grouped = InvigilationAssignment.objects.values(
        "staff_id",
        "exam_schedule__date"
    ).annotate(total=Count("id"))

    for g in grouped:

        if g["total"] > max_per_day:
            conflicts.append({
                "type": "STAFF_OVERLOAD",
                "staff_id": g["staff_id"],
                "date": g["exam_schedule__date"],
                "count": g["total"]
            })

    return conflicts


def detect_capacity_issues():
    conflicts = []

    schedule_map = {}

    allocations = ExamRoomAllocation.objects.select_related("exam_schedule", "exam_schedule__exam")

    for alloc in allocations:
        schedule = alloc.exam_schedule

        if schedule.id not in schedule_map:
            schedule_map[schedule.id] = {
                "schedule": schedule,
                "total": 0
            }

        schedule_map[schedule.id]["total"] += alloc.allocated_students

    # compare expected vs actual
    for item in schedule_map.values():

        expected = item["schedule"].exam.total_students
        actual = item["total"]

        if expected != actual:
            conflicts.append({
                "type": "CAPACITY_MISMATCH",
                "schedule": str(item["schedule"]),
                "expected": expected,
                "actual": actual
            })

    return conflicts

def run_all_conflict_checks():
    return {
        "room_conflicts": detect_room_conflicts(),
        "staff_conflicts": detect_staff_overload(),
        "capacity_issues": detect_capacity_issues(),
    }