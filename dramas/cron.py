import logging
import subprocess
import os
from django.conf import settings

logger = logging.getLogger(__name__)

def run_drama_sync():
    """
    Cron job to run drama sync nightly.
    Uses the reliable management command.
    """
    logger.info("Starting nightly drama sync via cron...")
    
    # Path to manage.py
    manage_py = os.path.join(settings.BASE_DIR, 'manage.py')
    
    # Run the command with python -u for unbuffered output
    # We use subprocess to run it exactly like the user would
    # Note: We assume the venv python is available or we use sys.executable
    import sys
    
    try:
        # Run sequential sync
        subprocess.run(
            [sys.executable, '-u', manage_py, 'sync_dramas'],
            check=True
        )
        logger.info("Nightly sync completed successfully.")
    except Exception as e:
        logger.error(f"Nightly sync failed: {e}")
