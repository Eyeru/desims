# dashboard/forms.py

from django import forms
from academics.models import AcademicYear


class PlanGenerationForm(forms.Form):

    academic_year = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all()
    )

    year_level = forms.IntegerField()

    semester = forms.IntegerField()

    program_type = forms.ChoiceField(
        choices=[
            ("REGULAR", "Regular"),
            ("EXTENSION", "Extension")
        ]
    )

    student_count = forms.IntegerField()

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )