from django.contrib import admin
from .models import AdConfig

@admin.register(AdConfig)
class AdConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'ad_type', 'sequence', 'show_random', 'random_min', 'random_max', 'is_active', 'updated_at')
    list_editable = ('sequence', 'show_random', 'random_min', 'random_max', 'is_active')
    search_fields = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'ad_type', 'code', 'is_active')
        }),
        ('Sequence Settings', {
            'fields': ('sequence', 'show_random', 'random_min', 'random_max'),
            'description': 'Configure how often ads appear. Enable "show_random" to use random intervals instead of fixed sequence.'
        }),
    )
