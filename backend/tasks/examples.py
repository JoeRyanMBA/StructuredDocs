"""Example background tasks for RQ.

These are illustrative; replace or extend with real application logic.
"""
import time
from datetime import datetime


def example_long_task(duration: int = 5) -> dict:
    """Simulate a long-running job.

    Args:
        duration: Seconds to sleep.
    Returns:
        Dict with metadata about the run.
    """
    start = datetime.utcnow()
    time.sleep(max(0, duration))
    end = datetime.utcnow()
    return {
        "task": "example_long_task",
        "duration": duration,
        "started": start.isoformat() + 'Z',
        "finished": end.isoformat() + 'Z',
        "status": "completed"
    }
