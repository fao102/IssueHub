from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from rag.models import KnowledgeEntry
from tickets.models import Category, Ticket


class RagQueryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="agent@example.com", password="pass1234")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.category = Category.objects.create(name="Networking")
        self.ticket = Ticket.objects.create(
            title="VPN not connecting",
            description="User cannot connect to the VPN from home.",
            category=self.category,
            created_by=self.user,
            status=Ticket.Status.RESOLVED,
            priority=Ticket.Priority.HIGH,
        )
        self.knowledge_entry = KnowledgeEntry.objects.create(
            title="VPN troubleshooting",
            content="If the VPN is not connecting, restart the client and verify the network connection.",
            source_type="article",
        )

    def test_query_endpoint_returns_answer_and_sources(self):
        response = self.client.post(
            "/api/rag/query/",
            {"question": "How can I fix VPN connection issues?", "ticket_id": str(self.ticket.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("answer", body)
        self.assertIn("sources", body)
        self.assertGreater(len(body["sources"]), 0)
