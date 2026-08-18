import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

GOOGLE_PLAY_PACKAGE = os.getenv("GOOGLE_PLAY_PACKAGE", "com.example.feedbackapp")
APP_STORE_APP_ID = os.getenv("APP_STORE_APP_ID", "id284882215")
CSV_PATH = os.getenv("CSV_PATH", str(DATA_DIR / "sample_feedback.csv"))
REPORT_PATH = os.getenv("REPORT_PATH", str(OUTPUT_DIR / "weekly_report.pdf"))

DATE_RANGE_DAYS = int(os.getenv("DATE_RANGE_DAYS", "30"))

DEFAULT_GOOGLE_PLAY_REVIEWS = int(os.getenv("GOOGLE_PLAY_REVIEWS", "25"))
DEFAULT_APP_STORE_REVIEWS = int(os.getenv("APP_STORE_REVIEWS", "25"))

DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def get_enabled_sources() -> list[str]:
    sources = os.getenv("ENABLED_SOURCES", "google_play,app_store,csv")
    return [source.strip().lower() for source in sources.split(",") if source.strip()]
