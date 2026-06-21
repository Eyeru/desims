from rest_framework import serializers
from semester_setup.models import SemesterPlan
from scheduling.models import ExamSchedule


class SemesterPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SemesterPlan
        fields = "__all__"


class ExamScheduleSerializer(serializers.ModelSerializer):
    exam_course = serializers.CharField(source="exam.course.name", read_only=True)

    class Meta:
        model = ExamSchedule
        fields = [
            "id",
            "exam",
            "exam_course",
            "date",
            "session",
            "plan",
        ]