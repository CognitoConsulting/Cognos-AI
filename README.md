# Cognos AI

AI-assisted construction site reporting SaaS.

## Product summary

Cognos AI helps small contractors and builder-developers capture daily construction site data through WhatsApp and review it through a dashboard.

The MVP focuses on:

- progress reporting
- manpower reporting
- material received and issued tracking
- image/proof capture
- voice and text input
- project knowledgebase-based validation
- dashboard analytics
- Excel workbook export
- automatic daily WhatsApp summaries

## Repository status

This is the clean MVP repository.

The previous intern-built prototype should be treated as an audit/reference source only. Old prototype code should not be copied into this repository without review.

## Documentation

The MVP planning pack is available in:

```text
docs/mvp-planning
```

Start with:

- `01 MVP Product Brief.md`
- `02 MVP Scope.md`
- `11 Implementation Backlog.md`
- `12 GitHub Branching and Repo Setup.md`

Local development setup:

- `docs/LOCAL_DEVELOPMENT.md`

Current foundation includes:

- backend health check
- PostgreSQL migration setup
- company setup APIs
- user setup APIs
- project setup APIs
- project-user assignment APIs
- project knowledgebase APIs for units, activities, locations, BOQ items, schedule items, and upload tracking
- project knowledgebase Excel template download and import foundation
- provider-neutral WhatsApp webhook intake and message audit storage
- first rule-based assistant parser foundation
- assistant confirmation/missing-information conversation state foundation
- provider-neutral outbound WhatsApp reply logging with generic/test simulated delivery
- daily WhatsApp summary foundation with configurable 7 PM local default, preview, manual send, and send audit records
- automatic in-app daily summary scheduler that checks local project time and sends each project summary once per day
- reporting record tables for progress, manpower, materials, stock balances, and media/proof files
- first assistant confirmed-save workflow for WhatsApp replies like “Yes”, “OK”, or “haan”
- project-selection follow-up when a WhatsApp user belongs to multiple active projects
- first live dashboard reporting views for saved progress, manpower, materials, stock, and media records
- first project-manager analytics cards for progress by area, manpower distribution, stock highlights, and attention items
- demo data seed script for quickly populating a realistic company/project dashboard
- password-based login foundation with signed bearer tokens for the dashboard
- role-aware API access for company, project, reporting, knowledgebase, and WhatsApp admin routes
- role-aware dashboard navigation, reporting sections, and exports
- first dashboard team-management UI for adding users and assigning them to projects
- first dashboard project-management UI for creating projects and reviewing project setup
- first dashboard project knowledgebase UI for template downloads, template imports, and upload history
- dependency-free Excel workbook export with separate sheets for reporting data
- polished reporting workspace with health indicators, row counts, clearer empty states, and role-aware restricted messages

## Planned architecture

- Backend: Python/FastAPI
- Database: PostgreSQL
- Dashboard: modern web frontend
- WhatsApp: provider-flexible adapter, ready for Meta WhatsApp Cloud API or another provider
- AI: platform-managed keys or company-owned keys
- Media: object storage

## Local development

Copy the environment template:

```bash
cp .env.example .env
```

Start the stack:

```bash
docker compose up --build
```

Then open:

```text
http://localhost:3000
```

Seed demo data:

```bash
python scripts/seed_demo_data.py
```

This creates a demo company, project, users, reporting records, stock balances, and proof images through the backend API.

The seed script also prints a demo owner email and password that can be used on the dashboard login screen.

## Branching

Default branch:

```text
main
```

Feature work should happen on branches such as:

```text
feature/backend-foundation
feature/frontend-foundation
feature/project-knowledgebase
feature/whatsapp-provider-adapter
feature/ai-assistant-parser
feature/assistant-confirmation-workflow
```
