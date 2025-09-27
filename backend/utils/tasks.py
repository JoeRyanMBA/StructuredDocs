"""Helper utilities for enqueuing background tasks."""
from importlib import import_module
from typing import Any
from backend.extensions import task_queue


def enqueue_task(func_path: str, *args: Any, **kwargs: Any):
    """Enqueue a task by dotted path.

    Example:
        enqueue_task('backend.tasks.examples.example_long_task', duration=10)
    """
    if not task_queue:
        raise RuntimeError("Task queue not initialized (Redis not configured)")
    module_name, attr = func_path.rsplit('.', 1)
    mod = import_module(module_name)
    fn = getattr(mod, attr)
    return task_queue.enqueue(fn, *args, **kwargs)
