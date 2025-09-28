#!/usr/bin/env python3

"""Generic WSGI entrypoint kept for legacy compatibility."""

from backend.app import create_app

application = create_app()
