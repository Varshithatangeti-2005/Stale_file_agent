

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Project base directory
BASE_DIR = Path(__file__).resolve().parent

# 1. Folders to monitor
# Replace these sample paths with your actual folder paths
MONITORED_FOLDERS = [
    BASE_DIR / "source",
    BASE_DIR / "source2",
]

# 2. File monitoring settings
# Monitor all file types when the list is empty
MONITORED_EXTENSIONS = []

# 3. Stale file threshold
STALE_THRESHOLD_MINUTES = 5

# 4. Early delay prediction settings
# Warn when file age reaches 80% of expected processing time
PREDICTION_RATIO = 0.8

# 5. JSON history and report files
HISTORY_FILE = BASE_DIR / "file_history.json"
REPORT_FILE = BASE_DIR / "monitoring_report.json"

# 6. Existing API configuration
API_URL = os.getenv("API_URL", "")

# 7. Google ADK / Gemini configuration
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
