

from history_manager import load_history
from config import PREDICTION_RATIO, STALE_THRESHOLD_MINUTES


def get_expected_processing_time(file_record, history):
    """Calculate expected processing time using available history."""

    file_path = file_record.get("file_path")
    file_name = file_record.get("file_name")

    # Find previous records for the same file
    matching_records = [
        record
        for record in history
        if record.get("file_path") == file_path
        and record.get("processing_time_minutes") is not None
    ]

    # If the same file has no completed processing history,
    # check whether other files with the same name have history.
    if not matching_records:
        matching_records = [
            record
            for record in history
            if record.get("file_name") == file_name
            and record.get("processing_time_minutes") is not None
        ]

    if matching_records:
        durations = [
            record["processing_time_minutes"]
            for record in matching_records
        ]

        return sum(durations) / len(durations)

    # No historical processing duration is available yet.
    return None


def predict_delay(file_record, history=None):
    """Predict whether a file may become stale before its threshold."""

    if history is None:
        history = load_history()

    age_minutes = file_record.get("age_minutes", 0)

    expected_time = get_expected_processing_time(
        file_record,
        history,
    )

    # Without historical processing times, use the configured
    # stale threshold to provide a basic early warning.
    if expected_time is None:
        expected_time = STALE_THRESHOLD_MINUTES

    prediction_time = expected_time * PREDICTION_RATIO

    if age_minutes >= STALE_THRESHOLD_MINUTES:
        risk = "STALE"
        message = "The file has reached the stale threshold."

    elif age_minutes >= prediction_time:
        risk = "HIGH"
        message = (
            "The file may be delayed. It is approaching "
            "its expected processing time."
        )

    else:
        risk = "LOW"
        message = "The file is within its expected monitoring period."

    return {
        "file_name": file_record.get("file_name"),
        "age_minutes": age_minutes,
        "expected_processing_minutes": round(expected_time, 2),
        "prediction_trigger_minutes": round(prediction_time, 2),
        "delay_risk": risk,
        "prediction_message": message,
    }


if __name__ == "__main__":
    from file_monitor import scan_monitored_folders

    files = scan_monitored_folders()
    history = load_history()

    print("\nDelay Prediction Results")

    for file_record in files:
        result = predict_delay(file_record, history)
        print(result)
