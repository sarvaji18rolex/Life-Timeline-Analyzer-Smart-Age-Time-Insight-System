"""
utils/pdf_generator.py
Generates a downloadable PDF report for the Life Timeline Dashboard.
Uses ReportLab for PDF creation.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io


# ── Color Palette ─────────────────────────────────────────────────────────────
DARK_BG     = colors.HexColor('#0d1117')
ACCENT_CYAN = colors.HexColor('#00d4ff')
ACCENT_GOLD = colors.HexColor('#f0c040')
LIGHT_TEXT  = colors.HexColor('#e6edf3')
MID_GRAY    = colors.HexColor('#8b949e')
CARD_BG     = colors.HexColor('#161b22')
GREEN       = colors.HexColor('#3fb950')


def generate_pdf_report(username: str, email: str, dob: str, stats: dict) -> bytes:
    """
    Generate a styled PDF life-timeline report.
    Returns raw PDF bytes.
    """
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm,   bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=ACCENT_CYAN,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=MID_GRAY,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=ACCENT_GOLD,
        spaceBefore=14,
        spaceAfter=6,
        fontName='Helvetica-Bold',
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        textColor=LIGHT_TEXT,
        spaceAfter=4,
    )
    insight_style = ParagraphStyle(
        'Insight',
        parent=styles['Normal'],
        fontSize=10,
        textColor=LIGHT_TEXT,
        spaceAfter=3,
        leftIndent=10,
    )

    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph("✦ Life Timeline Report ✦", title_style))
    story.append(Paragraph(f"Generated for {username}", subtitle_style))
    story.append(Paragraph(
        f"Report Date: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_CYAN, spaceAfter=12))

    # ── User Info ─────────────────────────────────────────────────────────────
    story.append(Paragraph("👤 Personal Information", section_style))
    user_data = [
        ['Username',       username],
        ['Email',          email],
        ['Date of Birth',  dob],
        ['Report Time',    datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
    ]
    user_table = Table(user_data, colWidths=[5*cm, 12*cm])
    user_table.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, -1), CARD_BG),
        ('TEXTCOLOR',   (0, 0), (0, -1), ACCENT_CYAN),
        ('TEXTCOLOR',   (1, 0), (1, -1), LIGHT_TEXT),
        ('FONTNAME',    (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 10),
        ('GRID',        (0, 0), (-1, -1), 0.5, MID_GRAY),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [CARD_BG, DARK_BG]),
        ('PADDING',     (0, 0), (-1, -1), 8),
    ]))
    story.append(user_table)

    # ── Age Details ───────────────────────────────────────────────────────────
    story.append(Paragraph("🎂 Age Details", section_style))
    age = stats['age']
    totals = stats['totals']
    age_data = [
        ['Metric',             'Value'],
        ['Age',                f"{age['years']} years, {age['months']} months, {age['days']} days"],
        ['Total Days Lived',   f"{totals['days']:,} days"],
        ['Total Weeks Lived',  f"{totals['weeks']:,} weeks"],
        ['Total Hours Lived',  f"{totals['hours']:,} hours"],
        ['Total Minutes Lived',f"{totals['minutes']:,} minutes"],
        ['Total Seconds Lived',f"{totals['seconds']:,} seconds"],
    ]
    age_table = Table(age_data, colWidths=[7*cm, 10*cm])
    age_table.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), ACCENT_CYAN),
        ('TEXTCOLOR',   (0, 0), (-1, 0), DARK_BG),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND',  (0, 1), (-1, -1), CARD_BG),
        ('TEXTCOLOR',   (0, 1), (0, -1), ACCENT_CYAN),
        ('TEXTCOLOR',   (1, 1), (1, -1), LIGHT_TEXT),
        ('FONTSIZE',    (0, 0), (-1, -1), 10),
        ('GRID',        (0, 0), (-1, -1), 0.5, MID_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CARD_BG, DARK_BG]),
        ('PADDING',     (0, 0), (-1, -1), 8),
    ]))
    story.append(age_table)

    # ── Life Progress ─────────────────────────────────────────────────────────
    story.append(Paragraph("⏳ Life Progress", section_style))
    prog = stats['life_progress']
    prog_data = [
        ['Metric',                'Value'],
        ['Life Completed',        f"{prog['pct_complete']}%"],
        ['Remaining Years',       f"~{prog['remaining_years']} years"],
        ['Remaining Days',        f"~{prog['remaining_days']:,} days"],
        ['Average Lifespan Used', f"{prog['avg_lifespan']} years"],
    ]
    prog_table = Table(prog_data, colWidths=[7*cm, 10*cm])
    prog_table.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), ACCENT_GOLD),
        ('TEXTCOLOR',   (0, 0), (-1, 0), DARK_BG),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND',  (0, 1), (-1, -1), CARD_BG),
        ('TEXTCOLOR',   (0, 1), (0, -1), ACCENT_GOLD),
        ('TEXTCOLOR',   (1, 1), (1, -1), LIGHT_TEXT),
        ('FONTSIZE',    (0, 0), (-1, -1), 10),
        ('GRID',        (0, 0), (-1, -1), 0.5, MID_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CARD_BG, DARK_BG]),
        ('PADDING',     (0, 0), (-1, -1), 8),
    ]))
    story.append(prog_table)

    # ── Fun Bio Stats ─────────────────────────────────────────────────────────
    story.append(Paragraph("🧬 Fun Life Statistics", section_style))
    fun = stats['fun_stats']
    fun_data = [
        ['Statistic',           'Estimated Value'],
        ['Heartbeats',          f"{fun['heartbeats']:,}"],
        ['Breaths Taken',       f"{fun['breaths']:,}"],
        ['Sleep Time',          f"{fun['sleep_days']:,} days ({fun['sleep_years']} years)"],
        ['Steps Walked',        f"{fun['steps']:,} steps (~{fun['steps_km']:,} km)"],
    ]
    fun_table = Table(fun_data, colWidths=[7*cm, 10*cm])
    fun_table.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), GREEN),
        ('TEXTCOLOR',   (0, 0), (-1, 0), DARK_BG),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND',  (0, 1), (-1, -1), CARD_BG),
        ('TEXTCOLOR',   (0, 1), (0, -1), GREEN),
        ('TEXTCOLOR',   (1, 1), (1, -1), LIGHT_TEXT),
        ('FONTSIZE',    (0, 0), (-1, -1), 10),
        ('GRID',        (0, 0), (-1, -1), 0.5, MID_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [CARD_BG, DARK_BG]),
        ('PADDING',     (0, 0), (-1, -1), 8),
    ]))
    story.append(fun_table)

    # ── Insights ──────────────────────────────────────────────────────────────
    story.append(Paragraph("💡 Time Insights", section_style))
    for insight in stats['insights']:
        story.append(Paragraph(insight, insight_style))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_GRAY))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Generated by Life Timeline Analyzer • Your time, visualized.",
        subtitle_style
    ))

    doc.build(story)
    return buffer.getvalue()
