from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

import pandas as pd


def _normalize_date(value: Any) -> pd.Timestamp:
    if isinstance(value, pd.Timestamp):
        return value
    if isinstance(value, datetime):
        return pd.Timestamp(value)
    try:
        return pd.to_datetime(value)
    except Exception:
        return pd.Timestamp.now().normalize()


def build_daily_sentiment(reviews: list[dict[str, Any]]) -> pd.DataFrame:
    if not reviews:
        return pd.DataFrame(columns=["date", "sentiment_score", "sentiment"])

    df = pd.DataFrame(reviews)
    if df.empty:
        return pd.DataFrame(columns=["date", "sentiment_score", "sentiment"])

    if "date" not in df.columns:
        df["date"] = pd.Timestamp.now().normalize()

    df["date"] = df["date"].apply(_normalize_date)
    df["sentiment_score"] = pd.to_numeric(df.get("sentiment_score", 0), errors="coerce").fillna(0)

    daily = df.groupby(df["date"].dt.date).agg(sentiment_score=("sentiment_score", "mean")).reset_index()
    daily = daily.rename(columns={"date": "date"})
    daily["date"] = pd.to_datetime(daily["date"])
    return daily.sort_values("date").reset_index(drop=True)


def detect_sentiment_trend(reviews: list[dict[str, Any]], window_days: int = 7) -> dict[str, Any]:
    if not reviews:
        return {"trend": "stable", "delta": 0.0, "summary": "No review data available."}

    daily = build_daily_sentiment(reviews)
    if daily.empty or len(daily) < 2:
        return {"trend": "stable", "delta": 0.0, "summary": "Not enough review history to determine a trend."}

    daily["score_shift"] = daily["sentiment_score"].rolling(window=window_days, min_periods=1).mean()
    if len(daily) >= 2:
        start_value = float(daily["score_shift"].iloc[0])
        end_value = float(daily["score_shift"].iloc[-1])
        delta = end_value - start_value
    else:
        delta = 0.0

    if delta > 0.1:
        trend = "increasing"
    elif delta < -0.1:
        trend = "decreasing"
    else:
        trend = "stable"

    return {
        "trend": trend,
        "delta": round(delta, 3),
        "summary": f"Average sentiment moved by {delta:.3f} over the selected period.",
        "daily": daily,
    }
