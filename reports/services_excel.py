from openpyxl import Workbook
from scheduling.models import ExamSchedule


def export_full_timetable():
    wb = Workbook()

    # Sheet 1: Exam Schedule
    ws1 = wb.active
    ws1.title = "Exam Timetable"

    ws1.append(["Course", "Date", "Session", "Status"])

    schedules = ExamSchedule.objects.select_related("exam", "session")

    for s in schedules:
        ws1.append([
            s.exam.course.code,
            str(s.date),
            s.session.name,
            "FINAL" if s.is_final else "DRAFT"
        ])

    # Sheet 2: Room Allocation
    ws2 = wb.create_sheet("Room Allocation")
    ws2.append(["Course", "Room", "Students"])

    for s in schedules:
        allocations = s.exam.examroomallocation_set.all()

        for a in allocations:
            ws2.append([
                s.exam.course.code,
                a.room.name,
                a.allocated_students
            ])

    # Sheet 3: Invigilation
    ws3 = wb.create_sheet("Invigilation")
    ws3.append(["Course", "Room", "Staff"])

    for s in schedules:
        invigs = s.exam.invigilationassignment_set.all()

        for i in invigs:
            ws3.append([
                s.exam.course.code,
                i.room.name,
                i.staff.first_name + " " + i.staff.last_name
            ])

    return wb