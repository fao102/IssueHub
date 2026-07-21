from rest_framework import serializers


class RagQuerySerializer(serializers.Serializer):
    question = serializers.CharField(required=True, allow_blank=False)
    ticket_id = serializers.CharField(required=False, allow_blank=True, default="")
