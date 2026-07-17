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

Create a unit:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/units \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"name\":\"Square Meter\",\"symbol\":\"sqm\",\"unit_type\":\"area\"}"
```

Create an activity:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/activities \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"name\":\"Plastering\",\"category\":\"Finishing\",\"default_unit_id\":\"<unit_id>\"}"
```

Create an activity synonym:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/activities/<activity_id>/synonyms \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"synonym\":\"plaster complete hua\",\"language\":\"hinglish\"}"
```

Create a project area:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/projects/<project_id>/locations \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"name\":\"Tower A\",\"location_type\":\"tower\"}"
```

Create a project sub-area:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/projects/<project_id>/locations \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"name\":\"Floor 2\",\"location_type\":\"floor\",\"parent_location_id\":\"<area_id>\"}"
```

Create a BOQ/material item:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/projects/<project_id>/boq-items \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"item_code\":\"PL-001\",\"item_description\":\"Internal plastering\",\"planned_quantity\":500,\"unit_id\":\"<unit_id>\",\"material_name\":\"Cement\",\"activity_id\":\"<activity_id>\"}"
```

Create a schedule item:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/projects/<project_id>/schedule-items \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"activity_id\":\"<activity_id>\",\"activity_name\":\"Plastering\",\"planned_start_date\":\"2026-07-20\",\"planned_end_date\":\"2026-07-25\",\"area_id\":\"<area_id>\",\"sub_area_id\":\"<sub_area_id>\",\"planned_quantity\":100,\"unit_id\":\"<unit_id>\"}"
```

Create a knowledge upload tracking record:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/projects/<project_id>/knowledge-uploads \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"upload_type\":\"boq\",\"file_name\":\"boq-template.xlsx\",\"uploaded_by\":\"<user_id>\",\"status\":\"imported\"}"
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
