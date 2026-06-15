from django.db import models
from courses.models import Course
from academics.models import AcademicYear, ExamSession


class Exam(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    total_students = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.course.code} - {self.date}"