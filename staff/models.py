from django.db import models

# Create your models here.

class Staff(models.Model):
    INSTRUCTOR = "INSTRUCTOR"
    TECHNICAL_ASSISTANT = "TECH_ASSISTANT"

    STAFF_TYPES = [
        (INSTRUCTOR, "Instructor"),
        (TECHNICAL_ASSISTANT, "Technical Assistant"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"