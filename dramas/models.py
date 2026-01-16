from django.db import models


class JoliboxConfig(models.Model):
    """Configuration model for storing Jolibox API credentials."""
    
    name = models.CharField(max_length=100, help_text="Config identifier (e.g., 'Production', 'Test')")
    joli_source_token = models.TextField(help_text="Jolibox API source token")
    device_id = models.CharField(max_length=255, help_text="Device identifier")
    is_active = models.BooleanField(default=True, help_text="Only active config will be used")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Jolibox Configuration"
        verbose_name_plural = "Jolibox Configurations"

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"

    @classmethod
    def get_active_config(cls):
        """Get the first active configuration."""
        return cls.objects.filter(is_active=True).first()
