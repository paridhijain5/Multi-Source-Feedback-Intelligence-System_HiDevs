from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import requests

from config import GOOGLE_PLAY_PACKAGE, get_enabled_sources

logger = logging.getLogger(__name__)


def _mock_google_play_reviews(limit: int = 25) -> list[dict[str, Any]]:
    samples = [
        ("2026-08-01", 5, "App is fast and the new dashboard looks great."),
        ("2026-08-04", 4, "Good experience overall, but notifications are delayed."),
        ("2026-08-06", 2, "The app keeps crashing on login and freezes often."),
        ("2026-08-09", 1, "Very slow and the latest update broke sign in."),
        ("2026-08-12", 3, "Mostly okay, but the UI can be confusing."),
        ("2026-08-15", 5, "Love the new features and responsive support."),
        ("2026-08-17", 2, "Billing page error keeps showing up."),
        ("2026-08-20", 4, "Nice app, but some pages load slowly."),
        ("2026-08-22", 1, "The app fails to load after update."),
        ("2026-08-25", 5, "Smooth experience and very helpful reminders."),
    ]
    records = []
    for idx, (date, rating, text) in enumerate(samples[:limit]):
        records.append(
            {
                "date": date,
                "source": "Google Play",
                "rating": rating,
                "text": text,
                "sentiment": None,
                "sentiment_confidence": None,
            }
        )
    return records


def fetch_google_play_reviews(package_name: str | None = None, max_reviews: int = 25) -> list[dict[str, Any]]:
    package = package_name or GOOGLE_PLAY_PACKAGE
    try:
        if "google_play" not in get_enabled_sources():
            raise RuntimeError("Google Play source disabled in config")

        try:
            from google_play_scraper import reviews as google_reviews
        except ImportError:
            logger.warning("google-play-scraper not available; using mock Google Play reviews.")
            return _mock_google_play_reviews(max_reviews)

        result, _ = google_reviews(
            package,
            lang="en",
            country="us",
            sort=google_reviews.__globals__.get("Sort", {}).get("NEWEST", 3) if hasattr(google_reviews, "__globals__") else 3,
            count=max_reviews,
        )
        return [
            {
                "date": datetime.utcfromtimestamp(item["at"].timestamp()).strftime("%Y-%m-%d"),
                "source": "Google Play",
                "rating": item.get("score", 0),
                "text": item.get("content", ""),
                "sentiment": None,
                "sentiment_confidence": None,
            }
            for item in result
        ]
    except Exception as exc:
        logger.warning("Google Play fetch failed: %s. Falling back to mock data.", exc)
        return _mock_google_play_reviews(max_reviews)
