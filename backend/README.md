# Backend

FastAPI backend for Cognos AI.

## Purpose

The backend will handle:

- company, project, and user management
- WhatsApp webhook intake
- AI assistant parsing
- project knowledgebase validation
- progress, manpower, material, and media records
- dashboard APIs
- Excel export
- daily WhatsApp summaries

## Local development

From the repository root:

```bash
docker compose up --build
```

Backend health check:

```text
http://localhost:8000/health
```

API docs:

```text
http://localhost:8000/docs
```

