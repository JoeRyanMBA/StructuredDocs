#!/usr/bin/env python3

"""Reference WSGI entrypoint for StructuredDocs."""

from backend.app import create_app

application = create_app()
