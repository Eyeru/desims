from django.db import models

from scheduling.models import ExamSchedule
from staff.models import Staff
from allocations.models import ExamRoomAllocation


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
    room_allocation = models.ForeignKey(
        ExamRoomAllocation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="invigilator_assignments",
    )

    is_auto = models.BooleanField(default=True)

    class Meta:
        unique_together = (
            "exam_schedule",
            "staff"
        )

    def __str__(self):
        return f"{self.staff} -> {self.exam_schedule}"