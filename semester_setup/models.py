from django.db import models
# from courses.models import Course


class SemesterPlan(models.Model):

    REGULAR = "REGULAR"
    EXTENSION = "EXTENSION"

    PROGRAM_TYPES = [
        (REGULAR, "Regular"),
        (EXTENSION, "Extension"),
    ]

    SESSION_POLICY_CHOICES = [
        ("MORNING", "Morning Only"),
        ("AFTERNOON", "Afternoon Only"),
        ("MIXED", "Mixed"),
    ]

    session_policy = models.CharField(
        max_length=20,
        choices=SESSION_POLICY_CHOICES,
        default="MIXED"
    )

    exam_session = models.ForeignKey(
        "academics.ExamSession",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

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
   
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"Year {self.year_level} "
            f"Semester {self.semester}"
        )
