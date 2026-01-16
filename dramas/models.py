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
