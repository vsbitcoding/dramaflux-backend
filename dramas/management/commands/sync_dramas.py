"""
Django management command for syncing dramas - RELIABLE VERSION.
Uses sequential processing to ensure 100% unlock rate.

Usage:
    python manage.py sync_dramas
"""
import asyncio
import logging
from django.core.management.base import BaseCommand
from dramas.sync_service import ReliableDramaSyncService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Reliable sync all dramas and episodes'

    def handle(self, *args, **options):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        
        self.stdout.write(self.style.NOTICE('Starting Reliable Sync Service...'))
        
        try:
            service = ReliableDramaSyncService()
            asyncio.run(service.start_sync())
            
            self.stdout.write(self.style.SUCCESS('Sync Process Finished.'))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Sync failed: {str(e)}'))
