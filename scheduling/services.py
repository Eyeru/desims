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

    candidate = date + timedelta(days=2)

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



def get_plan_session(plan, sessions):

    if plan.session_policy == "MORNING":
        return sessions.filter(name="MORNING").first()

    if plan.session_policy == "AFTERNOON":
        return sessions.filter(name="AFTERNOON").first()

    return None  # or fallback mixed logic

# ----------------------------
# SCHEDULING ENGINE
# ----------------------------

def schedule_exams(plan, exams):
    if not plan.is_active:
        return  # Only schedule exams for the active plan
    sessions = list(
        ExamSession.objects.all().order_by("start_time")
    )

    fixed_session = get_plan_session(plan, sessions)

    if not fixed_session:
        raise ValueError("No valid session found for the plan's session policy")
 
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
                "plan": plan,
                "date": current_date,
                "session": session,
                "is_auto": True,
                "is_final": False,
            }
        )

        current_date = next_valid_date(current_date)

        session_index += 1

        if session_index % len(sessions) == 0:
            current_date = next_valid_date(current_date)


# ----------------------------
# FULL PIPELINE
# ----------------------------

def generate_full_plan(plan):
    if plan is None:
        raise ValueError("SemesterPlan is required but None was provided")
    if plan.is_generated:
        return ExamSchedule.objects.filter(plan=plan)
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


def regenerate_plan(plan):

    ExamSchedule.objects.filter(plan=plan).delete()

    exams = generate_exams(plan)

    schedule_exams(plan, exams)

    schedules = ExamSchedule.objects.filter(plan=plan)

    allocate_all_exams(schedules)

    assign_all_invigilators(schedules)

    plan.is_generated = True
    plan.save()

    return schedules
