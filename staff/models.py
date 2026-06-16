from django.db import models


class Staff(models.Model):

    INSTRUCTOR = "INSTRUCTOR"
    TECHNICAL_ASSISTANT = "TECH_ASSISTANT"

    STAFF_TYPES = [
        (INSTRUCTOR, "Instructor"),
        (TECHNICAL_ASSISTANT, "Technical Assistant"),
    ]

    REGULAR = "REGULAR"
    EXTENSION = "EXTENSION"
    BOTH = "BOTH"

    PROGRAM_TYPES = [
        (REGULAR, "Regular"),
        (EXTENSION, "Extension"),
        (BOTH, "Both"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    staff_type = models.CharField(
        max_length=20,
        choices=STAFF_TYPES
    )

    program_type = models.CharField(
        max_length=20,
        choices=PROGRAM_TYPES,
        default=BOTH
    )

    department = models.CharField(
        max_length=100,
        default="Computer Science"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"