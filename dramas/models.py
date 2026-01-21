from django.db import models


class JoliboxConfig(models.Model):
    """Singleton configuration model for storing Jolibox API credentials."""
    
    joli_source_token = models.TextField(help_text="Jolibox API source token", blank=True, default="")
    device_id = models.CharField(max_length=255, help_text="Device identifier", blank=True, default="")

    class Meta:
        verbose_name = "Jolibox Configuration"
        verbose_name_plural = "Jolibox Configuration"

    def __str__(self):
        return "API Configuration"

    def save(self, *args, **kwargs):
        """Ensure only one record exists."""
        if not self.pk and JoliboxConfig.objects.exists():
            existing = JoliboxConfig.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        """Get or create the single configuration."""
        config, _ = cls.objects.get_or_create(pk=1)
        return config


class Drama(models.Model):
    """Cached drama from NanoDrama API."""
    
    drama_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True, default="")
    cover_url = models.URLField(max_length=2000, blank=True, default="")
    logo_url = models.URLField(max_length=2000, blank=True, default="")
    episode_count = models.IntegerField(default=0)
    orientation = models.CharField(max_length=20, default="VERTICAL")
    categories = models.JSONField(default=list, blank=True)
    views = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default="PUBLISHED")
    host_mode = models.CharField(max_length=50, default="JOLIBOX_HOST")
    content_provider_id = models.CharField(max_length=100, blank=True, default="")
    is_active = models.BooleanField(default=True)
    last_synced = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Drama"
        verbose_name_plural = "Dramas"
        ordering = ['-views', 'name']

    def __str__(self):
        return f"{self.name} ({self.drama_id})"


class Episode(models.Model):
    """Cached episode with video URL from NanoDrama API."""
    
    drama = models.ForeignKey(Drama, on_delete=models.CASCADE, related_name='episodes')
    episode_number = models.IntegerField()
    video_url = models.URLField(max_length=2000, blank=True, default="")
    is_unlocked = models.BooleanField(default=False)
    unlock_error = models.TextField(blank=True, default="")
    last_synced = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Episode"
        verbose_name_plural = "Episodes"
        unique_together = ['drama', 'episode_number']
        ordering = ['drama', 'episode_number']

    def __str__(self):
        return f"{self.drama.name} - Episode {self.episode_number}"


class SyncLog(models.Model):
    """Log for tracking sync operations."""
    
    SYNC_TYPE_CHOICES = [
        ('full', 'Full Sync'),
        ('drama', 'Single Drama'),
        ('episodes', 'Episodes Only'),
    ]
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    dramas_synced = models.IntegerField(default=0)
    episodes_synced = models.IntegerField(default=0)
    errors = models.TextField(blank=True, default="")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Sync Log"
        verbose_name_plural = "Sync Logs"
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.sync_type} - {self.status} ({self.started_at})"
