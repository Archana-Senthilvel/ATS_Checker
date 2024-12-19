import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

def create_pdf_report(resume_text, analysis_result, overall_score, profile_info):
    """Generate PDF report using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12
    )

    # Add content
    story.append(Paragraph("Resume Analysis Report", title_style))
    story.append(Spacer(1, 12))

    # Profile Section
    story.append(Paragraph("1. Profile Information", heading_style))
    story.append(Paragraph(f"Name: {profile_info.get('name', 'Not found')}", normal_style))
    story.append(Paragraph(f"Email: {profile_info.get('email', 'Not found')}", normal_style))
    story.append(Paragraph(f"Phone: {profile_info.get('phone', 'Not found')}", normal_style))
    story.append(Spacer(1, 12))

    # Analysis Results
    story.append(Paragraph("2. Analysis Results", heading_style))
    story.append(Paragraph(analysis_result.replace('\n', '<br/>'), normal_style))
    story.append(Spacer(1, 12))

    # Overall Score
    story.append(Paragraph("3. Overall ATS Score", heading_style))
    story.append(Paragraph(f"Score: {overall_score}", heading_style))
    story.append(Spacer(1, 12))

    # Generation Info
    story.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles['Normal']
    ))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer