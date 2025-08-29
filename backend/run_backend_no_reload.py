#!/usr/bin/env python3
import os, sys
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)
from app import create_app

if __name__ == '__main__':
    print('Starting backend (no reloader)')
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
