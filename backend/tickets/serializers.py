from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import MinimalUserSerializer

from .models import Category, Ticket, TicketActivity

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]


class TicketActivitySerializer(serializers.ModelSerializer):
    actor = MinimalUserSerializer(read_only=True)
    ticket_id = serializers.UUIDField(source="ticket.id", read_only=True)
    ticket_title = serializers.CharField(source="ticket.title", read_only=True)

    class Meta:
        model = TicketActivity
        fields = ["id", "ticket_id", "ticket_title", "actor", "action", "detail", "created_at"]
        read_only_fields = fields


class TicketSerializer(serializers.ModelSerializer):
    created_by = MinimalUserSerializer(read_only=True)
    assigned_to = MinimalUserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True, required=False, allow_null=True
    )
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        source="assigned_to",
        queryset=User.objects.filter(is_staff=True),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "description",
            "category",
            "category_id",
            "priority",
            "status",
            "created_by",
            "assigned_to",
            "assigned_to_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def validate(self, attrs):
        if "assigned_to" in attrs:
            request = self.context["request"]
            if not request.user.is_staff:
                raise serializers.ValidationError(
                    {"assigned_to_id": "Only staff can assign tickets."}
                )
        return attrs


class TicketDetailSerializer(TicketSerializer):
    activity = TicketActivitySerializer(many=True, read_only=True)

    class Meta(TicketSerializer.Meta):
        fields = TicketSerializer.Meta.fields + ["activity"]
