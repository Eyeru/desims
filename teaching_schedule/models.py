from django.db import models
from staff.models import Staff
import PyPDF2


class TeachingSchedule(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    raw_text = models.TextField()
    uploaded_file = models.FileField(upload_to="teaching_schedules/")
    created_at = models.DateTimeField(auto_now_add=True)



def extract_pdf_text(file_path):
    text = ""

    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)

        for page in reader.pages:
            text += page.extract_text() or ""

    return text