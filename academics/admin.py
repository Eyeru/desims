from django.contrib import admin
from .models import AcademicYear, Semester, ExamPeriod, Holiday, ExamSession

admin.site.register(AcademicYear)
admin.site.register(Semester)
admin.site.register(ExamPeriod)
admin.site.register(Holiday)
admin.site.register(ExamSession)