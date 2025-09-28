#!/usr/bin/env python3

"""Generic WSGI entrypoint for StructuredDocs."""

from backend.app import create_app

application = create_app()
