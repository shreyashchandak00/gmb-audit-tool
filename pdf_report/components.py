import math
from reportlab.platypus import Flowable
from reportlab.lib.colors import HexColor
from pdf_report.styles import (
    PRIMARY, WHITE, TEXT_DARK, TEXT_MUTED, BG_CARD, BORDER,
    SEVERITY_COLORS, GRADE_COLORS
)


class ScoreGauge(Flowable):
    """Circular score gauge showing score out of 100."""

    def __init__(self, score: int, grade: str, grade_color: str,
                 width=160, height=160):
        super().__init__()
        self.score = score
        self.grade = grade
        self.grade_color = HexColor(grade_color) if isinstance(grade_color, str) else grade_color
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        canvas = self.canv
        cx = self.width / 2
        cy = self.height / 2
        radius = min(cx, cy) - 10

        # Background circle
        canvas.setStrokeColor(BG_CARD)
        canvas.setLineWidth(12)
        canvas.circle(cx, cy, radius)

        # Score arc
        canvas.setStrokeColor(self.grade_color)
        canvas.setLineWidth(12)
        canvas.setLineCap(1)  # Round cap

        # Draw arc from 90 degrees (top) clockwise
        extent = (self.score / 100) * 360
        if extent > 0:
            canvas.arc(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                90, extent
            )

        # Score number
        canvas.setFont('Helvetica-Bold', 36)
        canvas.setFillColor(TEXT_DARK)
        canvas.drawCentredString(cx, cy + 8, str(self.score))

        # "/100" text
        canvas.setFont('Helvetica', 11)
        canvas.setFillColor(TEXT_MUTED)
        canvas.drawCentredString(cx, cy - 10, '/100')

        # Grade label
        canvas.setFont('Helvetica-Bold', 14)
        canvas.setFillColor(self.grade_color)
        canvas.drawCentredString(cx, cy - 30, f'Grade: {self.grade}')


class SeverityBadge(Flowable):
    """Colored severity badge (CRITICAL, WARNING, INFO)."""

    def __init__(self, severity: str, width=80, height=20):
        super().__init__()
        self.severity = severity
        self.color = SEVERITY_COLORS.get(severity, PRIMARY)
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        canvas = self.canv

        # Rounded rectangle background
        canvas.setFillColor(self.color)
        canvas.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=0)

        # Label text
        canvas.setFont('Helvetica-Bold', 8)
        canvas.setFillColor(WHITE)
        canvas.drawCentredString(
            self.width / 2, self.height / 2 - 3,
            self.severity.upper()
        )


class ProgressBar(Flowable):
    """Horizontal progress bar showing completeness."""

    def __init__(self, value: float, max_value: float = 100,
                 width=400, height=20, fill_color=None, label: str = ''):
        super().__init__()
        self.value = value
        self.max_value = max_value
        self.width = width
        self.height = height
        self.fill_color = fill_color or PRIMARY
        self.label = label

    def wrap(self, availWidth, availHeight):
        return self.width, self.height + 16

    def draw(self):
        canvas = self.canv

        # Label
        if self.label:
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(TEXT_MUTED)
            canvas.drawString(0, self.height + 3, self.label)

        # Background bar
        canvas.setFillColor(BG_CARD)
        canvas.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=0)

        # Fill bar
        fill_width = (self.value / self.max_value) * self.width
        if fill_width > 0:
            canvas.setFillColor(self.fill_color)
            canvas.roundRect(0, 0, fill_width, self.height, 4, fill=1, stroke=0)

        # Percentage text
        pct = int((self.value / self.max_value) * 100)
        canvas.setFont('Helvetica-Bold', 9)
        canvas.setFillColor(WHITE if fill_width > 40 else TEXT_DARK)
        text_x = fill_width / 2 if fill_width > 40 else fill_width + 8
        canvas.drawCentredString(text_x, self.height / 2 - 3, f'{pct}%')


class SectionDivider(Flowable):
    """A styled section divider line."""

    def __init__(self, width=500, color=None):
        super().__init__()
        self.width = width
        self.color = color or BORDER

    def wrap(self, availWidth, availHeight):
        return self.width, 8

    def draw(self):
        canvas = self.canv
        canvas.setStrokeColor(self.color)
        canvas.setLineWidth(1)
        canvas.line(0, 4, self.width, 4)


class StatBox(Flowable):
    """A small stat display box with label and value."""

    def __init__(self, label: str, value: str, color=None,
                 width=100, height=55):
        super().__init__()
        self.label = label
        self.value = value
        self.color = color or PRIMARY
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        canvas = self.canv

        # Background
        canvas.setFillColor(BG_CARD)
        canvas.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=0)

        # Value
        canvas.setFont('Helvetica-Bold', 16)
        canvas.setFillColor(self.color)
        canvas.drawCentredString(self.width / 2, self.height / 2 + 2, str(self.value))

        # Label
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(TEXT_MUTED)
        canvas.drawCentredString(self.width / 2, 8, self.label)
