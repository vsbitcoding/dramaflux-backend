from django.contrib import admin
from django.utils.html import format_html
from .models import JoliboxConfig, Drama, Episode, SyncLog


@admin.register(JoliboxConfig)
class JoliboxConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'joli_source_token', 'device_id')
    list_editable = ('joli_source_token', 'device_id')
    list_display_links = None

    def has_add_permission(self, request):
        """Disable add - only one record allowed."""
        if not JoliboxConfig.objects.exists():
            JoliboxConfig.objects.create()
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 0
    readonly_fields = ('episode_number', 'is_unlocked', 'video_url', 'unlock_error', 'last_synced')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Drama)
class DramaAdmin(admin.ModelAdmin):
    list_display = ('name', 'drama_id', 'episode_count', 'synced_episodes_display', 'views', 'is_active', 'last_synced')
    list_filter = ('is_active', 'orientation', 'status')
    search_fields = ('name', 'drama_id', 'description')
    readonly_fields = ('drama_id', 'last_synced', 'created_at')
    inlines = [EpisodeInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('drama_id', 'name', 'description', 'is_active')
        }),
        ('Media', {
            'fields': ('cover_url', 'logo_url', 'orientation')
        }),
        ('Metadata', {
            'fields': ('episode_count', 'views', 'categories', 'status', 'host_mode', 'content_provider_id')
        }),
        ('Sync Info', {
            'fields': ('last_synced', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Synced')
    def synced_episodes_display(self, obj):
        total = obj.episodes.count()
        unlocked = obj.episodes.filter(is_unlocked=True).count()
        if total == 0:
            return "0/0"
        color = 'green' if unlocked == total else 'orange'
        return format_html('<span style="color: {};">{}/{}</span>', color, unlocked, total)


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('drama', 'episode_number', 'is_unlocked', 'has_video_display', 'last_synced')
    list_filter = ('is_unlocked', 'drama')
    search_fields = ('drama__name', 'drama__drama_id')
    readonly_fields = ('drama', 'episode_number', 'video_url', 'is_unlocked', 'unlock_error', 'last_synced', 'created_at')
    
    @admin.display(description='Video', boolean=True)
    def has_video_display(self, obj):
        return bool(obj.video_url)


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ('sync_type', 'status', 'dramas_synced', 'episodes_synced', 'started_at', 'duration_display')
    list_filter = ('sync_type', 'status')
    readonly_fields = ('sync_type', 'status', 'dramas_synced', 'episodes_synced', 'errors', 'started_at', 'completed_at')
    
    @admin.display(description='Duration')
    def duration_display(self, obj):
        if obj.completed_at:
            return str(obj.completed_at - obj.started_at)
        return 'Running...'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
