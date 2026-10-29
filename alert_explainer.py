

from config import STALE_THRESHOLD_MINUTES


def generate_alert_explanation(file_record):
    """Generate an explanation for a stale file alert."""

    file_name = file_record.get("file_name", "Unknown file")
    file_path = file_record.get("file_path", "Unknown path")
    age_minutes = file_record.get("age_minutes", 0)
    status = file_record.get("status", "UNKNOWN")
    size_bytes = file_record.get("size_bytes", 0)

    if status != "STALE" and age_minutes < STALE_THRESHOLD_MINUTES:
        return None

    reason = (
        f"{file_name} has remained in the monitored folder for "
        f"{age_minutes} minutes, exceeding the configured "
        f"stale threshold of {STALE_THRESHOLD_MINUTES} minutes."
    )

    recommended_actions = [
        "Check whether the file-processing service is running.",
        "Verify source and destination folder permissions.",
        "Review processing logs for errors related to this file.",
        "Confirm whether the file is waiting for another process.",
    ]

    return {
        "alert_type": "STALE_FILE",
        "file_name": file_name,
        "file_path": file_path,
        "file_age_minutes": age_minutes,
        "threshold_minutes": STALE_THRESHOLD_MINUTES,
        "size_bytes": size_bytes,
        "severity": "HIGH",
        "reason": reason,
        "recommended_actions": recommended_actions,
    }


if __name__ == "__main__":
    from file_monitor import scan_monitored_folders

    files = scan_monitored_folders()

    print("\nAlert Explanation Results")

    for file_record in files:
        alert = generate_alert_explanation(file_record)

        if alert:
            print(alert)
        else:
            print(
                f"{file_record['file_name']}: "
                "No stale alert required."
            )
