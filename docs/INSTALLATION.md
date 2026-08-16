# Installation Guide

## Prerequisites

- Docker & Docker Compose (recommended path)
- Or, for manual setup: Python 3.12+, Node.js 20+, PostgreSQL 16, Redis 7

## Option A: Docker Compose (recommended)

```bash
git clone <this-repo>
cd askmydocs-ai
cp .env.example .env
# Edit .env: set JWT_SECRET_KEY, POSTGRES_PASSWORD, and either
# OPENAI_API_KEY (if LLM_PROVIDER=openai) or leave LLM_PROVIDER=ollama
# and run Ollama separately / add it as a compose service.

docker compose up --build
```

Then:

```bash
docker compose exec backend alembic upgrade head
```

- Frontend: http://localhost:3000
- Backend API + docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Option B: Manual local setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp ../.env.example ../.env       # or export the vars another way
# Make sure Postgres and Redis are running locally and DATABASE_URL /
# REDIS_URL in .env point at them.

alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local` if the backend
isn't at `http://localhost:8000/api/v1`.

## Running tests

```bash
cd backend
pytest -m "unit or api"      # fast, no external services required
pytest -m integration        # needs a live Postgres (docker compose up db)
pytest -m evaluation         # RAG quality regression suite

cd ../frontend
npm test
```

## Local LLM (Ollama)

If `LLM_PROVIDER=ollama` (the default), you need an Ollama server
reachable at `OLLAMA_BASE_URL`. Locally:

```bash
ollama serve
ollama pull llama3.1
```

In Docker Compose, add an `ollama` service and point `OLLAMA_BASE_URL`
at `http://ollama:11434`.

## Troubleshooting

See [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md).
