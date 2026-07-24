"""The RAG pipeline: chunk -> embed -> vector index -> retrieve -> answer.

Built on LlamaIndex. Two vector backends are supported (selected by
``settings.RAG_VECTOR_BACKEND``):

* ``memory`` (default) - an in-memory ``VectorStoreIndex`` rebuilt from
  ``KnowledgeEntry`` rows on demand. Zero external dependencies; great for dev,
  tests and small knowledge bases.
* ``pgvector`` - a persistent LlamaIndex ``PGVectorStore`` (Postgres +
  pgvector). Content is embedded and upserted on save (``ingest_entry``).

Answer generation degrades gracefully: if no LLM provider is configured the
pipeline returns an *extractive* answer built from the retrieved snippets and
reports ``configured: False`` so the UI can say so.
"""

import logging

from django.conf import settings

from .models import KnowledgeEntry
from .providers import get_embed_model, get_llm

logger = logging.getLogger(__name__)

_ANSWER_PROMPT = (
    "You are IssueHub's support assistant. Answer the user's question using ONLY "
    "the context below. If the context does not contain the answer, say you don't "
    "have enough information. Be concise.\n\n"
    "{ticket_context}"
    "Context:\n{context}\n\n"
    "Question: {question}\n\nAnswer:"
)


def is_llm_configured() -> bool:
    """True when a real answer-generation model is available."""
    try:
        return get_llm() is not None
    except Exception:
        logger.exception("Failed to construct RAG LLM")
        return False


def _splitter():
    from llama_index.core.node_parser import SentenceSplitter

    return SentenceSplitter(
        chunk_size=settings.RAG_CHUNK_SIZE, chunk_overlap=settings.RAG_CHUNK_OVERLAP
    )


def _documents_from_entries(entries):
    from llama_index.core import Document

    return [
        Document(
            text=entry.content,
            metadata={
                "entry_id": str(entry.id),
                "title": entry.title,
                "source_type": entry.source_type,
            },
            excluded_embed_metadata_keys=["entry_id", "source_type"],
            excluded_llm_metadata_keys=["entry_id", "source_type"],
        )
        for entry in entries
    ]


def _pgvector_store():
    from llama_index.vector_stores.postgres import PGVectorStore

    return PGVectorStore.from_params(
        connection_string=settings.RAG_PGVECTOR_URL,
        table_name="rag_knowledge_embeddings",
        embed_dim=settings.RAG_EMBED_DIM,
    )


def _build_index(entries=None):
    """Return a queryable VectorStoreIndex for the configured backend."""
    from llama_index.core import StorageContext, VectorStoreIndex

    embed_model = get_embed_model()

    if settings.RAG_VECTOR_BACKEND == "pgvector":
        store = _pgvector_store()
        return VectorStoreIndex.from_vector_store(store, embed_model=embed_model)

    # memory backend: rebuild from rows each call
    if entries is None:
        entries = KnowledgeEntry.objects.all()
    documents = _documents_from_entries(entries)
    storage_context = StorageContext.from_defaults()
    return VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
        transformations=[_splitter()],
    )


# --- Ingestion (only meaningful for the persistent pgvector backend) ---------


def ingest_entry(entry) -> None:
    """Embed & upsert a single KnowledgeEntry into the persistent store."""
    if settings.RAG_VECTOR_BACKEND != "pgvector":
        return
    try:
        from llama_index.core import VectorStoreIndex

        remove_entry(entry)
        index = VectorStoreIndex.from_vector_store(_pgvector_store(), embed_model=get_embed_model())
        for node in _splitter().get_nodes_from_documents(_documents_from_entries([entry])):
            index.insert_nodes([node])
    except Exception:
        logger.exception("RAG ingest failed for KnowledgeEntry %s", entry.id)


def remove_entry(entry) -> None:
    """Delete a KnowledgeEntry's nodes from the persistent store."""
    if settings.RAG_VECTOR_BACKEND != "pgvector":
        return
    try:
        store = _pgvector_store()
        store.delete(str(entry.id))
    except Exception:
        logger.exception("RAG delete failed for KnowledgeEntry %s", entry.id)


# --- Query -------------------------------------------------------------------


def _sources_from_nodes(nodes):
    sources = []
    seen = set()
    for node in nodes:
        meta = node.metadata or {}
        entry_id = meta.get("entry_id")
        if entry_id in seen:
            continue
        seen.add(entry_id)
        sources.append(
            {
                "id": entry_id,
                "title": meta.get("title", "Untitled"),
                "source_type": meta.get("source_type", "article"),
                "content": (node.get_content() or "")[:220],
            }
        )
    return sources


def _ticket_context(ticket) -> str:
    if ticket is None:
        return ""
    return (
        "The user is viewing this support ticket:\n"
        f"Title: {ticket.title}\n"
        f"Description: {ticket.description or 'No description provided.'}\n\n"
    )


def answer_question(question: str, ticket=None) -> dict:
    """Retrieve relevant knowledge and answer the question.

    Returns ``{answer, sources, configured}``. ``configured`` is False when no
    LLM provider is wired up (the answer is then extractive, not generated).
    """
    if not KnowledgeEntry.objects.exists():
        return {
            "answer": "The knowledge base is empty. Add knowledge articles to get grounded answers.",
            "sources": [],
            "configured": is_llm_configured(),
        }

    try:
        index = _build_index()
        nodes = index.as_retriever(similarity_top_k=settings.RAG_TOP_K).retrieve(question)
    except Exception:
        logger.exception("RAG retrieval failed")
        return _fallback_answer(question, reason="retrieval_error")

    sources = _sources_from_nodes(nodes)
    llm = None
    try:
        llm = get_llm()
    except Exception:
        logger.exception("RAG LLM construction failed")

    if llm is None:
        return _extractive_answer(question, nodes, sources)

    context = "\n\n".join(node.get_content() for node in nodes)
    prompt = _ANSWER_PROMPT.format(
        ticket_context=_ticket_context(ticket), context=context, question=question
    )
    try:
        response = llm.complete(prompt)
        return {"answer": str(response).strip(), "sources": sources, "configured": True}
    except Exception:
        logger.exception("RAG answer generation failed")
        return _extractive_answer(question, nodes, sources)


def _extractive_answer(question, nodes, sources) -> dict:
    """Answer built directly from the top retrieved snippets (no LLM)."""
    if not nodes:
        return _fallback_answer(question, reason="no_results")
    snippets = "\n\n".join(f"- {node.get_content().strip()}" for node in nodes[:3])
    answer = (
        "No answer-generation model is configured, so here are the most relevant "
        f"knowledge-base excerpts for your question:\n\n{snippets}"
    )
    return {"answer": answer, "sources": sources, "configured": False}


def _fallback_answer(question, reason) -> dict:
    """Last resort when the index/retrieval is unavailable: recency retrieval."""
    entries = KnowledgeEntry.objects.order_by("-created_at")[:5]
    sources = [
        {
            "id": str(entry.id),
            "title": entry.title,
            "source_type": entry.source_type,
            "content": entry.content[:220],
        }
        for entry in entries
    ]
    answer = (
        "Showing recent knowledge-base articles that may be related to your "
        "question. (The semantic search layer was unavailable.)"
    )
    return {"answer": answer, "sources": sources, "configured": False}
