from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import MinimalUserSerializer

from .models import Category, Ticket, TicketActivity
from .permissions import IsStaffOrReadCreateOnly
from .serializers import CategorySerializer, TicketActivitySerializer, TicketDetailSerializer, TicketSerializer

User = get_user_model()


def _visible_tickets(user):
    if user.is_staff:
        return Ticket.objects.all()
    return Ticket.objects.filter(Q(created_by=user) | Q(assigned_to=user))


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadCreateOnly]


class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = _visible_tickets(self.request.user).select_related("category", "created_by", "assigned_to")

        params = self.request.query_params
        if status_param := params.get("status"):
            qs = qs.filter(status=status_param)
        if priority_param := params.get("priority"):
            qs = qs.filter(priority=priority_param)
        if category_param := params.get("category"):
            qs = qs.filter(category_id=category_param)
        if search := params.get("search"):
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TicketDetailSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        ticket = serializer.save(created_by=self.request.user)
        TicketActivity.objects.create(
            ticket=ticket,
            actor=self.request.user,
            action=TicketActivity.Action.CREATED,
            detail="Ticket created",
        )

    def perform_update(self, serializer):
        ticket = serializer.instance
        before_status = ticket.status
        before_priority = ticket.priority
        before_category_id = ticket.category_id
        before_category_name = str(ticket.category) if ticket.category else "None"
        before_assignee_id = ticket.assigned_to_id
        before_assignee_name = str(ticket.assigned_to) if ticket.assigned_to else "Unassigned"

        ticket = serializer.save()

        entries = []
        if before_status != ticket.status:
            entries.append(
                (
                    TicketActivity.Action.STATUS_CHANGED,
                    f"Status changed from {Ticket.Status(before_status).label} to {ticket.get_status_display()}",
                )
            )
        if before_priority != ticket.priority:
            entries.append(
                (
                    TicketActivity.Action.PRIORITY_CHANGED,
                    f"Priority changed from {Ticket.Priority(before_priority).label} to "
                    f"{ticket.get_priority_display()}",
                )
            )
        if before_category_id != ticket.category_id:
            new_name = str(ticket.category) if ticket.category else "None"
            entries.append(
                (
                    TicketActivity.Action.CATEGORY_CHANGED,
                    f"Category changed from {before_category_name} to {new_name}",
                )
            )
        if before_assignee_id != ticket.assigned_to_id:
            new_name = str(ticket.assigned_to) if ticket.assigned_to else "Unassigned"
            entries.append(
                (
                    TicketActivity.Action.ASSIGNED,
                    f"Assignee changed from {before_assignee_name} to {new_name}",
                )
            )

        for action, detail in entries:
            TicketActivity.objects.create(ticket=ticket, actor=self.request.user, action=action, detail=detail)


class AssignableUsersView(generics.ListAPIView):
    serializer_class = MinimalUserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.filter(is_staff=True).order_by("email")
    pagination_class = None


class TicketDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = _visible_tickets(request.user)

        by_status = {value: qs.filter(status=value).count() for value, _ in Ticket.Status.choices}
        by_priority = {value: qs.filter(priority=value).count() for value, _ in Ticket.Priority.choices}

        recent_tickets = qs.select_related("category", "created_by", "assigned_to")[:5]
        recent_activity = TicketActivity.objects.filter(ticket__in=qs).select_related("actor", "ticket")[:10]

        return Response(
            {
                "total": qs.count(),
                "by_status": by_status,
                "by_priority": by_priority,
                "recent_tickets": TicketSerializer(recent_tickets, many=True, context={"request": request}).data,
                "recent_activity": TicketActivitySerializer(recent_activity, many=True).data,
            }
        )
