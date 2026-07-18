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
- company AI setting updates for platform-managed or company-owned AI mode
- provider-neutral WhatsApp webhook intake
- inbound WhatsApp message audit storage
- first assistant parser result storage
- assistant conversation state storage for confirmation or missing-information follow-up
- reporting record storage for progress, manpower, material transactions, stock balances, and media/proof files
- first confirmed-save workflow from WhatsApp confirmation replies into reporting records
- first correction workflow before confirmation-save
- first missing-information follow-up workflow before confirmation-save
- project-selection follow-up for users assigned to multiple active projects

During local development, these APIs require:

```text
X-Platform-Admin-Token: local-dev-platform-admin-token
```

This is a temporary foundation gate, not the final production authentication system.

## AI configuration foundation

The backend stores a company-level AI mode:

- `platform_managed`: Cognos AI manages the model credentials behind the scenes
- `company_owned`: the customer intends to use its own AI credentials

Owner/admin users can update the mode and AI insights subscription flag through:

```text
PUT /companies/{company_id}/ai-settings
```

This endpoint does not accept or store real API keys yet. Secure key entry should be added only with encrypted storage, masking, validation, and audit logging.

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

The assistant can now save final progress, manpower, and material records after a simple confirmation reply such as `Yes`, `OK`, or `haan`.

If the first message is incomplete, the assistant can now use the next short reply to complete the pending draft. For example, if the user says `cement received`, the assistant can ask for missing quantity/unit, and the user can reply `50 bags`.

Before saving, the user can correct the pending confirmation with replies such as:

- `change quantity to 60`
- `unit is bags`
- `location Tower B Floor 3`
- `material cement`

The assistant updates the pending entry and asks for confirmation again.

Current save behavior:

- if the user has exactly one active assigned project, the confirmed update is saved to that project
- if the user has multiple possible projects, the system does not guess and asks for project name or project code
- the user's next project name/code reply is matched against their active projects and then saved
- project-user permissions are checked before saving
- progress updates create one `progress_entries` record
- manpower updates create one `manpower_entries` record per trade/category
- material received/issued creates one `material_transactions` record
- material received/issued also updates `material_stock_balances`

More complex corrections such as changing the full intent, splitting one message into multiple entries, or editing already-saved records are not implemented yet.
Outbound WhatsApp replies are now logged through the provider-neutral outbound foundation.
Generic/test providers simulate delivery locally; real providers remain queued until provider credentials are configured.

## Daily summary scheduler

The backend now starts a lightweight in-app scheduler when `DAILY_SUMMARY_SCHEDULER_ENABLED=true`.

Current behavior:

- checks enabled daily summary settings at a configurable interval
- creates default 7:00 PM local daily summary settings for active projects that do not have settings yet
- sends each active project summary once per local project date after the configured local send time
- sends to active project users who have dashboard access and WhatsApp phone numbers
- records one `daily_summary_messages` row per recipient
- logs the underlying outbound WhatsApp message through `whatsapp_messages`

This is the MVP scheduler foundation.
For larger production deployments, this can later move from the FastAPI process into a separate worker.

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

