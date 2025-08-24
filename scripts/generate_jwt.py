"""Generate a short-lived JWT using the app's JWT configuration.

Usage:
  python3 scripts/generate_jwt.py --email joe@joe-ryan.mba --id 1 --hours 1

Prints the token to stdout.
"""
import argparse
from datetime import timedelta

parser = argparse.ArgumentParser()
parser.add_argument('--email', default='smoke@test.local')
parser.add_argument('--id', type=int, default=1)
parser.add_argument('--hours', type=int, default=1)
args = parser.parse_args()

# Import the app and create access token
from app import create_app
from flask_jwt_extended import create_access_token

app = create_app()
with app.app_context():
    identity = {"id": args.id, "email": args.email}
    token = create_access_token(identity=identity, expires_delta=timedelta(hours=args.hours))
    print(token)
