# AskMyDocs AI

Enterprise-grade Retrieval-Augmented Generation (RAG) platform. Upload documents (PDF, DOCX, TXT, Markdown), ask questions in natural language, and get cited, hallucination-checked answers backed by a hybrid BM25 + vector retrieval pipeline.

> **Status:** Under active build. See `docs/PROGRESS.md` for what's implemented so far.

## Stack

| Layer      | Tech |
|------------|------|
| Frontend   | Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion, React Query |
| Backend    | FastAPI, Python 3.12+, SQLAlchemy, Alembic, Pydantic v2 |
| Data       | PostgreSQL, Redis |
| Retrieval  | LangChain, LlamaIndex, FAISS, BM25, Sentence Transformers, Cross-Encoder re-ranking, Reciprocal Rank Fusion |
| LLM        | OpenAI API (optional) or local Ollama |
| Evaluation | RAGAS, DeepEval |

## Project Structure

```
askmydocs-ai/
├── backend/            # FastAPI application
│   ├── app/
│   │   ├── api/v1/         # Route handlers
│   │   ├── core/           # Config, security, logging
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response models
│   │   ├── services/       # Business logic
│   │   ├── repositories/   # Data access layer
│   │   ├── ingestion/      # Document parsing & chunking
│   │   ├── retrieval/      # Hybrid search, RRF, re-ranking
│   │   ├── evaluation/     # RAGAS / DeepEval pipelines
│   │   └── utils/
│   ├── alembic/             # DB migrations
│   └── tests/                # unit / integration / api / evaluation
├── frontend/            # Next.js application
│   └── src/
│       ├── app/            # App Router pages
│       ├── components/     # UI components
│       ├── lib/            # API client, utils
│       ├── hooks/          # Custom React hooks
│       ├── types/          # Shared TypeScript types
│       └── styles/
├── deployment/          # Platform-specific deployment configs
├── docs/                 # Architecture, API, deployment docs
├── .github/workflows/    # CI/CD pipelines
└── docker-compose.yml
```

## Getting Started

```bash
cp .env.example .env         # fill in secrets
docker compose up --build    # starts db, redis, backend, frontend
```

- Backend API: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:3000

See `docs/INSTALLATION.md` for local (non-Docker) setup and `docs/ARCHITECTURE.md` for how the retrieval pipeline works.

## Build Plan

This project is being built incrementally, feature by feature:

1. ✅ Project scaffold & Docker Compose
2. ✅ Backend core: config, auth (JWT), protected routes
3. ✅ Document ingestion: upload, chunking, embeddings, FAISS/BM25 indexing
4. ⬜ Hybrid retrieval + RAG chat endpoint (streaming, citations)
4. ✅ Hybrid retrieval + RAG chat endpoint (streaming, citations)
5. ✅ Frontend: landing page → dashboard → chat UI
6. ✅ Analytics, evaluation pipeline, tests, CI/CD, docs

See `docs/API.md`, `docs/ARCHITECTURE.md`, `docs/INSTALLATION.md`, `docs/ENVIRONMENT_VARIABLES.md`, `docs/DEPLOYMENT.md`, and `docs/TROUBLESHOOTING.md` for details on each.

#venkatesh