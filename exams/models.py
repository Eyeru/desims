from django.db import models
from courses.models import Course
from academics.models import AcademicYear, ExamSession


class Exam(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    date = models.DateField(null=True, blank=True)
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, null=True, blank=True)

    total_students = models.IntegerField(default=0)

    is_scheduled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.course.code} - {self.date}"