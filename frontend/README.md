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

- requires login using a seeded demo user
- loads companies and projects from the backend
- shows saved progress, manpower, material, stock, and media/proof records
- supports date range filtering
- includes summary cards
- includes project-manager analytics cards for progress by area, manpower distribution, stock highlights, and attention items
- includes CSV export buttons that Excel can open
- adapts navigation, report sections, analytics, and export buttons to the signed-in user's role
- lets owner/admin users add company users and assign users to the selected project

During local development, run the seed script and use the printed owner email with password `Demo12345!`.

The current login uses a signed bearer token. Backend APIs enforce role-aware access, and the frontend now hides or marks restricted sections based on the user's role/API permissions.

Current team management limitations:

- users can be created, but not edited or deactivated from the dashboard yet
- project assignments can be created, but not removed or edited from the dashboard yet

## Local development

From the repository root:

```bash
docker compose up --build
```

Dashboard:

```text
http://localhost:3000
```

