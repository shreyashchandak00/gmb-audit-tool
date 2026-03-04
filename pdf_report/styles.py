from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Brand colors
PRIMARY = HexColor('#1a56db')
PRIMARY_LIGHT = HexColor('#3b82f6')
SECONDARY = HexColor('#6366f1')
ACCENT = HexColor('#0ea5e9')
SUCCESS = HexColor('#22c55e')
WARNING = HexColor('#f97316')
DANGER = HexColor('#ef4444')
INFO = HexColor('#3b82f6')

WHITE = HexColor('#ffffff')
BLACK = HexColor('#000000')
TEXT_DARK = HexColor('#1e293b')
TEXT_MUTED = HexColor('#64748b')
TEXT_LIGHT = HexColor('#94a3b8')
BG_LIGHT = HexColor('#f8fafc')
BG_CARD = HexColor('#f1f5f9')
BORDER = HexColor('#e2e8f0')

SEVERITY_COLORS = {
    'critical': DANGER,
    'warning': WARNING,
    'info': INFO,
}

GRADE_COLORS = {
    'A': SUCCESS,
    'B': HexColor('#84cc16'),
    'C': HexColor('#eab308'),
    'D': WARNING,
    'F': DANGER,
}

# Paragraph styles
STYLES = {
    'title': ParagraphStyle(
        'Title',
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=6,
    ),
    'subtitle': ParagraphStyle(
        'Subtitle',
        fontName='Helvetica',
        fontSize=12,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
        spaceAfter=20,
    ),
    'heading': ParagraphStyle(
        'Heading',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=PRIMARY,
        spaceBefore=16,
        spaceAfter=8,
    ),
    'subheading': ParagraphStyle(
        'Subheading',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=TEXT_DARK,
        spaceBefore=10,
        spaceAfter=4,
    ),
    'body': ParagraphStyle(
        'Body',
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_DARK,
        leading=14,
        spaceAfter=6,
    ),
    'body_muted': ParagraphStyle(
        'BodyMuted',
        fontName='Helvetica',
        fontSize=9,
        textColor=TEXT_MUTED,
        leading=13,
        spaceAfter=4,
    ),
    'label': ParagraphStyle(
        'Label',
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=TEXT_MUTED,
        spaceAfter=2,
    ),
    'value': ParagraphStyle(
        'Value',
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_DARK,
        spaceAfter=6,
    ),
    'score_text': ParagraphStyle(
        'ScoreText',
        fontName='Helvetica-Bold',
        fontSize=36,
        alignment=TA_CENTER,
    ),
    'grade_text': ParagraphStyle(
        'GradeText',
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=4,
    ),
    'issue_title': ParagraphStyle(
        'IssueTitle',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=TEXT_DARK,
        spaceAfter=4,
    ),
    'recommendation': ParagraphStyle(
        'Recommendation',
        fontName='Helvetica',
        fontSize=9,
        textColor=TEXT_DARK,
        leading=13,
        leftIndent=12,
        spaceAfter=8,
    ),
    'footer': ParagraphStyle(
        'Footer',
        fontName='Helvetica',
        fontSize=8,
        textColor=TEXT_LIGHT,
        alignment=TA_CENTER,
    ),
    'checklist': ParagraphStyle(
        'Checklist',
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_DARK,
        leading=16,
        leftIndent=20,
        spaceAfter=4,
    ),
    'priority_header': ParagraphStyle(
        'PriorityHeader',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=TEXT_DARK,
        spaceBefore=14,
        spaceAfter=6,
    ),
}
