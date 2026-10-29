
from fastapi import FastAPI, HTTPException
from pathlib import Path
from datetime import datetime
import json

app = FastAPI(title="Stale File Monitoring API")

# Store received alerts in a JSON file
BASE_DIR = Path(__file__).resolve().parent
ALERTS_FILE = BASE_DIR / "received_alerts.json"


def load_alerts():
    """Load previously received alerts."""

    if not ALERTS_FILE.exists():
        return []

    try:
        with ALERTS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def save_alerts(alerts):
    """Save alerts to JSON."""

    try:
        with ALERTS_FILE.open("w", encoding="utf-8") as file:
            json.dump(alerts, file, indent=4)

    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not save alerts: {error}",
        )


@app.get("/")
def home():
    return {
        "message": "Stale File Monitoring API is running"
    }


@app.post("/api/alerts")
def receive_alert(alert: dict):
    """Receive a stale-file alert from api_client.py."""

    if not alert.get("file_name"):
        raise HTTPException(
            status_code=400,
            detail="file_name is required",
        )

    alerts = load_alerts()

    received_alert = alert.copy()
    received_alert["received_at"] = (
        datetime.now().astimezone().isoformat(
            timespec="seconds"
        )
    )

    alerts.append(received_alert)
    save_alerts(alerts)

    return {
        "message": "Alert received successfully",
        "file_name": received_alert["file_name"],
        "total_alerts": len(alerts),
    }


@app.get("/api/alerts")
def get_alerts():
    """Return all received alerts."""

    return load_alerts()
