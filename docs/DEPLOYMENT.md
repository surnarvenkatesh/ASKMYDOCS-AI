# Deployment Guide

This app is a standard two-container (frontend + backend) app with a
managed Postgres and Redis, so it maps cleanly onto most platforms.
Platform-specific config lives under `deployment/<platform>/`.

## General checklist (any platform)

1. Provision managed Postgres 16 and Redis 7.
2. Set every variable in `docs/ENVIRONMENT_VARIABLES.md` on the backend
   service — especially `JWT_SECRET_KEY` (long random value, never the
   dev default), `DATABASE_URL`, `REDIS_URL`, and either `OPENAI_API_KEY`
   or a reachable `OLLAMA_BASE_URL`.
3. Run `alembic upgrade head` as a release/pre-deploy step, not inside
   the app's normal startup path.
4. Set `NEXT_PUBLIC_API_BASE_URL` on the frontend build to the
   backend's public URL + `/api/v1`.
5. Mount persistent storage for `UPLOAD_DIR` and `VECTOR_STORE_PATH` —
   these are plain files (FAISS indexes, BM25 pickles, raw uploads) and
   are **not** stored in Postgres. On platforms without persistent
   volumes, point these at an attached disk or object-storage-backed
   filesystem; otherwise re-indexing is required after every deploy.
6. Point your load balancer / reverse proxy at the backend with
   response buffering **disabled** for `/api/v1/chat/*` (see
   `docs/TROUBLESHOOTING.md` — streaming SSE responses break if buffered).

## Render — `deployment/render/`

`render.yaml` defines a Blueprint: a web service for the backend, a web
service for the frontend, a managed Postgres instance, and a Redis
instance. Deploy with:

```bash
render blueprint launch
```

## Railway — `deployment/railway/`

`railway.json` + per-service `Dockerfile` references. Railway auto-
provisions Postgres/Redis plugins; wire their generated connection
strings into `DATABASE_URL`/`REDIS_URL` via Railway's variable
references (`${{Postgres.DATABASE_URL}}`, etc.).

## AWS — `deployment/aws/`

`ecs-task-definition.json` for running both containers on ECS Fargate,
behind an ALB. Use RDS (Postgres) and ElastiCache (Redis). Persistent
storage for uploads/vector store: an EFS volume mounted into the
backend task.

## Azure — `deployment/azure/`

`container-app.bicep` provisioning Azure Container Apps for both
services, Azure Database for PostgreSQL, and Azure Cache for Redis.

## DigitalOcean — `deployment/digitalocean/`

`app.yaml` App Platform spec — two services (frontend, backend) plus
a managed Postgres and Redis database, wired the same way as the other
platforms.

## Zero-downtime migrations

Alembic migrations in this repo are additive-first (new tables/columns
before any destructive change), so they're safe to run before the new
backend version starts serving traffic. Run `alembic upgrade head` as a
pre-deploy/release-phase step on every platform above.
