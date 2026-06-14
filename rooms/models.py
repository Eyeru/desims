from django.db import models

# Create your models here.

class Room(models.Model):
    CLASSROOM = "CLASSROOM"
    HALL = "HALL"

    ROOM_TYPES = [
        (CLASSROOM, "Classroom"),
        (HALL, "Hall"),
    ]

    name = models.CharField(max_length=50)
    building = models.CharField(max_length=100)
    physical_capacity = models.IntegerField()
    exam_capacity = models.IntegerField()
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)

    def __str__(self):
        return self.name