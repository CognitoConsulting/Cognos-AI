# Local Development

## Prerequisites

- Git
- Docker Desktop
- Node.js if running the frontend outside Docker
- Python 3.12 if running the backend outside Docker

## First-time setup

Copy the example environment file:

```bash
cp .env.example .env
```

Start the local stack:

```bash
docker compose up --build
```

## Local URLs

Backend:

```text
http://localhost:8000
```

Backend health check:

```text
http://localhost:8000/health
```

Backend API docs:

```text
http://localhost:8000/docs
```

Frontend dashboard:

```text
http://localhost:3000
```

PostgreSQL:

```text
localhost:5433
```

## Database migrations

Migrations run automatically when the backend container starts.

To run migrations manually inside the backend container:

```bash
docker compose exec backend alembic upgrade head
```

## Important safety rule

Never commit real credentials.

Use `.env` locally and keep `.env.example` as the safe template.
