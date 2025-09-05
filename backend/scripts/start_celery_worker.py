#!/usr/bin/env python3
"""
Celery worker startup script.

Starts the Celery worker for background market data processing.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.background_jobs import celery_app

if __name__ == "__main__":
    # Start Celery worker
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--concurrency=4",
        "--queues=market_data,default",
        "--hostname=market_data_worker@%h"
    ])
