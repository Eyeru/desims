from django.db import models
from exams.models import Exam
from academics.models import ExamSession


class ExamSchedule(models.Model):
    plan = models.ForeignKey(
        "semester_setup.SemesterPlan",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    exam = models.OneToOneField(Exam, on_delete=models.CASCADE)
    date = models.DateField()
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE)

    is_auto = models.BooleanField(default=True)
    is_final = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.exam} -> {self.date} {self.session}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["exam", "plan"],
                name="unique_exam__per_plan"
            )
        ]
