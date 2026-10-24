"""Build the polished assignment PDF from report/report_source.md."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "report" / "report_source.md"
OUTPUT = ROOT / "deliverables" / "CSE513_Assignment1_Report.pdf"


def inline_markup(text: str) -> str:
    escaped = html.escape(text.strip())
    escaped = re.sub(
        r"\[([^]]+)\]\((https?://[^)]+)\)",
        r'<link href="\2" color="#2563EB"><u>\1</u></link>',
        escaped,
    )
    escaped = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    return escaped.replace("  ", "<br/>")


class ReportDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=26 * mm,
            bottomMargin=18 * mm,
            title="CSE513 Assignment 1 - CPU Scheduling Simulator",
            author="CPU Scheduling Simulator Project",
        )
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        self.addPageTemplates(PageTemplate(id="report", frames=frame))


class HeaderFooterCanvas(canvas.Canvas):
    """Draw repeated furniture after page content so split flowables cannot cover it."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_header_footer()
            super().showPage()
        super().save()

    def _draw_header_footer(self):
        self.saveState()
        width, height = A4
        page_number = self.getPageNumber()
        if page_number > 1:
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(18 * mm, height - 11 * mm, "CSE513 Assignment 1 · CPU Scheduling Simulator")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.line(18 * mm, height - 13 * mm, width - 18 * mm, height - 13 * mm)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawRightString(width - 18 * mm, 10 * mm, f"Page {page_number}")
        self.restoreState()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=31, textColor=colors.HexColor("#0F172A"), alignment=TA_CENTER, spaceAfter=16))
styles.add(ParagraphStyle(name="CoverUrl", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11, leading=16, textColor=colors.HexColor("#B45309"), alignment=TA_CENTER, backColor=colors.HexColor("#FFF7ED"), borderColor=colors.HexColor("#FDBA74"), borderWidth=0.8, borderPadding=10, spaceAfter=14))
styles.add(ParagraphStyle(name="H1Custom", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=22, textColor=colors.HexColor("#1E3A8A"), spaceBefore=10, spaceAfter=8))
styles.add(ParagraphStyle(name="H2Custom", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13.5, leading=18, textColor=colors.HexColor("#1D4ED8"), spaceBefore=10, spaceAfter=6))
styles.add(ParagraphStyle(name="H3Custom", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=colors.HexColor("#0F172A"), spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name="BodyCustom", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13.2, textColor=colors.HexColor("#1E293B"), alignment=TA_LEFT, spaceAfter=6))
styles.add(ParagraphStyle(name="CodeCustom", parent=styles["Code"], fontName="Courier", fontSize=7.8, leading=11, textColor=colors.HexColor("#E2E8F0"), backColor=colors.HexColor("#0F172A"), borderPadding=8, spaceAfter=8))
styles.add(ParagraphStyle(name="TableCell", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.5, leading=9.5, textColor=colors.HexColor("#1E293B")))
styles.add(ParagraphStyle(name="TableHeader", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.5, leading=9.5, textColor=colors.white))


def markdown_table(lines: list[str]) -> Table:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    rows = [rows[0]] + rows[2:]
    data = []
    for row_index, row in enumerate(rows):
        style = styles["TableHeader"] if row_index == 0 else styles["TableCell"]
        data.append([Paragraph(inline_markup(cell), style) for cell in row])
    column_count = len(data[0])
    first_width = 31 * mm if column_count >= 4 else 55 * mm
    remaining = (174 * mm - first_width) / max(1, column_count - 1)
    table = Table(data, colWidths=[first_width] + [remaining] * (column_count - 1), repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def build_story(source: str):
    lines = source.splitlines()
    story = []
    paragraph_buffer: list[str] = []
    list_buffer: list[str] = []
    code_buffer: list[str] = []
    in_code = False
    first_heading = True
    index = 0

    def flush_paragraph():
        if paragraph_buffer:
            story.append(Paragraph(inline_markup(" ".join(paragraph_buffer)), styles["BodyCustom"]))
            paragraph_buffer.clear()

    def flush_list():
        if list_buffer:
            items = [ListItem(Paragraph(inline_markup(item), styles["BodyCustom"]), leftIndent=10) for item in list_buffer]
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=18, bulletColor=colors.HexColor("#2563EB")))
            story.append(Spacer(1, 4))
            list_buffer.clear()

    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code:
                story.append(Paragraph("<br/>".join(html.escape(line) for line in code_buffer), styles["CodeCustom"]))
                code_buffer.clear()
            in_code = not in_code
            index += 1
            continue
        if in_code:
            code_buffer.append(raw)
            index += 1
            continue
        if stripped == "<!-- PAGE_BREAK -->":
            flush_paragraph()
            flush_list()
            story.append(PageBreak())
            index += 1
            continue
        if stripped.startswith("|") and index + 1 < len(lines) and lines[index + 1].strip().startswith("|"):
            flush_paragraph()
            flush_list()
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            story.append(KeepTogether([markdown_table(table_lines), Spacer(1, 7)]))
            continue
        if stripped.startswith("# "):
            flush_paragraph()
            flush_list()
            if first_heading:
                story.append(Spacer(1, 28 * mm))
                story.append(Paragraph(inline_markup(stripped[2:]), styles["CoverTitle"]))
                story.append(HRFlowable(width="62%", thickness=2, color=colors.HexColor("#2563EB"), spaceBefore=2, spaceAfter=16, hAlign="CENTER"))
                first_heading = False
            else:
                story.append(Paragraph(inline_markup(stripped[2:]), styles["H1Custom"]))
            index += 1
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            flush_list()
            story.append(Paragraph(inline_markup(stripped[3:]), styles["H1Custom"]))
            index += 1
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            flush_list()
            story.append(KeepTogether([Paragraph(inline_markup(stripped[4:]), styles["H2Custom"])]))
            index += 1
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            list_buffer.append(stripped[2:])
            index += 1
            continue
        if not stripped:
            flush_paragraph()
            flush_list()
            index += 1
            continue
        if "Public website URL:" in stripped:
            flush_paragraph()
            flush_list()
            story.append(Paragraph(inline_markup(stripped), styles["CoverUrl"]))
            index += 1
            continue
        paragraph_buffer.append(stripped)
        index += 1

    flush_paragraph()
    flush_list()
    return story


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    source = SOURCE.read_text(encoding="utf-8")
    doc = ReportDocTemplate(str(OUTPUT))
    doc.build(build_story(source), canvasmaker=HeaderFooterCanvas)
    print(OUTPUT)


if __name__ == "__main__":
    main()

