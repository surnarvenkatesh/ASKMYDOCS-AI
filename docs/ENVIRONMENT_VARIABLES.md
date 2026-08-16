# Environment Variables

All variables live in `.env` at the project root (see `.env.example`).
Docker Compose and the backend's `Settings` class (Pydantic) both read
from this same file.

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | `development`, `staging`, or `production` |
| `APP_DEBUG` | `true` | Enables SQL echo and verbose errors |
| `BACKEND_PORT` | `8000` | FastAPI port |
| `FRONTEND_URL` / `CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origin(s), comma-separated |
| `DATABASE_URL` | — | `postgresql+asyncpg://user:pass@host:5432/db` |
| `REDIS_URL` | — | `redis://host:6379/0` |
| `JWT_SECRET_KEY` | — | **Change in production.** Long random string. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |
| `LLM_PROVIDER` | `ollama` | `openai` or `ollama` |
| `OPENAI_API_KEY` | — | Required if `LLM_PROVIDER=openai` |
| `OPENAI_MODEL` | `gpt-4o-mini` | Chat model |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Local/self-hosted Ollama server |
| `OLLAMA_MODEL` | `llama3.1` | Local model name |
| `EMBEDDING_PROVIDER` | `huggingface` | `huggingface` or `openai` |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Sentence-transformers model |
| `CROSS_ENCODER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Re-ranking model |
| `VECTOR_STORE_PATH` | `./storage/vector_store` | FAISS/BM25 index storage root |
| `UPLOAD_DIR` | `./storage/uploads` | Raw file storage root |
| `MAX_UPLOAD_SIZE_MB` | `25` | Upload size limit |
| `ALLOWED_FILE_TYPES` | `.pdf,.docx,.txt,.md` | Accepted extensions |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `800` / `120` | Recursive chunker sizing (approx. tokens) |
| `BM25_TOP_K` / `VECTOR_TOP_K` | `20` / `20` | Candidates pulled per method before fusion |
| `RRF_K` | `60` | Reciprocal Rank Fusion constant |
| `RERANK_TOP_K` | `5` | Chunks kept after cross-encoder re-ranking |
| `MIN_CONFIDENCE_SCORE` | `0.35` | Informational confidence floor shown in the UI |
| `RAGAS_ENABLED` / `DEEPEVAL_ENABLED` | `true` | Gate the optional LLM-graded evaluation runner |
| `LOG_LEVEL` / `LOG_FORMAT` | `INFO` / `json` | structlog configuration |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000/api/v1` | Frontend -> backend base URL |

**Never commit `.env`.** It's covered by `.gitignore`; only
`.env.example` (with placeholder values) is committed.
