# RAG / AI Assistant — what you need to plug in

The RAG (Retrieval-Augmented Generation) feature is built on **LlamaIndex** and
is **provider-agnostic**. It runs with **zero setup** out of the box:

- **Retrieval always works.** The default embedding is a small local,
  deterministic model (no API key, no download, no network), and the default
  vector store is rebuilt in-memory from your knowledge articles.
- **Answers are extractive by default.** Without an LLM key, the assistant
  returns the most relevant knowledge-base excerpts and labels itself
  "not configured." Add a provider key to get *generated* answers.

So nothing below is required to demo the feature. This doc lists what to plug
in **when you want the fuller experience** (real generated answers and/or a
production-grade persistent vector store).

---

## TL;DR — the three things you might plug in

| Want… | Do this |
|---|---|
| Generated answers (not just excerpts) | Install a provider, set `RAG_LLM_PROVIDER` + its API key |
| Higher-quality retrieval | Set `RAG_EMBED_PROVIDER` to the same provider (+ `RAG_EMBED_DIM`) |
| Persistent production vector store | Install `requirements-ai.txt`, enable pgvector, set `RAG_VECTOR_BACKEND=pgvector` |

All configuration is via environment variables in `backend/.env` (see
`backend/.env.example`). No code changes.

---

## 1. Turn on generated answers (an LLM provider + key)

Pick **one** provider and provide its key. You (the human) must supply the key —
it can't be obtained automatically.

### Option A — Google Gemini (matches the design doc's AI roadmap)

```bash
cd backend
pip install -r requirements-ai.txt          # installs the Gemini + pgvector extras
```

In `backend/.env`:

```env
RAG_LLM_PROVIDER=gemini
RAG_EMBED_PROVIDER=gemini
RAG_EMBED_DIM=768                            # text-embedding-004 is 768-dim
GEMINI_API_KEY=your-key-here
# Optional overrides (defaults shown):
# GEMINI_LLM_MODEL=models/gemini-1.5-flash
# GEMINI_EMBED_MODEL=models/text-embedding-004
```

Get a key from Google AI Studio: https://aistudio.google.com/app/apikey

### Option B — OpenAI

```bash
cd backend
pip install -r requirements-ai.txt
```

In `backend/.env`:

```env
RAG_LLM_PROVIDER=openai
RAG_EMBED_PROVIDER=openai
RAG_EMBED_DIM=1536                           # text-embedding-3-small is 1536-dim
OPENAI_API_KEY=sk-...
# Optional overrides (defaults shown):
# OPENAI_LLM_MODEL=gpt-4o-mini
# OPENAI_EMBED_MODEL=text-embedding-3-small
```

Get a key from https://platform.openai.com/api-keys

> You can mix and match: e.g. keep `RAG_EMBED_PROVIDER=local` (no embedding
> cost) and set only `RAG_LLM_PROVIDER=gemini` for generated answers. If you do,
> leave `RAG_EMBED_DIM=256`.

Restart the backend after editing `.env`. Ask the AI Assistant on any ticket —
the "not configured" notice disappears and answers are now generated.

---

## 2. Switch to the pgvector production vector store

The default `memory` backend re-embeds all articles per query — fine for dev and
small knowledge bases. For production, use the persistent pgvector store so
embeddings are computed once (on save) and stored in Postgres.

1. **Install the extras** (if you haven't already): `pip install -r backend/requirements-ai.txt`
2. **Enable the pgvector extension** in your Postgres database (one-time):
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
   - Managed Postgres (Neon, Railway, RDS, Supabase…): pgvector is usually
     available; run the statement above once.
   - Self-hosted: install the OS package first, e.g. `postgresql-16-pgvector`.
3. **Configure `backend/.env`:**
   ```env
   RAG_VECTOR_BACKEND=pgvector
   # Defaults to DATABASE_URL; set only if the vector store uses a different DB:
   # RAG_PGVECTOR_URL=postgres://user:pass@host:5432/dbname
   RAG_EMBED_DIM=768        # MUST match your embedding provider (see table below)
   ```
4. **Re-index existing articles.** Embeddings are written when an article is
   created/updated through the API/UI. For articles that already existed before
   you switched on pgvector, re-save each one (edit → save) to embed it, or
   create them fresh.

LlamaIndex manages its own table (`rag_knowledge_embeddings`) — no Django
migration is involved, and `KnowledgeEntry` remains the source of truth.

### `RAG_EMBED_DIM` must match the embedding provider

| `RAG_EMBED_PROVIDER` | Model | `RAG_EMBED_DIM` |
|---|---|---|
| `local` (default) | built-in hashing embedding | `256` |
| `gemini` | `text-embedding-004` | `768` |
| `openai` | `text-embedding-3-small` | `1536` |

If this is wrong, pgvector will reject the vectors with a dimension-mismatch
error. If you change providers after data exists, drop the
`rag_knowledge_embeddings` table and re-index.

---

## 3. Populate the knowledge base

Staff users get a **Knowledge** link in the navbar → create/edit articles in the
UI (`/knowledge`). Non-staff users can read but not write. You can also manage
articles in Django admin (`/admin` → Knowledge entries). Each save chunks and
(re)embeds the article automatically.

---

## Reference: every RAG setting

| Env var | Default | Meaning |
|---|---|---|
| `RAG_EMBED_PROVIDER` | `local` | `local` \| `gemini` \| `openai` \| `mock` |
| `RAG_LLM_PROVIDER` | `none` | `none` \| `gemini` \| `openai` \| `mock` |
| `RAG_VECTOR_BACKEND` | `memory` | `memory` \| `pgvector` |
| `RAG_TOP_K` | `4` | how many chunks to retrieve |
| `RAG_CHUNK_SIZE` | `512` | chunk size (tokens) for splitting articles |
| `RAG_CHUNK_OVERLAP` | `40` | chunk overlap |
| `RAG_EMBED_DIM` | `256` | embedding width — must match the provider |
| `GEMINI_API_KEY` / `OPENAI_API_KEY` | empty | provider key (you supply) |
| `GEMINI_LLM_MODEL` / `OPENAI_LLM_MODEL` | see `.env.example` | answer model |
| `GEMINI_EMBED_MODEL` / `OPENAI_EMBED_MODEL` | see `.env.example` | embedding model |
| `RAG_PGVECTOR_URL` | `DATABASE_URL` | Postgres URL for the pgvector store |

`mock` providers are for tests only (deterministic, no network).

---

## How it fits together (for interviews / the README)

```
KnowledgeEntry (Postgres, source of truth)
      │  on save: chunk (SentenceSplitter) → embed → upsert
      ▼
LlamaIndex VectorStoreIndex  ──(memory | pgvector)──►  vector store
      ▲
      │  question → embed → top-k similarity retrieve
Ticket + question ──► grounded prompt ──► LLM (Gemini/OpenAI) ──► answer + sources
```

One-line résumé phrasing:

> Built a Django REST + LlamaIndex RAG service with vector retrieval
> (pgvector-backed), synchronous on-save ingestion, and a provider-agnostic
> LLM answer-generation layer.
