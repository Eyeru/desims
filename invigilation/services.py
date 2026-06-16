from django.db.models import Count

from staff.models import Staff
from rooms.models import Room

from allocations.models import ExamRoomAllocation
from .models import InvigilationAssignment


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


def busy_staff(date, session):
    """
    Staff already assigned in the same
    date/session cannot be assigned again.
    """

    return Staff.objects.filter(
        invigilationassignment__exam_schedule__date=date,
        invigilationassignment__exam_schedule__session=session
    ).distinct()


def eligible_staff(program_type):
    """
    Extension exams:
    only EXTENSION or BOTH staff.

    Regular exams:
    any active staff.
    """

    if program_type == "EXTENSION":

        return Staff.objects.filter(
            is_active=True,
            program_type__in=[
                Staff.EXTENSION,
                Staff.BOTH
            ]
        )

    return Staff.objects.filter(
        is_active=True
    )


def assign_invigilators(schedule):

    required = required_invigilators(schedule)

    available = eligible_staff(
        schedule.exam.course.program_type
    )

    available = available.exclude(
        id__in=busy_staff(
            schedule.date,
            schedule.session
        )
    )

    available = available.annotate(
        assignment_count=Count(
            "invigilationassignment"
        )
    ).order_by(
        "assignment_count"
    )

    assignments = []

    for staff in available[:required]:

        assignment = InvigilationAssignment.objects.create(
            exam_schedule=schedule,
            staff=staff,
            is_auto=True
        )

        assignments.append(assignment)

    return assignments


def assign_all_invigilators(exam_schedules):

    results = []

    for schedule in exam_schedules:

        assignments = assign_invigilators(
            schedule
        )

        results.append(
            (
                schedule,
                assignments
            )
        )

    return results