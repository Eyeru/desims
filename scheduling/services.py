from datetime import timedelta, datetime

from academics.models import Holiday, ExamSession
from courses.models import Course
from exams.models import Exam

from .models import ExamSchedule

from allocations.services import allocate_all_exams
from invigilation.services import assign_all_invigilators


# ----------------------------
# DATE UTILITIES
# ----------------------------

def is_valid_day(date):

    if date.weekday() >= 5:
        return False

    if Holiday.objects.filter(date=date).exists():
        return False

    return True


def next_valid_date(date):

    candidate = date + timedelta(days=1)

    while not is_valid_day(candidate):
        candidate += timedelta(days=1)

    return candidate


# ----------------------------
# EXAM GENERATION
# ----------------------------

def generate_exams(plan):

    courses = Course.objects.filter(
        year_level=plan.year_level,
        semester=plan.semester,
        program_type=plan.program_type,
    )

    exams = []

    for course in courses:

        exam, created = Exam.objects.get_or_create(
            academic_year=plan.academic_year,
            course=course,
            defaults={
                "total_students": plan.student_count
            }
        )

        if not created:
            exam.total_students = plan.student_count
            exam.save()

        exams.append(exam)

    return exams


# ----------------------------
# SCHEDULING ENGINE
# ----------------------------

def schedule_exams(plan, exams):

    sessions = list(
        ExamSession.objects.all().order_by("start_time")
    )

    if not sessions:
        raise Exception("No ExamSession configured")

    current_date = plan.start_date
    if isinstance(current_date, str):
        current_date = datetime.strptime(current_date, "%Y-%m-%d").date()

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

        if session_index % len(sessions) == 0:
            current_date = next_valid_date(current_date)


# ----------------------------
# FULL PIPELINE
# ----------------------------

def generate_full_plan(plan):
    if plan is None:
        raise ValueError("SemesterPlan is required but None was provided")

    exams = generate_exams(plan)

    schedule_exams(plan, exams)

    exam_schedules = ExamSchedule.objects.filter(
        exam__in=exams
    )

    allocate_all_exams(exam_schedules)

    assign_all_invigilators(exam_schedules)

    plan.is_generated = True
    plan.save()

    return exam_schedules
