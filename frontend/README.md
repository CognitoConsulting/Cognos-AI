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
- includes Excel workbook export with separate sheets for accessible reporting sections
- includes reporting health indicators for proof gaps, low stock, and attached images
- shows whether image/proof records are linked to project proof, progress, manpower, or material entries
- shows table helper text, row counts, clearer empty states, and role-aware restricted messages
- adapts navigation, report sections, analytics, and export buttons to the signed-in user's role
- lets owner/admin users create projects and review selected-project details
- lets owner/admin users add company users and assign users to the selected project
- lets owner/admin users download knowledgebase templates, upload completed `.xlsx` templates, and view upload history
- lets owner/admin users configure daily WhatsApp summaries, preview the message, send manually, and view send history
- lets owner/admin users review company-level inbound/outbound WhatsApp message logs
- lets owner/admin users add and review WhatsApp provider accounts for local/generic and Meta-style setups
- lets owner/admin users review assistant parse results, missing fields, and conversation states for pilot debugging
- lets owner/admin users configure whether the company uses platform-managed AI keys or company-owned AI mode

During local development, run the seed script and use the printed owner email with password `Demo12345!`.

The current login uses a signed bearer token. Backend APIs enforce role-aware access, and the frontend now hides or marks restricted sections based on the user's role/API permissions.

Current team management limitations:

- users can be created, but not edited or deactivated from the dashboard yet
- project assignments can be created, but not removed or edited from the dashboard yet

Current project management limitations:

- projects can be created, but not edited, archived, or deleted from the dashboard yet

Current knowledgebase management limitations:

- templates can be downloaded and imported, but imported knowledgebase records are not yet editable from the dashboard

Current AI configuration limitations:

- AI mode and AI insights subscription status can be configured
- real company-owned API key entry, validation, masking, and encrypted storage are not implemented yet

Current export behavior:

- the dashboard exports one `.xlsx` workbook for the selected company, project, and date range
- workbook sheets are included only for sections the signed-in user can access
- workbook generation currently happens in the browser

## Local development

From the repository root:

```bash
docker compose up --build
```

Dashboard:

```text
http://localhost:3000
```

