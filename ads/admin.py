from django.contrib import admin
from .models import AdConfig

@admin.register(AdConfig)
class AdConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'ad_type', 'sequence', 'is_active', 'updated_at')
    list_filter = ('ad_type', 'is_active')
    search_fields = ('name',)
