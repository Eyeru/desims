from django.contrib import admin
from .models import SemesterPlan


@admin.register(SemesterPlan)
class SemesterPlanAdmin(admin.ModelAdmin):

    list_display = (
        "academic_year",
        "semester",
        "program_type",
        "start_date",
        "end_date",
        "is_generated"
    )

    list_filter = (
        "semester",
        "program_type",
        "is_generated"
    )
