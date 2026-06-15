from django.db import models
from exams.models import Exam
from staff.models import Staff
from rooms.models import Room


class Conflict(models.Model):
    WARNING = "WARNING"
    BLOCKER = "BLOCKER"

    SEVERITY = [
        (WARNING, "Warning"),
        (BLOCKER, "Blocker"),
    ]

    conflict_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=10, choices=SEVERITY)

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True, blank=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)

    message = models.TextField()

    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.conflict_type} - {self.severity}"