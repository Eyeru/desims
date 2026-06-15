from django.db import models
from exams.models import Exam
from rooms.models import Room
from staff.models import Staff


class InvigilationAssignment(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)

    is_auto = models.BooleanField(default=True)

    class Meta:
        unique_together = ("exam", "room", "staff")

    def __str__(self):
        return f"{self.exam} - {self.room} - {self.staff}"
    

class StaffWorkload(models.Model):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE)

    total_assignments = models.IntegerField(default=0)
    current_semester = models.IntegerField(default=0)

    last_updated = models.DateTimeField(auto_now=True)