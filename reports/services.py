from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def generate_invigilation_pdf(exam_schedule, output_path):

    doc = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()
    elements = []

    exam = exam_schedule.exam

    # Header
    elements.append(Paragraph("EXAM INVIGILATION SHEET", styles['Title']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Course: {exam.course.title}", styles['Normal']))
    elements.append(Paragraph(f"Date: {exam_schedule.date}", styles['Normal']))
    elements.append(Paragraph(f"Session: {exam_schedule.session.name}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Room allocations
    allocations = exam.examroomallocation_set.all()

    for alloc in allocations:
        room = alloc.room

        elements.append(Paragraph(f"Room: {room.name}", styles['Heading3']))
        elements.append(Paragraph(f"Students: {alloc.allocated_students}", styles['Normal']))

        # Invigilators
        invigilators = []

        invigs = alloc.exam.invigilationassignment_set.filter(room=room)

        for i in invigs:
            invigilators.append(i.staff.first_name + " " + i.staff.last_name)

        data = [["Invigilators"]]
        for name in invigilators:
            data.append([name])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 12))

    doc.build(elements)

    return output_path