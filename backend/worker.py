"""RQ worker entrypoint.

Usage:
    python -m backend.worker

Environment:
    REDIS_URL / REDISCLOUD_URL : Redis connection string
    RQ_QUEUES (optional)       : Comma-separated queue names (default: 'default')
"""
import os
from backend.app import create_app
from backend.extensions import redis_conn

try:
    import rq  # type: ignore
except Exception:  # pragma: no cover
    rq = None  # type: ignore


def main():
    app = create_app()
    if not redis_conn or not rq:
        print("Redis or rq not available; worker exiting.")
        return
    queues = [q.strip() for q in os.environ.get('RQ_QUEUES', 'default').split(',') if q.strip()]
    with app.app_context():
        q_objects = [rq.Queue(name, connection=redis_conn) for name in queues]
        worker = rq.Worker(q_objects)
        print(f"🚧 RQ Worker starting for queues: {queues}")
        worker.work()


if __name__ == '__main__':
    main()
