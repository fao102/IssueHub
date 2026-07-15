from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Ticket, TicketActivity

User = get_user_model()


def make_user(email, is_staff=False):
    return User.objects.create_user(email=email, password="S3cure-Passw0rd!", is_staff=is_staff)


class CategoryTests(APITestCase):
    def setUp(self):
        self.user = make_user("user@example.com")
        self.staff = make_user("staff@example.com", is_staff=True)
        self.category = Category.objects.create(name="Networking")

    def test_authenticated_user_can_list_categories(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("category-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_list_categories(self):
        response = self.client.get(reverse("category-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_category(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse("category-list"), {"name": "Hardware"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_staff_cannot_update_category(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(reverse("category-detail", args=[self.category.id]), {"name": "Renamed"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_staff_cannot_delete_category(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(reverse("category-detail", args=[self.category.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_update_and_delete_category(self):
        self.client.force_authenticate(self.staff)
        update = self.client.patch(reverse("category-detail", args=[self.category.id]), {"name": "Renamed"})
        self.assertEqual(update.status_code, status.HTTP_200_OK)

        delete = self.client.delete(reverse("category-detail", args=[self.category.id]))
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)


class TicketCRUDTests(APITestCase):
    def setUp(self):
        self.owner = make_user("owner@example.com")
        self.other_user = make_user("other@example.com")
        self.staff = make_user("staff@example.com", is_staff=True)
        self.category = Category.objects.create(name="Networking")

    def test_create_ticket_sets_creator_and_logs_activity(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            reverse("ticket-list"),
            {"title": "Printer is broken", "description": "It won't turn on", "category_id": self.category.id},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        ticket = Ticket.objects.get(id=response.data["id"])
        self.assertEqual(ticket.created_by, self.owner)
        self.assertEqual(ticket.status, Ticket.Status.OPEN)

        activity = TicketActivity.objects.filter(ticket=ticket)
        self.assertEqual(activity.count(), 1)
        self.assertEqual(activity.first().action, TicketActivity.Action.CREATED)

    def test_owner_can_retrieve_own_ticket_with_activity(self):
        self.client.force_authenticate(self.owner)
        create = self.client.post(reverse("ticket-list"), {"title": "Ticket A"})
        ticket_id = create.data["id"]

        response = self.client.get(reverse("ticket-detail", args=[ticket_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("activity", response.data)
        self.assertEqual(len(response.data["activity"]), 1)

    def test_unrelated_user_cannot_see_ticket(self):
        self.client.force_authenticate(self.owner)
        create = self.client.post(reverse("ticket-list"), {"title": "Private ticket"})
        ticket_id = create.data["id"]

        self.client.force_authenticate(self.other_user)
        response = self.client.get(reverse("ticket-detail", args=[ticket_id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_staff_sees_all_tickets(self):
        self.client.force_authenticate(self.owner)
        self.client.post(reverse("ticket-list"), {"title": "Owner's ticket"})

        self.client.force_authenticate(self.staff)
        response = self.client.get(reverse("ticket-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_update_ticket_logs_status_and_priority_changes(self):
        self.client.force_authenticate(self.owner)
        create = self.client.post(reverse("ticket-list"), {"title": "Ticket to update"})
        ticket_id = create.data["id"]

        response = self.client.patch(
            reverse("ticket-detail", args=[ticket_id]), {"status": "resolved", "priority": "high"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        actions = list(
            TicketActivity.objects.filter(ticket_id=ticket_id).values_list("action", flat=True)
        )
        self.assertIn(TicketActivity.Action.STATUS_CHANGED, actions)
        self.assertIn(TicketActivity.Action.PRIORITY_CHANGED, actions)

    def test_delete_ticket(self):
        self.client.force_authenticate(self.owner)
        create = self.client.post(reverse("ticket-list"), {"title": "To delete"})
        ticket_id = create.data["id"]

        response = self.client.delete(reverse("ticket-detail", args=[ticket_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ticket.objects.filter(id=ticket_id).exists())

    def test_filter_by_status(self):
        self.client.force_authenticate(self.owner)
        open_ticket = self.client.post(reverse("ticket-list"), {"title": "Open one"}).data
        resolved = self.client.post(reverse("ticket-list"), {"title": "Resolved one"}).data
        self.client.patch(reverse("ticket-detail", args=[resolved["id"]]), {"status": "resolved"})

        response = self.client.get(reverse("ticket-list"), {"status": "resolved"})
        ids = [t["id"] for t in response.data["results"]]
        self.assertIn(resolved["id"], ids)
        self.assertNotIn(open_ticket["id"], ids)


class TicketAssignmentTests(APITestCase):
    def setUp(self):
        self.owner = make_user("owner@example.com")
        self.staff = make_user("staff@example.com", is_staff=True)
        self.other_staff = make_user("staff2@example.com", is_staff=True)

    def test_non_staff_cannot_assign_ticket(self):
        self.client.force_authenticate(self.owner)
        create = self.client.post(reverse("ticket-list"), {"title": "Needs help"})
        ticket_id = create.data["id"]

        response = self.client.patch(
            reverse("ticket-detail", args=[ticket_id]), {"assigned_to_id": self.staff.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_assign_to_non_staff_user(self):
        non_staff = make_user("nobody@example.com")
        self.client.force_authenticate(self.staff)
        create = self.client.post(reverse("ticket-list"), {"title": "Needs help"})
        ticket_id = create.data["id"]

        response = self.client.patch(
            reverse("ticket-detail", args=[ticket_id]), {"assigned_to_id": non_staff.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_can_assign_ticket_to_staff_and_it_becomes_visible(self):
        self.client.force_authenticate(self.owner)
        create = self.client.post(reverse("ticket-list"), {"title": "Needs help"})
        ticket_id = create.data["id"]

        self.client.force_authenticate(self.staff)
        response = self.client.patch(
            reverse("ticket-detail", args=[ticket_id]), {"assigned_to_id": self.other_staff.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        activity = TicketActivity.objects.filter(ticket_id=ticket_id, action=TicketActivity.Action.ASSIGNED)
        self.assertEqual(activity.count(), 1)

        self.client.force_authenticate(self.other_staff)
        detail = self.client.get(reverse("ticket-detail", args=[ticket_id]))
        self.assertEqual(detail.status_code, status.HTTP_200_OK)

    def test_assignable_users_endpoint_is_staff_only(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(reverse("ticket-assignable-users"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.staff)
        response = self.client.get(reverse("ticket-assignable-users"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = [u["email"] for u in response.data]
        self.assertIn(self.staff.email, emails)
        self.assertIn(self.other_staff.email, emails)


class TicketDashboardTests(APITestCase):
    def setUp(self):
        self.owner = make_user("owner@example.com")
        self.other_user = make_user("other@example.com")
        self.staff = make_user("staff@example.com", is_staff=True)

    def test_dashboard_scoped_to_visible_tickets(self):
        self.client.force_authenticate(self.owner)
        self.client.post(reverse("ticket-list"), {"title": "Owner ticket 1"})
        self.client.post(reverse("ticket-list"), {"title": "Owner ticket 2"})

        self.client.force_authenticate(self.other_user)
        self.client.post(reverse("ticket-list"), {"title": "Other user's ticket"})

        self.client.force_authenticate(self.owner)
        response = self.client.get(reverse("ticket-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 2)
        self.assertEqual(response.data["by_status"]["open"], 2)
        self.assertEqual(len(response.data["recent_tickets"]), 2)

    def test_dashboard_staff_sees_everything(self):
        self.client.force_authenticate(self.owner)
        self.client.post(reverse("ticket-list"), {"title": "Owner ticket"})
        self.client.force_authenticate(self.other_user)
        self.client.post(reverse("ticket-list"), {"title": "Other ticket"})

        self.client.force_authenticate(self.staff)
        response = self.client.get(reverse("ticket-dashboard"))
        self.assertEqual(response.data["total"], 2)
