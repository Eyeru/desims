from django.http import FileResponse
from scheduling.models import ExamSchedule
from .services import generate_invigilation_pdf
import os


def download_invigilation_sheet(request, schedule_id):

    schedule = ExamSchedule.objects.get(id=schedule_id)

    file_path = f"/tmp/invigilation_{schedule_id}.pdf"

    generate_invigilation_pdf(schedule, file_path)

    return FileResponse(open(file_path, 'rb'), content_type='application/pdf')