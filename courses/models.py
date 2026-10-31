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
    year_level = models.IntegerField()
    semester = models.IntegerField()
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES)
    is_department_owned = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["code", "program_type", "year_level", "semester"],
                name="unique_course_offering",
            )
        ]
