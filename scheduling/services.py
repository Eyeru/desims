from datetime import timedelta

from academics.models import Holiday, ExamSession
from exams.models import Exam
from .models import ExamSchedule


# ----------------------------
# HOLIDAY / DATE UTILITIES
# ----------------------------

def is_valid_day(date):
    """Check if date is not weekend or holiday."""
    if date.weekday() >= 5:  # Saturday/Sunday
        return False

    if Holiday.objects.filter(date=date).exists():
        return False

    return True


def next_valid_date(date):
    """Find next valid exam day (skips weekends + holidays)."""
    candidate = date + timedelta(days=1)

    while not is_valid_day(candidate):
        candidate += timedelta(days=1)

    return candidate


# ----------------------------
# EXAM GENERATION
# ----------------------------

def generate_exams(plan):
    """
    Create exams from courses matching:
    - year_level
    - semester
    - program_type
    """

    courses = plan.course_set.filter(
        year_level=plan.year_level,
        semester=plan.semester,
        program_type=plan.program_type,
    )

    exams = []

    for course in courses:

        exam, _ = Exam.objects.get_or_create(
            academic_year=plan.academic_year,
            course=course,
            defaults={
                "total_students": plan.student_count
            }
        )

        exams.append(exam)

    return exams


# ----------------------------
# SCHEDULING ENGINE
# ----------------------------

def schedule_exams(plan, exams):
    """
    Assign date + session to exams using:
    - no weekends
    - no holidays
    - multiple sessions per day
    """

    sessions = list(
        ExamSession.objects.all().order_by("start_time")
    )

    if not sessions:
        raise Exception("No ExamSession configured")

    current_date = plan.start_date

    # ensure valid start date
    while not is_valid_day(current_date):
        current_date += timedelta(days=1)

    session_index = 0

    for exam in exams:

        session = sessions[session_index % len(sessions)]

        ExamSchedule.objects.update_or_create(
            exam=exam,
            defaults={
                "date": current_date,
                "session": session,
                "is_auto": True,
                "is_final": False,
            }
        )

        session_index += 1

        # move to next day after all sessions used
        if session_index % len(sessions) == 0:
            current_date = next_valid_date(current_date)


# ----------------------------
# FULL PIPELINE
# ----------------------------

def generate_full_plan(plan):
    """
    End-to-end exam generation pipeline:
    1. Generate exams
    2. Schedule them
    3. Return schedules
    """

    exams = generate_exams(plan)

    schedule_exams(plan, exams)

    return ExamSchedule.objects.filter(exam__in=exams)