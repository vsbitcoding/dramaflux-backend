import os
import django
import asyncio
from asgiref.sync import sync_to_async
from django.conf import settings
import aiohttp

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dramaflux.settings")
django.setup()

from dramas.sync_service import ReliableDramaSyncService
from dramas.models import Drama

async def refresh():
    try:
        service = await sync_to_async(ReliableDramaSyncService)()
        drama_id = "V32298644053821764888394483315"
        try:
            drama = await sync_to_async(Drama.objects.get)(drama_id=drama_id)
            print(f"Found drama: {drama.name}. Refreshing Episode 1...")
        except Drama.DoesNotExist:
            print(f"Drama {drama_id} not found locally! Fetching list first...")
            # If drama not found, we might need to fetch it first, but let's assume it is there since we saw it in API
            return

        async with aiohttp.ClientSession() as session:
            # Unlock and verify (Refreshes the token in DB)
            success = await service.verify_and_unlock(session, drama, 1)
            
            if success:
                print("Successfully refreshed episode 1!")
                # Print new URL
                from dramas.models import Episode
                ep = await sync_to_async(Episode.objects.get)(drama=drama, episode_number=1)
                print(f"New Video URL: {ep.video_url}")
            else:
                print("Failed to refresh episode 1.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(refresh())
