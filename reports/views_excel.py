from django.http import HttpResponse
from .services_excel import export_full_timetable


def download_excel(request):

    wb = export_full_timetable()

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = "attachment; filename=exam_timetable.xlsx"

    wb.save(response)

    return response