
import json
from datetime import datetime
from pathlib import Path
from api_client import send_alerts
from config import REPORT_FILE


def save_monitoring_report(file_records, predictions=None, alerts=None):
    """Save monitoring results, predictions, and alerts to JSON."""

    predictions = predictions or []
    alerts = alerts or []

    report = {
        "generated_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "total_files": len(file_records),
        "total_predictions": len(predictions),
        "total_alerts": len(alerts),
        "files": file_records,
        "predictions": predictions,
        "alerts": alerts,
    }

    report_path = Path(REPORT_FILE)

    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with report_path.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        print(f"\nMonitoring report saved: {report_path}")

    except OSError as error:
        print(f"Could not save monitoring report: {error}")

    return report


if __name__ == "__main__":
    from file_monitor import scan_monitored_folders
    from history_manager import load_history, update_history
    from delay_predictor import predict_delay
    from alert_explainer import generate_alert_explanation

    print("Starting file monitoring report generation...")

    # 1. Scan configured folders
    files = scan_monitored_folders()

    # 2. Update JSON history
    history = update_history(files)

    # 3. Generate delay predictions
    predictions = [
        predict_delay(file_record, history)
        for file_record in files
    ]

    # 4. Generate explanations for stale files
    alerts = []

    for file_record in files:
        alert = generate_alert_explanation(file_record)

        if alert:
            alerts.append(alert)
    # Send stale alerts to the existing API
    send_alerts(alerts)



    # 5. Save the complete report
    report = save_monitoring_report(
        file_records=files,
        predictions=predictions,
        alerts=alerts,
    )

    print("\n--- Monitoring Summary ---")
    print(f"Total files scanned: {report['total_files']}")
    print(f"Total predictions: {report['total_predictions']}")
    print(f"Total stale alerts: {report['total_alerts']}")
