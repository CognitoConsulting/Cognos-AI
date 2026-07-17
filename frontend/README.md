# Frontend

React dashboard for Cognos AI.

## Purpose

The frontend will provide:

- login and role-based dashboard access
- company and project views
- team management
- project knowledgebase uploads
- progress, manpower, materials, and image/proof views
- project manager analytics
- Excel exports
- WhatsApp and AI configuration screens

Current live dashboard foundation:

- loads companies and projects from the backend
- shows saved progress, manpower, material, stock, and media/proof records
- supports date range filtering
- includes summary cards
- includes CSV export buttons that Excel can open

During local development, the frontend uses the temporary platform-admin token.
This should be replaced by real login before production use.

## Local development

From the repository root:

```bash
docker compose up --build
```

Dashboard:

```text
http://localhost:3000
```

