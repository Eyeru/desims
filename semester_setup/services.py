from courses.models import Course
from exams.models import Exam
from datetime import timedelta
from academics.models import Holiday


def generate_exams(plan):

    if plan is None:
        raise ValueError("Semester plan is required to generate exams.")    

    courses = Course.objects.filter(
        year_level=plan.year_level,
        semester=plan.semester,
        program_type=plan.program_type,
    )

    generated_exams = []

    for course in courses:

        exam, created = Exam.objects.get_or_create(
            course=course,
            academic_year=plan.academic_year,
            defaults={
                "total_students": plan.student_count
            }
        )

        generated_exams.append(exam)

    return generated_exams


def schedule_exams(plan, exams):

    current_date = plan.start_date

    while not is_valid_exam_day(current_date):
        current_date += timedelta(days=1)

    for exam in exams:

        exam.date = current_date
        exam.is_scheduled = True
        exam.save()

        current_date = next_exam_day(current_date)

    
def is_valid_exam_day(date):

    if date.weekday() >= 5:
        return False

    if Holiday.objects.filter(date=date).exists():
        return False

    return True


def next_exam_day(current_date):

    candidate = current_date + timedelta(days=2)

    while not is_valid_exam_day(candidate):
        candidate += timedelta(days=1)

    return candidate