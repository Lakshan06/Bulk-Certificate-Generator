from pathlib import Path
from datetime import date
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def render_certificate(
    recipient_name: str,
    course: str | None,
    event_name: str,
    issue_date: date,
    output_path: Path,
) -> Path:
    """
    Renders a certificate as a PDF and saves it to output_path.
    Returns the path to the generated file.
    """
    # Create the PDF document
    c = canvas.Canvas(str(output_path), pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # Draw a decorative border
    margin = 50
    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(5)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin)
    
    c.setStrokeColor(colors.gold)
    c.setLineWidth(2)
    inner_margin = margin + 10
    c.rect(inner_margin, inner_margin, width - 2 * inner_margin, height - 2 * inner_margin)
    
    # Title
    c.setFont("Helvetica-Bold", 40)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2.0, height - 150, "Certificate of Completion")
    
    # Subtitle
    c.setFont("Helvetica", 18)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2.0, height - 210, "This is to certify that")
    
    # Recipient Name
    c.setFont("Helvetica-Bold", 35)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2.0, height - 280, recipient_name)
    
    # Course and Event
    c.setFont("Helvetica", 16)
    c.setFillColor(colors.black)
    course_text = f"has successfully completed the course '{course}'" if course else "has successfully participated"
    c.drawCentredString(width / 2.0, height - 340, course_text)
    
    c.setFont("Helvetica-Oblique", 16)
    c.drawCentredString(width / 2.0, height - 370, f"at {event_name}")
    
    # Date
    c.setFont("Helvetica", 14)
    date_str = issue_date.strftime("%B %d, %Y")
    c.drawString(margin + 50, margin + 50, f"Date: {date_str}")
    
    # Signature line
    c.line(width - margin - 200, margin + 70, width - margin - 50, margin + 70)
    c.drawCentredString(width - margin - 125, margin + 50, "Authorized Signature")
    
    # Save the PDF
    c.save()
    
    return output_path
