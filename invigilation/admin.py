from django.contrib import admin

from .models import InvigilationAssignment


@admin.register(InvigilationAssignment)
class InvigilationAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "staff",
        "exam_schedule",
        "is_auto",
    )

    list_filter = (
        "is_auto",
    )

    search_fields = (
        "staff__first_name",
        "staff__last_name",
    )