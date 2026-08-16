# Troubleshooting

### `docker compose up` fails building the backend image
Usually a missing system library for `unstructured`/`pypdf`/`sentence-transformers`.
The Dockerfile already installs `poppler-utils`, `libgl1`, and `libpq-dev` —
if you see a new missing-`.so` error, add the corresponding `apt-get`
package to `backend/Dockerfile`'s system-deps layer.

### `alembic upgrade head` fails with "relation already exists"
Someone ran `Base.metadata.create_all` directly instead of going through
Alembic (the integration tests do this in an isolated test DB — don't
point `DATABASE_URL` at your dev DB while running `pytest -m integration`).
Fix: drop and recreate the dev database, then run migrations from scratch.

### 401 Unauthorized immediately after logging in
Check `JWT_SECRET_KEY` is set (and identical) wherever the backend runs —
if you're running multiple backend instances/replicas with different
auto-generated secrets, tokens issued by one won't validate on another.

### Chat endpoint returns "You don't have any indexed documents yet"
Upload finished with `status: "failed"` — check `error_message` on the
document (`GET /api/v1/documents/{id}`) or the backend logs. Common
causes: corrupt/password-protected PDF, or an embedding model that
failed to download (check network access to Hugging Face on first run).

### Streaming chat responses stop mid-answer with no error
This is almost always a reverse-proxy buffering the SSE stream. Make
sure your proxy (nginx, an ALB, etc.) has response buffering disabled
for `/api/v1/chat/*` and forwards `text/event-stream` without altering
`Transfer-Encoding`.

### Frontend can't reach the backend (`ERR_CONNECTION_REFUSED` / CORS errors)
- Confirm `NEXT_PUBLIC_API_BASE_URL` matches where the backend is
  actually listening.
- Confirm `CORS_ORIGINS` in the backend's `.env` includes the exact
  frontend origin (scheme + host + port).

### FAISS index seems stale after re-uploading a document
Use the **Re-index** action (`POST /documents/{id}/reindex`) rather than
deleting and re-uploading under the same filename — re-index correctly
clears the old FAISS/BM25 index for that document before rebuilding it.

### `pytest -m integration` can't connect to Postgres
These tests need a real database. Start one with
`docker compose up db` (or point `DATABASE_URL` at any reachable
Postgres 16 instance) before running them; they're intentionally
excluded from the default `pytest -m "unit or api"` run.
