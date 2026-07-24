from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import KnowledgeEntryViewSet, RagQueryView

router = DefaultRouter()
router.register("knowledge", KnowledgeEntryViewSet, basename="knowledge")

urlpatterns = [
    path("rag/query/", RagQueryView.as_view(), name="rag-query"),
    path("", include(router.urls)),
]
