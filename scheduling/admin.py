from django.contrib import admin
from .models import ExamSchedule


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ("exam", "date", "session", "is_auto", "is_final")
    list_filter = ("date", "session", "is_final")
    search_fields = ("exam__course__code",)