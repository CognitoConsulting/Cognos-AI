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
- Excel export
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
- reporting record tables for progress, manpower, materials, stock balances, and media/proof files
- first assistant confirmed-save workflow for WhatsApp replies like “Yes”, “OK”, or “haan”

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
