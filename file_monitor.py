

from datetime import datetime
from pathlib import Path

from config import (
    MONITORED_FOLDERS,
    MONITORED_EXTENSIONS,
    STALE_THRESHOLD_MINUTES,
)


def get_file_details(file_path):
    """Collect file details and calculate its age."""

    try:
        if not file_path.is_file():
            return None

        file_stats = file_path.stat()
        current_time = datetime.now().astimezone()

        # Calculate age based on the last modified time
        modified_time = datetime.fromtimestamp(
            file_stats.st_mtime
        ).astimezone()

        age_minutes = max(
            0,
            int((current_time - modified_time).total_seconds() / 60),
        )

        # Get creation time where supported
        if hasattr(file_stats, "st_birthtime"):
            created_timestamp = file_stats.st_birthtime
        elif file_path.stat() and __import__("os").name == "nt":
            created_timestamp = file_stats.st_ctime
        else:
            created_timestamp = None

        created_time = (
            datetime.fromtimestamp(created_timestamp)
            .astimezone()
            .isoformat(timespec="seconds")
            if created_timestamp is not None
            else None
        )

        # Check whether the file extension should be monitored
        if MONITORED_EXTENSIONS:
            if file_path.suffix.lower() not in [
                ext.lower() for ext in MONITORED_EXTENSIONS
            ]:
                return None

        # Determine the file status
        status = (
            "STALE"
            if age_minutes >= STALE_THRESHOLD_MINUTES
            else "MONITORING"
        )

        return {
            "file_name": file_path.name,
            "file_path": str(file_path.resolve()),
            "folder_path": str(file_path.parent.resolve()),
            "created_time": created_time,
            "last_modified_time": modified_time.isoformat(
                timespec="seconds"
            ),
            "size_bytes": file_stats.st_size,
            "age_minutes": age_minutes,
            "status": status,
            "last_movement_time": None,
        }

    except (OSError, PermissionError) as error:
        print(f"Could not read {file_path}: {error}")
        return None


def scan_folder(folder_path):
    """Scan one folder and collect file details."""

    folder_path = Path(folder_path)
    file_records = []

    if not folder_path.exists():
        print(f"Folder does not exist: {folder_path}")
        return file_records

    if not folder_path.is_dir():
        print(f"Not a directory: {folder_path}")
        return file_records

    try:
        for file_path in folder_path.rglob("*"):
            if file_path.is_file():
                file_details = get_file_details(file_path)

                if file_details is not None:
                    file_records.append(file_details)

    except OSError as error:
        print(f"Could not scan {folder_path}: {error}")

    return file_records


def scan_monitored_folders():
    """Scan all folders configured in config.py."""

    all_file_records = []

    for folder in MONITORED_FOLDERS:
        print(f"Scanning folder: {folder}")

        records = scan_folder(folder)
        all_file_records.extend(records)

    return all_file_records


if __name__ == "__main__":
    files = scan_monitored_folders()

    print(f"\nTotal files found: {len(files)}")

    for file_record in files:
        print(file_record)
