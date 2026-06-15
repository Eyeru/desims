from django.contrib import admin
from .models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "staff_type", "is_active")
    list_filter = ("staff_type", "is_active")
    search_fields = ("first_name", "last_name")