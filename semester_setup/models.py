from django.db import models
from courses.models import Course


class SemesterPlan(models.Model):

    REGULAR = "REGULAR"
    EXTENSION = "EXTENSION"

    PROGRAM_TYPES = [
        (REGULAR, "Regular"),
        (EXTENSION, "Extension"),
    ]

    academic_year = models.ForeignKey(
        "academics.AcademicYear",
        on_delete=models.CASCADE
    )

    year_level = models.PositiveSmallIntegerField()

    semester = models.PositiveSmallIntegerField()

    program_type = models.CharField(
        max_length=20,
        choices=PROGRAM_TYPES,
        default=REGULAR
    )

    student_count = models.PositiveIntegerField()

    start_date = models.DateField()
    end_date = models.DateField()

    is_generated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Year {self.year_level} "
            f"Semester {self.semester}"
        )