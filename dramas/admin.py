from django.contrib import admin
from .models import JoliboxConfig


@admin.register(JoliboxConfig)
class JoliboxConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'device_id', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'device_id')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Configuration', {
            'fields': ('name', 'is_active')
        }),
        ('API Credentials', {
            'fields': ('joli_source_token', 'device_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
