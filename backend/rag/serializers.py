from rest_framework import serializers

from .models import KnowledgeEntry


class RagQuerySerializer(serializers.Serializer):
    question = serializers.CharField(required=True, allow_blank=False)
    ticket_id = serializers.CharField(required=False, allow_blank=True, default="")


class KnowledgeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeEntry
        fields = [
            "id",
            "title",
            "content",
            "source_type",
            "source_id",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
