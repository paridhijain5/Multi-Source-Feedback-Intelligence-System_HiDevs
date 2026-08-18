from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any


TOPIC_KEYWORDS = {
    "bug": [
        "bug", "bugs", "crash", "crashes", "freeze", "freezes", "error", "errors", "fails",
        "failure", "broken", "glitch", "stuck", "won t", "can't", "cannot", "fault", "issue"
    ],
    "performance": [
        "slow", "slower", "lag", "laggy", "loading", "load time", "unresponsive", "timeout",
        "delay", "delayed", "hang", "stuck", "spinner", "takes forever"
    ],
    "login": [
        "login", "log in", "sign in", "signin", "auth", "authentication", "password",
        "account access", "locked out", "session", "credential", "reset password", "access denied"
    ],
    "billing": [
        "billing", "payment", "payments", "refund", "refunds", "charge", "charged", "subscription",
        "invoice", "paid twice", "price", "renewal"
    ],
    "feature": [
        "feature request", "feature", "request", "would like", "wish", "missing", "need",
        "want", "could add", "could use", "dark mode", "search", "filter", "export", "sync"
    ],
    "ui_ux": [
        "ui", "ux", "design", "layout", "button", "buttons", "navigation", "screen", "menu",
        "confusing", "cluttered", "overwhelming", "easy to use", "intuitive"
    ],
    "notifications": [
        "notification", "notifications", "alert", "alerts", "push", "reminder", "reminders",
        "message", "messages", "sound", "badge"
    ],
    "update": [
        "update", "new update", "after update", "version", "upgrade", "patch", "release"
    ],
}


def normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", str(text).lower())


def prioritize_issues(reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    topics = defaultdict(lambda: {"count": 0, "negative_count": 0, "weight": 0.0})

    for entry in reviews:
        text = str(entry.get("text") or entry.get("review_text") or "")
        sentiment = str(entry.get("sentiment") or "neutral").lower()
        normalized = normalize_text(text)
        mentioned = set()

        for label, keywords in TOPIC_KEYWORDS.items():
            label_match = False
            for keyword in keywords:
                if keyword in normalized:
                    label_match = True
                    break
            if label_match:
                mentioned.add(label)

        if not mentioned and text:
            for label, keywords in TOPIC_KEYWORDS.items():
                for keyword in keywords:
                    if keyword.replace(" ", "") in normalized.replace(" ", ""):
                        mentioned.add(label)
                        break

        for label in mentioned:
            topics[label]["count"] += 1
            if sentiment == "negative":
                topics[label]["negative_count"] += 1
                topics[label]["weight"] += 1.5
            elif sentiment == "neutral":
                topics[label]["weight"] += 0.5
            else:
                topics[label]["weight"] += 0.25

    results = []
    for label, values in topics.items():
        score = values["count"] + values["weight"] + (values["negative_count"] * 2)
        if score >= 7:
            priority = "High"
        elif score >= 4:
            priority = "Medium"
        else:
            priority = "Low"
        results.append(
            {
                "topic": label,
                "count": values["count"],
                "negative_count": values["negative_count"],
                "score": round(score, 2),
                "priority": priority,
            }
        )

    return sorted(results, key=lambda item: (-item["score"], -item["count"]))
