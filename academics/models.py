from django.db import models

class AcademicYear(models.Model):
    name = models.CharField(max_length=20)  # e.g. 2025/2026
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Semester(models.Model):
    FIRST = 1
    SECOND = 2

    SEMESTERS = [
        (FIRST, "First Semester"),
        (SECOND, "Second Semester"),
    ]

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    name = models.IntegerField(choices=SEMESTERS)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.academic_year} - {self.name}"


class ExamPeriod(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.academic_year}"


class Holiday(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return self.name


class ExamSession(models.Model):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"

    SESSION_TYPES = [
        (MORNING, "Morning"),
        (AFTERNOON, "Afternoon"),
    ]

    name = models.CharField(max_length=10, choices=SESSION_TYPES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.name