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

## Local admin API token

During early development, platform-admin setup APIs use a simple local token.

Header:

```text
X-Platform-Admin-Token: local-dev-platform-admin-token
```

This is not the final production login system.

It exists so we can safely build company/project/user setup before full authentication is implemented.

## Example API calls

Create a company:

```bash
curl -X POST http://localhost:8000/companies \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"name\":\"Demo Construction\"}"
```

Create a user:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/users \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"name\":\"Site Engineer\",\"phone\":\"+919999999999\",\"email\":\"site@example.com\",\"role\":\"site_engineer\"}"
```

Create a project:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/projects \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"name\":\"Green Residency\",\"code\":\"GR-001\",\"location\":\"Pune\"}"
```

Assign a user to a project:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/projects/<project_id>/users \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"user_id\":\"<user_id>\",\"role_on_project\":\"site_engineer\",\"can_enter_progress\":true,\"can_enter_manpower\":true,\"can_view_dashboard\":true}"
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
