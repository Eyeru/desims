from django.db import models

from scheduling.models import ExamSchedule
from staff.models import Staff


class InvigilationAssignment(models.Model):

    exam_schedule = models.ForeignKey(
        ExamSchedule,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE
    )

    is_auto = models.BooleanField(default=True)

    class Meta:
        unique_together = (
            "exam_schedule",
            "staff"
        )

    def __str__(self):
        return f"{self.staff} -> {self.exam_schedule}"