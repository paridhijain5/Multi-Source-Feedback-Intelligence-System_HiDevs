import unittest

from analysis.issue_prioritizer import prioritize_issues


class IssuePrioritizerTests(unittest.TestCase):
    def test_detects_richer_issue_themes(self):
        reviews = [
            {"text": "Login keeps failing after the update and I cannot sign in.", "sentiment": "negative"},
            {"text": "The app is too slow and crashes when loading data.", "sentiment": "negative"},
            {"text": "I want a dark mode or better search feature request.", "sentiment": "neutral"},
            {"text": "My subscription charged twice and refund is impossible.", "sentiment": "negative"},
            {"text": "Push notifications are delayed and reminders never come.", "sentiment": "negative"},
            {"text": "The sign-in page is confusing and the account lockout is frustrating.", "sentiment": "negative"},
        ]

        issues = prioritize_issues(reviews)
        labels = {item["topic"] for item in issues}

        self.assertIn("login", labels)
        self.assertIn("performance", labels)
        self.assertIn("feature", labels)
        self.assertIn("billing", labels)
        self.assertIn("notifications", labels)


if __name__ == "__main__":
    unittest.main()
