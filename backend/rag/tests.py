from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from rag.models import KnowledgeEntry
from tickets.models import Category, Ticket

User = get_user_model()


def make_user(email, is_staff=False):
    return User.objects.create_user(email=email, password="S3cure-Passw0rd!", is_staff=is_staff)


class RagQueryTests(TestCase):
    def setUp(self):
        self.user = make_user("agent@example.com")
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
        self.vpn_entry = KnowledgeEntry.objects.create(
            title="VPN troubleshooting",
            content="If the VPN is not connecting, restart the client and verify the network connection.",
            source_type="article",
        )
        self.printer_entry = KnowledgeEntry.objects.create(
            title="Printer setup",
            content="To install a printer, download the HP driver package from the intranet portal.",
            source_type="article",
        )

    def test_query_endpoint_returns_answer_and_sources(self):
        # Original stub-era contract: answer + at least one source.
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

    def test_retrieval_ranks_semantically_relevant_entry_first(self):
        # The local embedding is real (not a constant), so a VPN question should
        # surface the VPN article ahead of the printer article.
        response = self.client.post(
            "/api/rag/query/",
            {"question": "my vpn will not connect from home"},
            format="json",
        )
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["sources"][0]["title"], "VPN troubleshooting")

    def test_query_without_llm_is_extractive_and_reports_not_configured(self):
        response = self.client.post(
            "/api/rag/query/", {"question": "how do I fix the vpn?"}, format="json"
        )
        body = response.json()
        self.assertFalse(body["configured"])
        # Extractive answer should surface the relevant article's content.
        self.assertIn("restart the client", body["answer"].lower())

    @override_settings(RAG_LLM_PROVIDER="mock")
    def test_query_with_llm_provider_reports_configured(self):
        response = self.client.post(
            "/api/rag/query/", {"question": "how do I fix the vpn?"}, format="json"
        )
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["configured"])
        self.assertTrue(body["answer"])

    def test_query_with_empty_knowledge_base(self):
        KnowledgeEntry.objects.all().delete()
        response = self.client.post("/api/rag/query/", {"question": "anything?"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sources"], [])

    def test_query_requires_authentication(self):
        self.client.force_authenticate(None)
        response = self.client.post("/api/rag/query/", {"question": "hi"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class KnowledgeEntryCRUDTests(APITestCase):
    def setUp(self):
        self.user = make_user("user@example.com")
        self.staff = make_user("staff@example.com", is_staff=True)
        self.entry = KnowledgeEntry.objects.create(title="Existing", content="Some content.")

    def test_authenticated_user_can_list_and_read(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get(reverse("knowledge-list")).status_code, status.HTTP_200_OK)
        detail = self.client.get(reverse("knowledge-detail", args=[self.entry.id]))
        self.assertEqual(detail.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_list(self):
        self.assertEqual(self.client.get(reverse("knowledge-list")).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_staff_cannot_create(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("knowledge-list"), {"title": "New", "content": "Body"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create_update_delete(self):
        self.client.force_authenticate(self.staff)
        created = self.client.post(
            reverse("knowledge-list"),
            {"title": "How to reset password", "content": "Use the reset link.", "source_type": "faq"},
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        entry_id = created.data["id"]

        updated = self.client.patch(
            reverse("knowledge-detail", args=[entry_id]), {"title": "How to reset your password"}
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)

        deleted = self.client.delete(reverse("knowledge-detail", args=[entry_id]))
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(KnowledgeEntry.objects.filter(id=entry_id).exists())
