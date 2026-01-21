"""
Reliable Drama Sync Service
Prioritizes accuracy and completeness over speed.
Processes one by one to ensure every episode is unlocked.
"""
import asyncio
import aiohttp
import logging
import random
from django.utils import timezone
from asgiref.sync import sync_to_async
from .models import Drama, Episode, JoliboxConfig, SyncLog

logger = logging.getLogger(__name__)

class ReliableDramaSyncService:
    BASE_URL = "https://www.nanodrama.com/api"

    def __init__(self):
        self.config = JoliboxConfig.get_config()
        if not self.config:
            raise ValueError("No Jolibox configuration found")

    def _get_headers(self, drama_id: str = None, episode_num: int = None) -> dict:
        headers = {
            "accept": "application/json",
            "accept-language": "en",
            "referer": "https://www.nanodrama.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "x-joli-accept-language": "en",
            "x-joli-source": self.config.joli_source_token,
            "x-os-type": "ANDROID",
            "x-runtime-type": "WEB",
        }
        if drama_id:
            headers["x-user-agent"] = f"JoliboxMinidramaWeb (PC; undefined; 10; en) uuid/{self.config.device_id} adid/ version/2.4.0"
            if episode_num:
                 headers["referer"] = f"https://www.nanodrama.com/drama/{drama_id}/{episode_num}"
        return headers

    async def start_sync(self):
        """Main entry point for reliable sync."""
        
        # Create SyncLog entry
        sync_log = await sync_to_async(SyncLog.objects.create)(
            sync_type='full',
            status='running'
        )
        
        try:
            async with aiohttp.ClientSession() as session:
                # 1. Fetch and store all dramas first
                print("Step 1: Fetching all dramas...")
                dramas_count = await self.fetch_all_dramas(session)
                print(f"Step 1 Complete. Found {dramas_count} dramas.")
                
                # Update log
                await sync_to_async(self._update_log_dramas)(sync_log, dramas_count)

                # 2. Process dramas in parallel batches (10 at a time)
                print("Step 2: Unlocking episodes (10 dramas in parallel)...")
                
                # Get all dramas from DB
                dramas = await sync_to_async(list)(Drama.objects.filter(is_active=True))
                
                semaphore = asyncio.Semaphore(10)
                
                async def process_with_semaphore(drama):
                    async with semaphore:
                        print(f"Starting: {drama.name}")
                        await self.process_drama_episodes(session, drama, sync_log)
                        print(f"Finished: {drama.name}")

                tasks = [process_with_semaphore(drama) for drama in dramas]
                await asyncio.gather(*tasks)
                
                # Completion
                await sync_to_async(self._complete_log)(sync_log, 'completed')
                
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            await sync_to_async(self._complete_log)(sync_log, 'failed', str(e))

    def _update_log_dramas(self, log, count):
        log.dramas_synced = count
        log.save()
        
    def _complete_log(self, log, status, error=""):
        log.status = status
        log.errors = error
        log.completed_at = timezone.now()
        log.save()

    async def fetch_all_dramas(self, session):
        url = f"{self.BASE_URL}/dramas"
        params = {"tag": "ALL", "limit": 2000, "reqId": "dramaflux"}
        
        try:
            async with session.get(url, headers=self._get_headers(), params=params) as resp:
                result = await resp.json()
                if result.get('code') == 'SUCCESS':
                    dramas_list = result.get('data', [])
                    await sync_to_async(self._save_dramas_batch)(dramas_list)
                    return len(dramas_list)
        except Exception as e:
            logger.error(f"Error fetching dramas: {e}")
        return 0

    def _save_dramas_batch(self, dramas_list):
        for data in dramas_list:
            Drama.objects.update_or_create(
                drama_id=data.get('dramaId'),
                defaults={
                    'name': data.get('name') or '',
                    'description': data.get('description') or '',
                    'cover_url': data.get('cover') or '',
                    'logo_url': data.get('logo') or '',
                    'episode_count': data.get('episodeCount') or 0,
                    'orientation': data.get('orientation') or 'VERTICAL',
                    'categories': data.get('categories') or [],
                    'status': data.get('status') or 'PUBLISHED',
                    'content_provider_id': data.get('contentProviderId') or '',
                    'is_active': data.get('channelActive', True),
                }
            )

    async def process_drama_episodes(self, session, drama, sync_log=None):
        """Unlock all episodes for a drama sequentially."""
        for ep_num in range(1, drama.episode_count + 1):
            # Check if already unlocked (optional optimization, but user said 'try again to unlock' implying verify execution)
            # We will just verify and unlock if needed.
            
            unlocked = False
            attempts = 0
            
            while not unlocked:
                unlocked = await self.verify_and_unlock(session, drama, ep_num)
                
                if unlocked:
                   print(f"  ✓ Episode {ep_num} Unlocked")
                   if sync_log:
                       await sync_to_async(self._increment_episode_count)(sync_log)
                   # Small delay to be nice
                   await asyncio.sleep(0.5)
                else:
                    attempts += 1
                    wait_time = min(attempts * 2, 30) # Backoff cap at 30s
                    print(f"  ✗ Episode {ep_num} Locked. Retrying in {wait_time}s... (Attempt {attempts})")
                    await asyncio.sleep(wait_time)

    def _increment_episode_count(self, log):
        log.episodes_synced += 1
        log.save()

    async def verify_and_unlock(self, session, drama, ep_num):
        """Try to unlock and then verify. Returns True if unlocked."""
        try:
            # 1. Attempt Unlock
            unlock_url = f"{self.BASE_URL}/dramas/ads/unlock"
            u_params = {"dramaId": drama.drama_id, "sessionId": "dramaflux", "episodeNum": ep_num}
            
            async with session.get(unlock_url, headers=self._get_headers(drama.drama_id, ep_num), params=u_params) as resp:
                await resp.read() # Consume response
            
            await asyncio.sleep(1) # Wait for server propagation

            # 2. Verify with Detail API
            detail_url = f"{self.BASE_URL}/dramas/{drama.drama_id}/detail"
            d_params = {"episodeNum": ep_num}
            
            async with session.get(detail_url, headers=self._get_headers(drama.drama_id), params=d_params) as resp:
                data = await resp.json()
                
                if data.get('code') == 'SUCCESS':
                    play_info = data.get('data', {}).get('playInfo', {})
                    video_url = play_info.get('episodeM3u8', '')
                    
                    if video_url:
                        await sync_to_async(self._save_episode)(drama, ep_num, video_url)
                        return True
                        
        except Exception as e:
            logger.error(f"Error on {drama.name} {ep_num}: {e}")
            
        return False

    def _save_episode(self, drama, ep_num, url):
        Episode.objects.update_or_create(
            drama=drama,
            episode_number=ep_num,
            defaults={'video_url': url, 'is_unlocked': True}
        )
