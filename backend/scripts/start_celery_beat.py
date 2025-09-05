#!/usr/bin/env python3
"""
Celery beat scheduler startup script.

Starts the Celery beat scheduler for periodic tasks.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.background_jobs import celery_app

if __name__ == "__main__":
    # Start Celery beat scheduler
    celery_app.start([
        "beat",
        "--loglevel=info",
        "--scheduler=celery.beat:PersistentScheduler"
    ])
