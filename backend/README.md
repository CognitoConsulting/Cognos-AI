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

## Early setup APIs

The first foundation APIs allow platform-admin setup of:

- companies
- company users
- projects
- project-user assignments
- project knowledgebase units
- project knowledgebase activities
- project areas and sub-areas
- BOQ/material items
- project schedule items
- project knowledge upload tracking

During local development, these APIs require:

```text
X-Platform-Admin-Token: local-dev-platform-admin-token
```

This is a temporary foundation gate, not the final production authentication system.

