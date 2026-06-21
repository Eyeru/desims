from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

from scheduling.models import ExamSchedule
from semester_setup.models import SemesterPlan

from .serializers import SemesterPlanSerializer, ExamScheduleSerializer


@api_view(["GET"])
def plans(request):
    qs = SemesterPlan.objects.all().order_by("-id")
    return Response(SemesterPlanSerializer(qs, many=True).data)


@api_view(["GET"])
def plan_detail(request, plan_id):
    plan = SemesterPlan.objects.get(id=plan_id)
    schedules = ExamSchedule.objects.filter(plan=plan)

    return Response({
        "plan": SemesterPlanSerializer(plan).data,
        "schedules": ExamScheduleSerializer(schedules, many=True).data
    })