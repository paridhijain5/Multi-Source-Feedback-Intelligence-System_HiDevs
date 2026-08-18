from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from analysis.issue_prioritizer import prioritize_issues
from analysis.sentiment_analyzer import analyze_reviews
from analysis.trend_detector import detect_sentiment_trend
from config import CSV_PATH, DATA_DIR, OUTPUT_DIR
from fetchers.app_store_fetcher import fetch_app_store_reviews
from fetchers.csv_fetcher import load_csv_reviews
from fetchers.google_play_fetcher import fetch_google_play_reviews

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_aggregated_reviews() -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    reviews.extend(fetch_google_play_reviews(max_reviews=25))
    reviews.extend(fetch_app_store_reviews(max_reviews=25))
    csv_reviews = load_csv_reviews(CSV_PATH)
    if csv_reviews:
        reviews.extend(csv_reviews)
    else:
        fallback_csv = [
            {"date": "2026-08-03", "source": "CSV", "rating": 4, "text": "Good overall, but the export step needs work."},
            {"date": "2026-08-10", "source": "CSV", "rating": 2, "text": "CSV imports are unstable and the bug is frustrating."},
            {"date": "2026-08-19", "source": "CSV", "rating": 5, "text": "The workflow is simple and the support team is helpful."},
        ]
        reviews.extend(fallback_csv)

    reviews = analyze_reviews(reviews)
    return reviews


def save_results(reviews: list[dict[str, Any]], output_dir: str | Path = OUTPUT_DIR) -> tuple[str, str]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "aggregated_feedback.csv"
    json_path = output_dir / "aggregated_feedback.json"

    df = pd.DataFrame(reviews)
    df.to_csv(csv_path, index=False)
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(reviews, handle, indent=2, default=str)
    return str(csv_path), str(json_path)


def run_pipeline() -> dict[str, Any]:
    reviews = load_aggregated_reviews()
    trend = detect_sentiment_trend(reviews)
    issues = prioritize_issues(reviews)
    csv_path, json_path = save_results(reviews)

    summary = {
        "total_reviews": len(reviews),
        "sources": sorted({entry["source"] for entry in reviews}),
        "sentiment_distribution": dict(pd.Series([entry["sentiment"] for entry in reviews]).value_counts().sort_index()),
        "trend": trend,
        "issues": issues,
        "csv_path": csv_path,
        "json_path": json_path,
    }
    logger.info("Pipeline completed. %s reviews processed.", len(reviews))
    return summary


if __name__ == "__main__":
    summary = run_pipeline()
    print(json.dumps(summary, indent=2, default=str))
