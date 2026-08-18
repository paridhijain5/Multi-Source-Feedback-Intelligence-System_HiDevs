# Multi-Source Feedback Intelligence System

A complete Python-based analytics pipeline that aggregates app feedback from multiple sources, analyzes sentiment, detects trends, prioritizes recurring issues, and produces downloadable PDF reports and a Streamlit dashboard.

## Features

- Google Play reviews fetcher with mock fallback
- App Store RSS reviews fetcher with mock fallback
- CSV ingestion for local review files
- Sentiment analysis using VADER
- Trend detection over rolling windows
- Issue prioritization by frequency and negative sentiment
- Dashboard with filters and live charts
- Weekly PDF report generation
- Graceful failure handling with mock data fallback

## Project Structure

```text
.
├── analysis/
│   ├── issue_prioritizer.py
│   ├── sentiment_analyzer.py
│   └── trend_detector.py
├── fetchers/
│   ├── app_store_fetcher.py
│   ├── csv_fetcher.py
│   ├── google_play_fetcher.py
│   └── __init__.py
├── reports/
│   └── pdf_generator.py
├── config.py
├── dashboard.py
├── main.py
├── requirements.txt
├── README.md
├── data/
│   └── sample_feedback.csv
└── output/
```

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install project dependencies:

```bash
pip install -r requirements.txt
```

3. Add environment variables (optional):

Create a `.env` file at the project root with values such as:

```env
GOOGLE_PLAY_PACKAGE=com.example.feedbackapp
APP_STORE_APP_ID=id284882215
CSV_PATH=data/sample_feedback.csv
REPORT_PATH=output/weekly_report.pdf
ENABLED_SOURCES=google_play,app_store,csv
```

If you do not provide credentials or app IDs, the app will automatically fall back to mock/demo data so the pipeline still runs end-to-end.

## Running the Pipeline

Execute the main orchestrator to fetch, analyze, and save aggregated data:

```bash
python main.py
```

This will generate:

- `output/aggregated_feedback.csv`
- `output/aggregated_feedback.json`

## Launching the Dashboard

Start the Streamlit application:

```bash
streamlit run dashboard.py
```

Then open the local URL shown in the terminal (typically http://localhost:8501).

## Generating PDF Reports

The PDF is generated from the dashboard button or can be triggered programmatically:

```python
from reports.pdf_generator import WeeklyReportGenerator
from main import load_aggregated_reviews

reviews = load_aggregated_reviews()
issues = []
report_path = WeeklyReportGenerator("output/weekly_report.pdf").generate(reviews, issues)
print(report_path)
```

## Notes

- The app intentionally degrades gracefully when APIs fail or rate limits occur.
- If a live source is unavailable, it switches to mock sample data so the dashboard and PDF report remain demoable.
- The dashboard supports date range, source, and sentiment filters in real time.


## Demo
[demo link](https://drive.google.com/file/d/1zQjwWfILdoc6RWzYKccGI86iKraBewvh/view?usp=sharing)
