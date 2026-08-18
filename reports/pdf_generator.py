from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from analysis.trend_detector import detect_sentiment_trend


class WeeklyReportGenerator:
    def __init__(self, output_path: str | Path = "output/weekly_report.pdf"):
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def _plot_trend(self, reviews: list[dict[str, Any]]) -> str:
        summary = detect_sentiment_trend(reviews)
        daily = summary.get("daily")
        chart_path = self.output_path.parent / "sentiment_trend.png"

        if daily is not None and not daily.empty:
            plt.figure(figsize=(7, 4))
            plt.plot(daily["date"], daily["sentiment_score"], color="#1d4ed8", marker="o", linewidth=2.5)
            plt.axhline(0, color="#64748b", linestyle="--", linewidth=1)
            plt.fill_between(daily["date"], daily["sentiment_score"], 0, alpha=0.15, color="#60a5fa")
            plt.title("Sentiment Trend", fontsize=12, weight="bold")
            plt.xlabel("Date")
            plt.ylabel("Average score")
            plt.grid(alpha=0.25)
            plt.tight_layout()
            plt.savefig(chart_path)
            plt.close()
        else:
            plt.figure(figsize=(7, 4))
            plt.bar(["No data"], [0], color="#dbeafe")
            plt.title("Sentiment Trend", fontsize=12, weight="bold")
            plt.tight_layout()
            plt.savefig(chart_path)
            plt.close()
        return str(chart_path)

    def generate(self, reviews: list[dict[str, Any]], issues: list[dict[str, Any]] | None = None) -> str:
        if not reviews:
            return str(self.output_path)

        summary = detect_sentiment_trend(reviews)
        issues = issues or []
        doc = SimpleDocTemplate(str(self.output_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=8,
        )
        section_style = ParagraphStyle(
            "SectionStyle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=colors.HexColor("#1d4ed8"),
            spaceBefore=10,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "BodyStyle",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#334155"),
            leading=14,
        )
        story = []

        story.append(Paragraph("Weekly Feedback Intelligence Report", title_style))
        story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", body_style))
        story.append(Paragraph(f"Trend: <b>{summary.get('trend', 'stable').title()}</b> | Delta: {summary.get('delta', 0.0)}", body_style))
        story.append(Spacer(1, 12))

        chart_path = self._plot_trend(reviews)
        story.append(Paragraph("Sentiment Trend Overview", section_style))
        story.append(Image(chart_path, width=480, height=250))
        story.append(Spacer(1, 12))

        if issues:
            issue_rows = [["Topic", "Priority", "Count", "Negative Count"]]
            for item in issues[:5]:
                issue_rows.append([
                    item.get("topic", "-"),
                    item.get("priority", "Low"),
                    item.get("count", 0),
                    item.get("negative_count", 0),
                ])
            table = Table(issue_rows, colWidths=[160, 100, 80, 110])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]))
            story.append(Paragraph("Top Recurring Issues", section_style))
            story.append(table)
            story.append(Spacer(1, 14))

        summary_data = [
            ["Metric", "Value"],
            ["Total reviews", str(len(reviews))],
            ["Positive", str(sum(1 for entry in reviews if entry.get("sentiment") == "positive"))],
            ["Neutral", str(sum(1 for entry in reviews if entry.get("sentiment") == "neutral"))],
            ["Negative", str(sum(1 for entry in reviews if entry.get("sentiment") == "negative"))],
        ]
        summary_table = Table(summary_data, colWidths=[180, 200])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(Paragraph("Summary", section_style))
        story.append(summary_table)

        doc.build(story)
        return str(self.output_path)
