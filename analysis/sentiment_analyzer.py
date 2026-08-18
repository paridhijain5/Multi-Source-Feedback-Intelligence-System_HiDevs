from __future__ import annotations

from typing import Any

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        return {"label": "neutral", "confidence": 0.0, "score": 0.0}

    sentiment_score = analyzer.polarity_scores(text)["compound"]

    if sentiment_score >= 0.05:
        label = "positive"
    elif sentiment_score <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    confidence = min(1.0, max(0.0, abs(sentiment_score) * 0.8 + 0.2))
    return {"label": label, "confidence": round(confidence, 3), "score": round(sentiment_score, 3)}


def analyze_reviews(reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for entry in reviews:
        text = str(entry.get("text") or entry.get("review_text") or "")
        result = analyze_sentiment(text)
        record = dict(entry)
        record["sentiment"] = result["label"]
        record["sentiment_confidence"] = result["confidence"]
        record["sentiment_score"] = result["score"]
        enriched.append(record)
    return enriched
