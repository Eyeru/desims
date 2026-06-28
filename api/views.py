from rest_framework.decorators import api_view
from rest_framework.response import Response

from courses.models import Course
from rooms.models import Room
from staff.models import Staff
from scheduling.models import ExamSchedule


@api_view(["GET"])
def dashboard(request):

    data = {
        "courses": Course.objects.count(),
        "rooms": Room.objects.count(),
        "staff": Staff.objects.count(),
        "schedules": ExamSchedule.objects.count(),
    }

    return Response(data)
