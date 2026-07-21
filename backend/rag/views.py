from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from tickets.models import Ticket

from .models import KnowledgeEntry
from .serializers import RagQuerySerializer


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

        entries = KnowledgeEntry.objects.order_by("-created_at")[:5]
        sources = []
        for entry in entries:
            sources.append(
                {
                    "id": str(entry.id),
                    "title": entry.title,
                    "source_type": entry.source_type,
                    "content": entry.content[:220],
                }
            )

        context_parts = [entry.content for entry in entries]
        if ticket is not None:
            context_parts.append(
                f"Ticket title: {ticket.title}\nTicket description: {ticket.description or 'No description provided.'}"
            )

        context = "\n\n".join(context_parts)
        answer = (
            f"Based on the available knowledge, here is a grounded suggestion for your question: {question}."
            f"\n\nContext used:\n{context[:1000]}"
        )

        return Response(
            {
                "answer": answer,
                "sources": sources,
                "ticket_id": str(ticket.id) if ticket else None,
            },
            status=status.HTTP_200_OK,
        )
