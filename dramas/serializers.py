from rest_framework import serializers


class DramaSerializer(serializers.Serializer):
    """Serializer for drama data."""
    dramaId = serializers.CharField()
    name = serializers.CharField()
    episodeCount = serializers.IntegerField()
    orientation = serializers.CharField()
    views = serializers.IntegerField()
    status = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True)
    cover = serializers.URLField(allow_blank=True, allow_null=True)
    logo = serializers.URLField(allow_blank=True, allow_null=True)
    categories = serializers.ListField(child=serializers.CharField(), allow_null=True)
    channelActive = serializers.BooleanField()


class EpisodeSerializer(serializers.Serializer):
    """Serializer for episode data."""
    episodeId = serializers.CharField()
    episodeNumber = serializers.IntegerField()
    title = serializers.CharField(allow_blank=True, allow_null=True)
    duration = serializers.IntegerField(allow_null=True)
    videoUrl = serializers.URLField(allow_blank=True, allow_null=True)
    thumbnail = serializers.URLField(allow_blank=True, allow_null=True)


class APIResponseSerializer(serializers.Serializer):
    """Serializer for API response wrapper."""
    code = serializers.CharField()
    message = serializers.CharField()
    data = serializers.ListField(allow_null=True)
