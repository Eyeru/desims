from django.db import models
from rooms.models import Room
from scheduling.models import ExamSchedule


class ExamRoomAllocation(models.Model):
    exam_schedule = models.ForeignKey(
        ExamSchedule,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="room_allocations"
    )

    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    allocated_students = models.IntegerField(default=0)

    is_auto = models.BooleanField(default=True)

    class Meta:
        unique_together = ('exam_schedule', 'room')

    def __str__(self):
        return f"{self.exam_schedule} -> {self.room}"
