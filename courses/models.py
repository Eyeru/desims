from django.db import models

class Course(models.Model):
    REGULAR = "REGULAR"
    EXTENSION = "EXTENSION"

    PROGRAM_TYPES = [
        (REGULAR, "Regular"),
        (EXTENSION, "Extension"),
    ]

    code = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    academic_year = models.IntegerField()
    semester = models.IntegerField()
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES)

    def __str__(self):
        return self.code