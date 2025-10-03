"""Log Rotation Utility - Manage log file sizes and archives."""

from pathlib import Path


def rotate_log(log_path: Path, max_size_mb: int = 10, max_files: int = 3) -> None:
    """Rotate log file if it exceeds size limit.

    Args:
        log_path: Path to the log file
        max_size_mb: Maximum size in megabytes before rotation
        max_files: Maximum number of archived log files to keep

    Example:
        rotate_log(Path("logs/activity.log"), max_size_mb=10, max_files=3)
        # Creates: activity.log.1, activity.log.2, activity.log.3
    """
    if not log_path.exists():
        return

    # Check file size
    size_mb = log_path.stat().st_size / (1024 * 1024)
    if size_mb < max_size_mb:
        return

    # Rotate existing backups (shift numbers up)
    for i in range(max_files, 0, -1):
        src = log_path.with_suffix(f"{log_path.suffix}.{i}")
        dst = log_path.with_suffix(f"{log_path.suffix}.{i+1}")

        if src.exists():
            if i == max_files:
                # Delete oldest backup
                src.unlink()
            else:
                # Shift to next number
                src.rename(dst)

    # Move current log to .1
    backup = log_path.with_suffix(f"{log_path.suffix}.1")
    log_path.rename(backup)
