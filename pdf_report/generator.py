import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.colors import HexColor

from scraper.data_models import AuditResult, Severity
from pdf_report.styles import (
    STYLES, PRIMARY, PRIMARY_LIGHT, WHITE, TEXT_DARK, TEXT_MUTED,
    BG_CARD, BG_LIGHT, BORDER, SEVERITY_COLORS, SUCCESS, WARNING, DANGER
)
from pdf_report.components import (
    ScoreGauge, SeverityBadge, ProgressBar, SectionDivider, StatBox
)


class AuditReportGenerator:

    def generate(self, result: AuditResult, output_path: str):
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            topMargin=20 * mm,
            bottomMargin=25 * mm,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
        )

        story = []
        story += self._build_cover_page(result)
        story.append(PageBreak())
        story += self._build_business_info_page(result)
        story.append(PageBreak())
        story += self._build_issues_page(result)
        story.append(PageBreak())
        story += self._build_action_plan_page(result)

        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)

    def _add_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(HexColor('#94a3b8'))
        canvas.drawCentredString(
            doc.pagesize[0] / 2, 15 * mm,
            f"Google Maps Profile Audit Report  |  Generated {datetime.now().strftime('%B %d, %Y')}  |  Page {canvas.getPageNumber()}"
        )
        canvas.restoreState()

    def _build_cover_page(self, result: AuditResult) -> list:
        elements = []
        profile = result.profile

        # Title
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Google Maps Profile", STYLES['title']))
        elements.append(Paragraph("Audit Report", STYLES['title']))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(
            f"Generated on {result.timestamp.strftime('%B %d, %Y at %I:%M %p')}",
            STYLES['subtitle']
        ))
        elements.append(Spacer(1, 10))

        # Business name card
        biz_name = profile.name or "Unknown Business"
        biz_category = profile.category or "Not specified"
        biz_data = [
            [Paragraph(f'<b>{biz_name}</b>', STYLES['subheading']),
             Paragraph(biz_category, STYLES['body_muted'])],
        ]
        biz_table = Table(biz_data, colWidths=[300, 200])
        biz_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_CARD),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 16),
            ('RIGHTPADDING', (0, 0), (-1, -1), 16),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(biz_table)
        elements.append(Spacer(1, 30))

        # Score gauge centered
        gauge = ScoreGauge(result.score, result.grade, result.grade_color)
        gauge_table = Table([[gauge]], colWidths=[500])
        gauge_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ]))
        elements.append(gauge_table)
        elements.append(Spacer(1, 8))

        # Grade label
        elements.append(Paragraph(
            f'<b>{result.grade_label}</b>',
            STYLES['grade_text']
        ))
        elements.append(Spacer(1, 30))

        # Quick stats grid
        rating_str = f"{profile.rating:.1f}" if profile.rating else "N/A"
        reviews_str = str(profile.review_count) if profile.review_count else "0"
        photos_str = str(profile.photos_count) if profile.photos_count else "0"
        website_str = "Yes" if profile.website else "No"

        rating_color = SUCCESS if profile.rating and profile.rating >= 4.0 else WARNING if profile.rating else DANGER
        website_color = SUCCESS if profile.website else DANGER

        stat_data = [[
            StatBox("Rating", rating_str, rating_color, width=115, height=55),
            StatBox("Reviews", reviews_str, PRIMARY, width=115, height=55),
            StatBox("Photos", photos_str, PRIMARY, width=115, height=55),
            StatBox("Website", website_str, website_color, width=115, height=55),
        ]]
        stat_table = Table(stat_data, colWidths=[125, 125, 125, 125])
        stat_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(stat_table)
        elements.append(Spacer(1, 30))

        # Issues summary
        issue_summary = f"Issues Found: {len(result.issues)}"
        if result.issues:
            parts = []
            if result.critical_count:
                parts.append(f'<font color="#ef4444">{result.critical_count} Critical</font>')
            if result.warning_count:
                parts.append(f'<font color="#f97316">{result.warning_count} Warning</font>')
            if result.info_count:
                parts.append(f'<font color="#3b82f6">{result.info_count} Info</font>')
            issue_summary += f"  ({', '.join(parts)})"

        elements.append(Paragraph(issue_summary, STYLES['body']))

        return elements

    def _build_business_info_page(self, result: AuditResult) -> list:
        elements = []
        profile = result.profile

        elements.append(Paragraph("Business Information", STYLES['heading']))
        elements.append(SectionDivider())
        elements.append(Spacer(1, 12))

        # Info table
        fields = [
            ("Business Name", profile.name or "Not available"),
            ("Address", profile.address or "Not available"),
            ("Phone", profile.phone or "Not listed"),
            ("Website", profile.website or "Not listed"),
            ("Category", profile.category or "Not specified"),
            ("Rating", f"{profile.rating:.1f} / 5.0" if profile.rating else "No rating"),
            ("Reviews", str(profile.review_count) if profile.review_count else "No reviews"),
            ("Photos", str(profile.photos_count) if profile.photos_count else "No photos"),
        ]

        if profile.description:
            desc_preview = profile.description[:150]
            if len(profile.description) > 150:
                desc_preview += "..."
            fields.append(("Description", desc_preview))
        else:
            fields.append(("Description", "No description available"))

        table_data = []
        for label, value in fields:
            table_data.append([
                Paragraph(f'<b>{label}</b>', STYLES['label']),
                Paragraph(value, STYLES['value']),
            ])

        info_table = Table(table_data, colWidths=[120, 380])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), WHITE),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))

        # Business hours
        elements.append(Paragraph("Business Hours", STYLES['subheading']))
        elements.append(Spacer(1, 6))

        if profile.hours:
            hours_data = []
            for h in profile.hours:
                hours_data.append([
                    Paragraph(f'<b>{h.day}</b>', STYLES['body']),
                    Paragraph(h.hours, STYLES['body']),
                ])
            hours_table = Table(hours_data, colWidths=[120, 380])
            hours_table.setStyle(TableStyle([
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER),
            ]))
            elements.append(hours_table)
        else:
            elements.append(Paragraph(
                "No business hours listed on profile.",
                STYLES['body_muted']
            ))

        elements.append(Spacer(1, 24))

        # Profile completeness bar
        elements.append(Paragraph("Profile Completeness", STYLES['subheading']))
        elements.append(Spacer(1, 8))

        total_fields = 9  # name, address, phone, website, category, rating, reviews, photos, description, hours
        filled = sum([
            bool(profile.name),
            bool(profile.address),
            bool(profile.phone),
            bool(profile.website),
            bool(profile.category),
            profile.rating is not None,
            profile.review_count is not None and profile.review_count > 0,
            profile.photos_count is not None and profile.photos_count > 0,
            bool(profile.description),
            bool(profile.hours),
        ])
        completeness = (filled / 10) * 100

        color = SUCCESS if completeness >= 80 else WARNING if completeness >= 60 else DANGER
        bar = ProgressBar(completeness, 100, width=480, height=18, fill_color=color)
        elements.append(bar)

        return elements

    def _build_issues_page(self, result: AuditResult) -> list:
        elements = []

        elements.append(Paragraph("Audit Findings", STYLES['heading']))
        elements.append(SectionDivider())
        elements.append(Spacer(1, 12))

        if not result.issues:
            elements.append(Paragraph(
                "No issues found! Your Google Maps profile is in excellent shape.",
                STYLES['body']
            ))
            return elements

        for issue in result.issues:
            issue_block = []

            # Severity badge + title row
            badge = SeverityBadge(issue.severity.value, width=70, height=18)
            title_data = [[
                badge,
                Paragraph(f'<b>{issue.title}</b>', STYLES['issue_title']),
                Paragraph(f'-{issue.points_deducted} pts', STYLES['body_muted']),
            ]]
            title_table = Table(title_data, colWidths=[80, 340, 60])
            title_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ]))
            issue_block.append(title_table)
            issue_block.append(Spacer(1, 4))

            # Issue description
            issue_block.append(Paragraph(issue.description, STYLES['body']))
            issue_block.append(Spacer(1, 4))

            # Recommendation
            issue_block.append(Paragraph(
                f'<b>Recommendation:</b>', STYLES['label']
            ))
            issue_block.append(Paragraph(issue.recommendation, STYLES['recommendation']))
            issue_block.append(SectionDivider())
            issue_block.append(Spacer(1, 8))

            elements.append(KeepTogether(issue_block))

        return elements

    def _build_action_plan_page(self, result: AuditResult) -> list:
        elements = []

        elements.append(Paragraph("Recommended Action Plan", STYLES['heading']))
        elements.append(SectionDivider())
        elements.append(Spacer(1, 12))

        # Group issues by priority
        critical = [i for i in result.issues if i.severity == Severity.CRITICAL]
        warnings = [i for i in result.issues if i.severity == Severity.WARNING]
        info = [i for i in result.issues if i.severity == Severity.INFO]

        if critical:
            elements.append(Paragraph(
                '<font color="#ef4444">Priority 1 - Do Immediately</font>',
                STYLES['priority_header']
            ))
            for issue in critical:
                elements.append(Paragraph(
                    f'\u2610  {issue.title}',
                    STYLES['checklist']
                ))
                elements.append(Paragraph(
                    issue.recommendation[:200] + ('...' if len(issue.recommendation) > 200 else ''),
                    STYLES['body_muted']
                ))
            elements.append(Spacer(1, 12))

        if warnings:
            elements.append(Paragraph(
                '<font color="#f97316">Priority 2 - Address This Week</font>',
                STYLES['priority_header']
            ))
            for issue in warnings:
                elements.append(Paragraph(
                    f'\u2610  {issue.title}',
                    STYLES['checklist']
                ))
                elements.append(Paragraph(
                    issue.recommendation[:200] + ('...' if len(issue.recommendation) > 200 else ''),
                    STYLES['body_muted']
                ))
            elements.append(Spacer(1, 12))

        if info:
            elements.append(Paragraph(
                '<font color="#3b82f6">Priority 3 - Ongoing Improvements</font>',
                STYLES['priority_header']
            ))
            for issue in info:
                elements.append(Paragraph(
                    f'\u2610  {issue.title}',
                    STYLES['checklist']
                ))
                elements.append(Paragraph(
                    issue.recommendation[:200] + ('...' if len(issue.recommendation) > 200 else ''),
                    STYLES['body_muted']
                ))
            elements.append(Spacer(1, 12))

        if not result.issues:
            elements.append(Paragraph(
                "Your profile is in great shape! Keep up the good work by:",
                STYLES['body']
            ))
            elements.append(Paragraph("\u2610  Regularly responding to new reviews", STYLES['checklist']))
            elements.append(Paragraph("\u2610  Posting Google updates weekly", STYLES['checklist']))
            elements.append(Paragraph("\u2610  Adding fresh photos monthly", STYLES['checklist']))
            elements.append(Paragraph("\u2610  Keeping business hours updated", STYLES['checklist']))

        elements.append(Spacer(1, 40))
        elements.append(SectionDivider())
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            "This report was generated by Google Maps Profile Audit Tool.",
            STYLES['footer']
        ))
        elements.append(Paragraph(
            "For best results, review and update your profile regularly.",
            STYLES['footer']
        ))

        return elements
