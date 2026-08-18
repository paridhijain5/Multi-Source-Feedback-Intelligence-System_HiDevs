from __future__ import annotations

import pandas as pd
import streamlit as st

from analysis.issue_prioritizer import prioritize_issues
from analysis.trend_detector import detect_sentiment_trend
from main import load_aggregated_reviews
from reports.pdf_generator import WeeklyReportGenerator


st.set_page_config(page_title="Feedback Intelligence Dashboard", layout="wide")


def apply_dashboard_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #111827 40%, #1e293b 100%);
            color: #e2e8f0;
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stMetricContainer"] > div {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 0.8rem;
            padding: 0.75rem 1rem;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.12);
        }
        .stDataFrame {
            border-radius: 0.75rem;
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.2);
        }
        .block-container {
            max-width: 1500px;
        }
        h1, h2, h3 {
            color: #f8fafc !important;
        }
        .sidebar-content {
            background: rgba(15, 23, 42, 0.75);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_dashboard_data() -> pd.DataFrame:
    reviews = load_aggregated_reviews()
    df = pd.DataFrame(reviews)
    if df.empty:
        return pd.DataFrame(columns=["date", "source", "rating", "text", "sentiment", "sentiment_confidence"])
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def render():
    apply_dashboard_theme()

    st.title("📊 Multi-Source Feedback Intelligence")
    st.caption("Customer sentiment and recurring issue tracking across Google Play, App Store, and CSV data sources.")

    df = load_dashboard_data()
    if df.empty:
        st.warning("No feedback records available. Run the main pipeline to generate sample data.")
        return

    with st.sidebar:
        st.subheader("Filters")
        min_date = min(df["date"].dropna()).date() if not df["date"].dropna().empty else pd.Timestamp.today().date()
        max_date = max(df["date"].dropna()).date() if not df["date"].dropna().empty else pd.Timestamp.today().date()
        start_date = st.date_input("Start date", min_date)
        end_date = st.date_input("End date", max_date)

        all_sources = ["All"] + sorted(df["source"].dropna().unique().tolist())
        selected_source = st.selectbox("Source", all_sources)

        all_sentiments = ["All"] + sorted(df["sentiment"].dropna().unique().tolist())
        sentiment_filter = st.selectbox("Sentiment", all_sentiments)

    filtered = df.copy()
    if selected_source != "All":
        filtered = filtered[filtered["source"] == selected_source]
    if sentiment_filter != "All":
        filtered = filtered[filtered["sentiment"] == sentiment_filter]
    filtered = filtered[(filtered["date"] >= pd.Timestamp(start_date)) & (filtered["date"] <= pd.Timestamp(end_date))]

    metric_cols = st.columns(4)
    metrics = [
        ("Total Reviews", len(filtered), "primary"),
        ("Positive", int((filtered["sentiment"] == "positive").sum()), "positive"),
        ("Neutral", int((filtered["sentiment"] == "neutral").sum()), "neutral"),
        ("Negative", int((filtered["sentiment"] == "negative").sum()), "negative"),
    ]
    for i, (label, value, kind) in enumerate(metrics):
        with metric_cols[i]:
            st.metric(label, value)

    if filtered.empty:
        st.warning("No reviews matched the selected filters.")
        return

    trend = detect_sentiment_trend(filtered.to_dict("records"))
    st.subheader("📈 Sentiment Trend")
    if trend.get("daily") is not None and not trend["daily"].empty:
        daily = trend["daily"].copy()
        daily["date"] = pd.to_datetime(daily["date"])
        st.line_chart(daily.set_index("date")["sentiment_score"], use_container_width=True)
    else:
        st.info("Not enough data for trend chart.")
    st.caption(trend.get("summary", "No summary available."))

    issue_list = prioritize_issues(filtered.to_dict("records"))
    st.subheader("🩺 Recurring Issues")
    if issue_list:
        issue_df = pd.DataFrame(issue_list)
        priority_palette = {
            "High": "#f87171",
            "Medium": "#fbbf24",
            "Low": "#4ade80",
        }
        issue_df["priority_color"] = issue_df["priority"].map(priority_palette)
        st.dataframe(
            issue_df[["topic", "priority", "count", "negative_count", "score"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No recurring issues detected for the selected filters.")

    report_col, download_col = st.columns([2, 1])
    with report_col:
        if st.button("Generate PDF Report", use_container_width=True):
            report_path = WeeklyReportGenerator("output/weekly_report.pdf").generate(filtered.to_dict("records"), issue_list)
            st.success(f"Report generated at {report_path}")
    with download_col:
        if st.button("Download PDF", use_container_width=True):
            report_path = "output/weekly_report.pdf"
            with open(report_path, "rb") as report_file:
                st.download_button(
                    label="Download PDF",
                    data=report_file.read(),
                    file_name="weekly_report.pdf",
                    mime="application/pdf",
                    key="download_pdf",
                    use_container_width=True,
                )


if __name__ == "__main__":
    render()
