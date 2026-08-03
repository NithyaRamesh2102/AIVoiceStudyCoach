"""
Generates downloadable PDF reports (study plan, mock test results,
progress report) using reportlab.
"""
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def build_study_plan_pdf(title: str, tasks: list[dict]) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 25 * mm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, y, title)
    y -= 12 * mm

    c.setFont("Helvetica", 10)
    for task in tasks:
        line = f"{task['day']:%Y-%m-%d}  |  {task['subject']:<15}  |  {task['topic']}  ({task['duration_minutes']} min)"
        if y < 20 * mm:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 20 * mm
        c.drawString(20 * mm, y, line[:110])
        y -= 6 * mm

    c.save()
    buffer.seek(0)
    return buffer.read()


def build_progress_report_pdf(summary: dict) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 25 * mm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, y, "Progress Report")
    y -= 12 * mm

    c.setFont("Helvetica", 11)
    c.drawString(20 * mm, y, f"Total minutes studied: {summary['total_minutes_studied']}")
    y -= 8 * mm
    c.drawString(20 * mm, y, f"Average quiz accuracy: {summary.get('average_quiz_accuracy')}")
    y -= 8 * mm
    c.drawString(20 * mm, y, f"Current streak: {summary['streak_days']} day(s)")
    y -= 12 * mm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(20 * mm, y, "By subject:")
    y -= 8 * mm
    c.setFont("Helvetica", 10)
    for row in summary.get("subjects_breakdown", []):
        c.drawString(
            22 * mm, y, f"- {row['subject']}: {row['minutes']} min, {row['topics']} topics"
        )
        y -= 6 * mm

    c.save()
    buffer.seek(0)
    return buffer.read()
