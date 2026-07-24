"""Provider-agnostic seam for the RAG pipeline.

Everything the pipeline needs from an LLM/embedding vendor is obtained through
``get_embed_model()`` and ``get_llm()``. Swapping providers (or wiring a real
API key in for the first time) is a matter of settings only - no other module
imports a vendor SDK directly. Vendor packages are imported lazily so the base
install (``llama-index-core`` only) stays lean and import-safe.
"""

import hashlib
import math
import re
from typing import List

from django.conf import settings
from llama_index.core.base.embeddings.base import BaseEmbedding


class LocalHashingEmbedding(BaseEmbedding):
    """A tiny deterministic bag-of-words embedding.

    It needs no API key, no model download and no network, yet produces
    genuine similarity ordering (tokens are hashed into a fixed-width vector,
    tf-weighted and L2-normalised). It is the default so retrieval works out of
    the box; swap in a real provider for higher-quality embeddings.
    """

    dim: int = 256

    @staticmethod
    def _tokens(text: str) -> List[str]:
        return re.findall(r"[a-z0-9]+", text.lower())

    def _embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        for token in self._tokens(text):
            bucket = int(hashlib.md5(token.encode()).hexdigest(), 16) % self.dim
            vec[bucket] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def _get_query_embedding(self, query: str) -> List[float]:
        return self._embed(query)

    def _get_text_embedding(self, text: str) -> List[float]:
        return self._embed(text)

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._embed(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._embed(text)


def get_embed_model():
    """Return a LlamaIndex embedding model for the configured provider.

    Never returns None - retrieval always has an embedding to work with
    (defaulting to the local no-key model).
    """
    provider = settings.RAG_EMBED_PROVIDER.lower()

    if provider in ("local", "mock"):
        return LocalHashingEmbedding()

    if provider == "gemini":
        from llama_index.embeddings.gemini import GeminiEmbedding

        return GeminiEmbedding(model_name=settings.GEMINI_EMBED_MODEL, api_key=settings.GEMINI_API_KEY)

    if provider == "openai":
        from llama_index.embeddings.openai import OpenAIEmbedding

        return OpenAIEmbedding(model=settings.OPENAI_EMBED_MODEL, api_key=settings.OPENAI_API_KEY)

    raise ValueError(f"Unknown RAG_EMBED_PROVIDER: {settings.RAG_EMBED_PROVIDER!r}")


def get_llm():
    """Return a LlamaIndex LLM for the configured provider, or None.

    None means "no answer-generation model configured" - the pipeline then
    returns an extractive answer built from the retrieved snippets instead of a
    generated one.
    """
    provider = settings.RAG_LLM_PROVIDER.lower()

    if provider == "none":
        return None

    if provider == "mock":
        from llama_index.core.llms import MockLLM

        return MockLLM(max_tokens=256)

    if provider == "gemini":
        if not settings.GEMINI_API_KEY:
            return None
        from llama_index.llms.gemini import Gemini

        return Gemini(model=settings.GEMINI_LLM_MODEL, api_key=settings.GEMINI_API_KEY)

    if provider == "openai":
        if not settings.OPENAI_API_KEY:
            return None
        from llama_index.llms.openai import OpenAI

        return OpenAI(model=settings.OPENAI_LLM_MODEL, api_key=settings.OPENAI_API_KEY)

    raise ValueError(f"Unknown RAG_LLM_PROVIDER: {settings.RAG_LLM_PROVIDER!r}")
