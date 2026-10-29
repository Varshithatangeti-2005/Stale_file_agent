
import json
from datetime import datetime
from pathlib import Path

from config import HISTORY_FILE


def load_history():
    """Load existing file history from the JSON file."""

    history_path = Path(HISTORY_FILE)

    if not history_path.exists():
        return []

    try:
        with history_path.open("r", encoding="utf-8") as file:
            history = json.load(file)

        if isinstance(history, list):
            return history

        print("Invalid history format. Starting with empty history.")
        return []

    except (json.JSONDecodeError, OSError) as error:
        print(f"Could not load history: {error}")
        return []


def save_history(history):
    """Save file history into the JSON file."""

    history_path = Path(HISTORY_FILE)

    try:
        history_path.parent.mkdir(parents=True, exist_ok=True)

        with history_path.open("w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)

        print(f"History saved successfully: {history_path}")

    except OSError as error:
        print(f"Could not save history: {error}")


def update_history(current_files):
    """Update history using the latest file monitoring results."""

    history = load_history()

    # Index existing records using their full file paths
    history_by_path = {
        record.get("file_path"): record
        for record in history
        if record.get("file_path")
    }

    current_time = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    for file_record in current_files:
        file_path = file_record.get("file_path")

        if not file_path:
            continue

        if file_path in history_by_path:
            # Update an existing file record
            existing_record = history_by_path[file_path]

            existing_record.update(file_record)
            existing_record["last_checked_time"] = current_time

        else:
            # Add a new file record
            new_record = file_record.copy()
            new_record["first_seen_time"] = current_time
            new_record["last_checked_time"] = current_time
            new_record["status_history"] = [
                {
                    "status": new_record.get("status"),
                    "time": current_time,
                }
            ]

            history.append(new_record)
            history_by_path[file_path] = new_record

    # Record status changes for files already in history
    for file_record in current_files:
        file_path = file_record.get("file_path")

        if file_path not in history_by_path:
            continue

        record = history_by_path[file_path]
        status_history = record.setdefault("status_history", [])

        latest_status = file_record.get("status")

        if (
            not status_history
            or status_history[-1].get("status") != latest_status
        ):
            status_history.append(
                {
                    "status": latest_status,
                    "time": current_time,
                }
            )

    save_history(history)

    return history


if __name__ == "__main__":
    from file_monitor import scan_monitored_folders

    print("Scanning monitored folders...")

    current_files = scan_monitored_folders()

    print(f"Files found: {len(current_files)}")

    history = update_history(current_files)

    print(f"Total history records: {len(history)}")
