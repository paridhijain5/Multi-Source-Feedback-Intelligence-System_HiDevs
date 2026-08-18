from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any


def load_csv_reviews(file_path: str | Path) -> list[dict[str, Any]]:
    csv_path = Path(file_path)
    if not csv_path.exists():
        return []

    records: list[dict[str, Any]] = []
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row:
                continue
            text = row.get("review_text") or row.get("text") or row.get("comment") or ""
            rating = row.get("rating")
            try:
                rating_value = int(float(rating)) if rating not in (None, "") else 0
            except (TypeError, ValueError):
                rating_value = 0
            records.append(
                {
                    "date": row.get("date") or datetime.utcnow().isoformat(),
                    "source": row.get("source") or "CSV",
                    "rating": rating_value,
                    "text": text,
                    "sentiment": row.get("sentiment") or None,
                    "sentiment_confidence": row.get("sentiment_confidence") or None,
                }
            )
    return records
