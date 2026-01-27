from django.db import models

class AdConfig(models.Model):
    AD_TYPES = [
        ('HOME_FEED', 'Home Feed'),
        ('DRAMA_PLAYER', 'Drama Player'),
        ('BETWEEN_ROWS', 'Between Rows'),
    ]

    name = models.CharField(max_length=100, help_text="Internal name for the ad configuration")
    ad_type = models.CharField(max_length=20, choices=AD_TYPES)
    code = models.TextField(help_text="The HTML/Script code for the ad")
    sequence = models.IntegerField(default=1, help_text="Frequency of the ad. E.g., 2 means every 2nd item/episode. (Ignored if show_random is True)")
    
    # Random sequence fields
    show_random = models.BooleanField(default=False, help_text="If enabled, uses random interval between random_min and random_max instead of fixed sequence")
    random_min = models.IntegerField(default=2, help_text="Minimum interval for random sequence (e.g., 2)")
    random_max = models.IntegerField(default=5, help_text="Maximum interval for random sequence (e.g., 5)")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_ad_type_display()})"
