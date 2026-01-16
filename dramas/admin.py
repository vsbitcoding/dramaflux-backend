from django.contrib import admin
from .models import JoliboxConfig


@admin.register(JoliboxConfig)
class JoliboxConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'joli_source_token', 'device_id')
    list_editable = ('joli_source_token', 'device_id')
    list_display_links = None

    def has_add_permission(self, request):
        """Disable add - only one record allowed."""
        if not JoliboxConfig.objects.exists():
            JoliboxConfig.objects.create()  # Auto-create single record
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable delete - always keep one record."""
        return False
