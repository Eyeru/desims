from django.db import models
from courses.models import Course
from academics.models import AcademicYear


class Exam(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    semester = models.IntegerField(null=True, blank=True)  # ADD THIS

    total_students = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "course", "semester"],
                name="unique_exam_per_semester"
            )
        ]

    def __str__(self):
        return f"{self.course.code}"