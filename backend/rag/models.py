from django.db import models

from core.models import BaseModel


class KnowledgeEntry(BaseModel):
    SOURCE_TYPES = (
        ("article", "Article"),
        ("ticket", "Ticket"),
        ("faq", "FAQ"),
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, default="article")
    source_id = models.CharField(max_length=255, blank=True, default="")
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
