from django.contrib import admin

from .models import KnowledgeEntry


@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
    list_display = ["title", "source_type", "created_at", "updated_at"]
    list_filter = ["source_type"]
    search_fields = ["title", "content"]
