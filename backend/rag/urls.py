from django.urls import path

from .views import RagQueryView

urlpatterns = [path("rag/query/", RagQueryView.as_view(), name="rag-query")]
