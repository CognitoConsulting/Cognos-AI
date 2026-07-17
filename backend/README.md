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
- sample Excel template download
- Excel template upload/import
- WhatsApp provider account setup
- provider-neutral WhatsApp webhook intake
- inbound WhatsApp message audit storage
- first assistant parser result storage
- assistant conversation state storage for confirmation or missing-information follow-up
- reporting record storage for progress, manpower, material transactions, stock balances, and media/proof files

During local development, these APIs require:

```text
X-Platform-Admin-Token: local-dev-platform-admin-token
```

This is a temporary foundation gate, not the final production authentication system.

## Knowledgebase template imports

The backend can now generate and import `.xlsx` templates for:

- units
- activities
- locations
- BOQ/material list
- schedule

This is the foundation for the dashboard upload workflow.

## WhatsApp provider adapter foundation

The backend now includes a provider-neutral webhook foundation.

Current supported intake formats:

- generic/test JSON payloads
- Meta WhatsApp Cloud API style text message payloads

This does not yet send WhatsApp replies or run the AI assistant workflow.

It normalizes inbound provider payloads and stores them in `whatsapp_messages`.

The webhook also creates a first parser result in `assistant_parse_results`.
It now creates a conversation state in `assistant_conversation_states` so the next step is visible:

- `awaiting_confirmation` when the message looks complete and should be confirmed before saving
- `awaiting_missing_information` when the assistant needs more details
- `redirected` when the message is irrelevant or offensive and should be handled professionally

Current parser behavior:

- detects progress updates
- detects manpower updates
- detects material received
- detects material issued
- detects irrelevant/offensive messages
- extracts basic quantity, unit, material, activity, trade counts, and location where possible
- marks missing information for follow-up

This is a rule-based foundation. External AI model calls will be added later.

The assistant does not yet save final progress, manpower, or material records.
The construction reporting tables now exist; the next step is to connect confirmed assistant conversations to these tables.

## Reporting record tables

The backend now has foundation tables and admin APIs for:

- `progress_entries`: confirmed work completed on site
- `manpower_entries`: workers by trade/category, date, and project area
- `material_transactions`: material received and material issued
- `material_stock_balances`: current material stock by project and material
- `media_files`: photos, voice notes, and proof files linked to a project or future record

These tables are intentionally separate from raw WhatsApp messages.
Raw messages preserve what the user sent.
Reporting records store the cleaned business data that dashboards, analytics, and exports will use.

Important user-identification rule:

- one WhatsApp phone number should map to one platform user
- this keeps inbound WhatsApp message routing unambiguous

