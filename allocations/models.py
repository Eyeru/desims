from django.db import models
from exams.models import Exam
from rooms.models import Room


class ExamRoomAllocation(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    allocated_students = models.IntegerField(default=0)

    is_auto = models.BooleanField(default=True)

    class Meta:
        unique_together = ('exam', 'room')

    def __str__(self):
        return f"{self.exam} -> {self.room}"