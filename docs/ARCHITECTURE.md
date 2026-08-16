# Architecture

## Layered backend design

```
API (FastAPI routes)
  -> Service (business logic, e.g. AuthService, DocumentService, ChatService)
    -> Repository (data access, e.g. UserRepository, DocumentRepository)
      -> SQLAlchemy models / DB
```

Each layer only knows about the one directly below it. Services are
unit-tested against fake repositories (see `tests/unit/`), so business
logic can be verified without a database. Routes are tested against
FastAPI's `TestClient` with services/repositories overridden by fakes
(see `tests/api/`). Full-stack behavior against a real Postgres is
covered separately by `tests/integration/`.

## Document ingestion pipeline

```
Upload -> Parse (PDF/DOCX/TXT/MD) -> Chunk (recursive or semantic)
       -> Embed (HuggingFace or OpenAI) -> Index (FAISS + BM25, per document)
       -> Persist DocumentChunk rows (DB) <-> vector_id mapping
```

Each document gets its own FAISS index and BM25 index, persisted under
`storage/vector_store/{document_id}/`. This makes per-document deletion,
re-indexing, and ownership isolation trivial — there's no need to filter
a shared global index by owner at query time.

## Hybrid retrieval + chat pipeline

```
Query
  -> BM25 search (per selected document)      \
  -> Vector search (per selected document)      >  Reciprocal Rank Fusion
                                                /
  -> Fused candidates -> Cross-encoder re-rank -> Top-K context chunks
  -> Prompt builder (numbered excerpts + citation instructions)
  -> LLM (OpenAI or Ollama), streamed token-by-token
  -> Citation validator (rejects/flags fabricated [n] references)
  -> Persisted as a Message with citations + generation_metadata
```

Retrieval happens per-document because each document has its own index;
results are fused globally with Reciprocal Rank Fusion using
`(document_id, vector_id)` as the fusion key, so RRF works the same way
whether the user scoped the question to one document or their entire
library.

**Why reject hallucinated answers rather than just trust the model?**
The system prompt instructs the model to cite every claim as `[n]`, but
prompting alone doesn't guarantee compliance. `citation_validator.py`
parses the actual `[n]` markers out of the generated text and
cross-checks them against the chunks that were really sent as context —
a citation number that doesn't map to a real chunk is flagged as
`invalid_ref_ids`, and a substantial answer with zero citations is
flagged as `has_unverifiable_claims`. The client surfaces this as a
visible warning rather than silently trusting the output.

## Auth

Stateless JWT access tokens (short-lived) + refresh tokens (longer-lived).
The frontend's Axios client automatically retries a request once with a
refreshed access token on a 401, via `refreshAccessToken()` in
`frontend/src/lib/api-client.ts`.

## Cross-cutting middleware

- **Rate limiting** (`app/core/rate_limit.py`): Redis-backed fixed-window
  counter per client (Authorization header, or IP if unauthenticated).
  Auth endpoints get a stricter limit (20/min) than the rest of the API
  (120/min) since they're the highest-value target for abuse. Fails
  open — if Redis is unreachable, requests are allowed through rather
  than taking the API down.
- **Request logging** (`app/core/request_logging.py`): every request
  gets a UUID (`X-Request-ID` response header) and a structured log line
  with method, path, status, and duration — the basis for the "API
  request logs" requirement and for correlating a user-reported issue
  with server-side logs.

## Analytics

`AnalyticsService` aggregates directly from stored data — no separate
event-tracking pipeline. Every assistant `Message` stores
`generation_metadata` (retrieval/generation latency, token usage, cost
estimate, and whether its citations were fully verifiable) at write
time in `ChatService`, and analytics queries simply aggregate that
column. This keeps analytics consistent with what actually happened
during generation, at the cost of not supporting metrics that weren't
anticipated when the message was written.

## Evaluation

Two tiers:

1. **Fast, network-free approximations** (`app/evaluation/metrics.py`,
   `runner.py`) — lexical/structural proxies for RAGAS's faithfulness,
   context recall/precision, and answer relevancy, plus a latency
   score. Runs in CI on every PR with no external dependencies.
2. **LLM-graded evaluation** (`app/evaluation/ragas_runner.py`) — wires
   the same `EvalExample` dataset into the real `ragas`/`deepeval`
   libraries for a deeper, LLM-judged score. Not part of the default CI
   gate since it costs real API calls; intended as a scheduled/nightly
   job once an LLM judge is configured.

## Frontend

Next.js App Router, with a `(dashboard)` route group sharing a sidebar
layout gated by `useRequireAuth`. Server-Sent Events from the chat
endpoint are consumed via `fetch` + `ReadableStream` rather than the
browser's `EventSource`, because `EventSource` can't send custom
headers (needed for the JWT) or a POST body (needed for the question).
