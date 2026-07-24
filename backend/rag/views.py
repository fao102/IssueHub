from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from tickets.models import Ticket

from . import services
from .models import KnowledgeEntry
from .permissions import IsStaffOrReadOnly
from .serializers import KnowledgeEntrySerializer, RagQuerySerializer


class KnowledgeEntryViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeEntry.objects.all()
    serializer_class = KnowledgeEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def perform_create(self, serializer):
        entry = serializer.save()
        services.ingest_entry(entry)

    def perform_update(self, serializer):
        entry = serializer.save()
        services.ingest_entry(entry)

    def perform_destroy(self, instance):
        services.remove_entry(instance)
        instance.delete()


class RagQueryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RagQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data["question"]
        ticket_id = serializer.validated_data.get("ticket_id", "").strip()

        ticket = None
        if ticket_id:
            ticket = get_object_or_404(Ticket, id=ticket_id)

        result = services.answer_question(question, ticket=ticket)

        return Response(
            {
                "answer": result["answer"],
                "sources": result["sources"],
                "configured": result["configured"],
                "ticket_id": str(ticket.id) if ticket else None,
            },
            status=status.HTTP_200_OK,
        )
