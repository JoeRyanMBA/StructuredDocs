from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

try:
	import sentry_sdk  # type: ignore
	from sentry_sdk.integrations.flask import FlaskIntegration  # type: ignore
except Exception:  # pragma: no cover - sentry optional
	sentry_sdk = None  # type: ignore
	FlaskIntegration = None  # type: ignore

try:
	import redis  # type: ignore
except Exception:  # pragma: no cover
	redis = None  # type: ignore

try:
	import rq  # type: ignore
except Exception:  # pragma: no cover
	rq = None  # type: ignore

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# Limiter configured later with app context (key_func needs request context)
limiter: Limiter | None = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])  # type: ignore

# Redis / RQ handles (initialized in app factory if redis available)
redis_conn = None
task_queue = None

def init_sentry(dsn: str | None):  # lightweight helper
	if dsn and sentry_sdk and FlaskIntegration:
		sentry_sdk.init(dsn=dsn, integrations=[FlaskIntegration()], traces_sample_rate=float(
			(dsn and 0.1) or 0.0))
		return True
	return False

