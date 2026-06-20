from courses.models import Course
from exams.models import Exam
from .models import SemesterPlan


def generate_exams(plan):

    if plan is None:
        raise ValueError("Semester plan is required to generate exams.")    

    courses = Course.objects.filter(
        year_level=plan.year_level,
        semester=plan.semester,
        program_type=plan.program_type,
    )

    exams = []

    for course in courses:

        exam, _ = Exam.objects.get_or_create(
            course=course,
            academic_year=plan.academic_year,
            defaults={
                "total_students": plan.student_count
            }
        )

        exams.append(exam)

    return exams


def set_active_plan(plan):
    SemesterPlan.objects.filter(is_active=True).update(is_active=False)
    plan.is_active = True
    plan.save()
