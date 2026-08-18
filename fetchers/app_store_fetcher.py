from __future__ import annotations

import logging
from typing import Any

import requests

from config import APP_STORE_APP_ID

logger = logging.getLogger(__name__)


def _mock_app_store_reviews(limit: int = 25) -> list[dict[str, Any]]:
    samples = [
        ("2026-08-02", 5, "App works smoothly and is easy to use."),
        ("2026-08-05", 3, "The UI is clean, but syncing is inconsistent."),
        ("2026-08-08", 2, "Crashes when opening the dashboard."),
        ("2026-08-11", 1, "Frequent payment issues after the new release."),
        ("2026-08-13", 4, "Feature set is great but a bit slow."),
        ("2026-08-16", 5, "Very polished and reliable."),
        ("2026-08-18", 2, "Notifications never show up sometimes."),
        ("2026-08-21", 3, "Good app with some navigation issues."),
        ("2026-08-24", 1, "The app is unusable because of login bugs."),
        ("2026-08-27", 4, "I like the updates and the support team."),
    ]
    return [
        {
            "date": date,
            "source": "App Store",
            "rating": rating,
            "text": text,
            "sentiment": None,
            "sentiment_confidence": None,
        }
        for date, rating, text in samples[:limit]
    ]


def fetch_app_store_reviews(app_id: str | None = None, max_reviews: int = 25) -> list[dict[str, Any]]:
    app_id = app_id or APP_STORE_APP_ID
    feed_url = f"https://itunes.apple.com/us/rss/customerreviews/id={app_id}/sortBy=mostRecent/xml"
    try:
        response = requests.get(feed_url, timeout=15)
        response.raise_for_status()
        xml_text = response.text
        if "<entry>" not in xml_text:
            raise ValueError("No review entries returned in App Store feed.")

        import xml.etree.ElementTree as ET

        root = ET.fromstring(xml_text)
        namespace = {"a": "http://www.w3.org/2005/Atom", "im": "http://itunes.apple.com/rss"}
        records = []
        for item in root.findall(".//entry"):
            date = item.findtext("updated", default="")
            text = item.findtext("content", default="")
            rating = item.findtext(".//im:rating", namespaces=namespace, default="0")
            if not text:
                continue
            records.append(
                {
                    "date": date[:10] if date else "",
                    "source": "App Store",
                    "rating": int(float(rating or 0)),
                    "text": text,
                    "sentiment": None,
                    "sentiment_confidence": None,
                }
            )
            if len(records) >= max_reviews:
                break
        if records:
            return records
        raise ValueError("No review entries found after parsing App Store feed.")
    except Exception as exc:
        logger.warning("App Store fetch failed: %s. Falling back to mock data.", exc)
        return _mock_app_store_reviews(max_reviews)
