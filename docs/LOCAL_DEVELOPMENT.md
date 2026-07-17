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

The dashboard now starts with a local login screen.

After seeding demo data, use the demo owner email printed by the seed script with this password:

```text
Demo12345!
```

After login, the dashboard stores a signed bearer token in the browser and can load:

- companies
- projects
- progress entries
- manpower entries
- material transactions
- material stock balances
- media/proof files

It includes company/project selection, date range filters, summary cards, project-manager analytics cards, reporting health indicators, reporting tables, and Excel workbook export.

This is still a development dashboard. The backend enforces role-aware API access, and the frontend now adapts the visible navigation, analytics, reporting tables, export buttons, empty states, and restricted messages to the signed-in user's role.

Owner/admin users can also use the first team-management panel to:

- create projects
- view selected-project setup details
- download project knowledgebase templates
- upload completed project knowledgebase templates
- view selected-project knowledgebase upload history
- view company users
- create company users
- view selected-project assignments
- assign users to the selected project with progress, manpower, material, and dashboard permissions
- export the selected reporting view as one `.xlsx` workbook with separate accessible sheets

Editing imported knowledgebase records, editing projects, archiving projects, editing users, deactivating users, and removing project assignments are not implemented yet.

## Seed demo data

After the backend is running, create a realistic demo dataset:

```bash
python scripts/seed_demo_data.py
```

The seed script creates:

- one demo company
- one active project
- owner, project manager, site engineer, and storekeeper users
- project assignments with realistic permissions
- progress entries
- manpower entries
- material received/issued transactions
- material stock balances, including low/negative stock examples
- proof/media file records
- demo passwords for seeded users

The script talks to the backend API at:

```text
http://localhost:8000
```

Override the API URL if needed:

```bash
python scripts/seed_demo_data.py --api-base http://localhost:8000
```

Then open:

```text
http://localhost:3000
```

Use the printed owner email and password `Demo12345!` to sign in.

PostgreSQL:

```text
localhost:5433
```

## Local admin API token

During early development, platform-admin setup APIs still support a simple local token.

Header:

```text
X-Platform-Admin-Token: local-dev-platform-admin-token
```

This is not the final production login system.

It exists so platform admins can safely create companies and initial owner/admin users during pilot setup.

The dashboard login uses:

```text
Authorization: Bearer <signed-login-token>
```

Current backend API permission rules:

- platform admin token can create companies and perform pilot setup
- owner/admin users can manage their company, users, projects, project assignments, and knowledgebase data
- project managers, site engineers, and supervisors can access only assigned projects
- progress APIs require progress permission on the project
- manpower APIs require manpower permission on the project
- material APIs require material permission on the project
- storekeepers can access material records for assigned projects, but not progress or manpower records
- users cannot access another company's data

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

Download a sample template:

```bash
curl -L http://localhost:8000/companies/<company_id>/knowledgebase/templates/boq \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -o boq_template.xlsx
```

Supported template types:

- `units`
- `activities`
- `locations`
- `boq`
- `schedule`

Upload and import a completed template:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/projects/<project_id>/knowledge-uploads/import \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -F "upload_type=boq" \
  -F "uploaded_by=<user_id>" \
  -F "file=@boq_template.xlsx"
```

Import behavior:

- validates required columns
- imports valid rows
- skips duplicate known records where possible
- records failed uploads with readable errors
- stores upload history in `project_knowledge_uploads`

## WhatsApp provider adapter examples

Create a WhatsApp provider account:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/whatsapp/provider-accounts \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"provider_name\":\"generic\",\"provider_account_id\":\"local-test-account\",\"phone_number_id\":\"local-test-number\"}"
```

Send a generic test webhook:

```bash
curl -X POST http://localhost:8000/webhooks/whatsapp/generic \
  -H "Content-Type: application/json" \
  -d @docs/examples/whatsapp-generic-message.json
```

If you run the same webhook test repeatedly, change the `message_id` in the sample file.

The system treats repeated provider message IDs as duplicates, which is intentional.

Send a Meta-style test webhook:

```bash
curl -X POST http://localhost:8000/webhooks/whatsapp/meta_cloud_api \
  -H "Content-Type: application/json" \
  -d @docs/examples/whatsapp-meta-text-message.json
```

List stored WhatsApp messages:

```bash
curl http://localhost:8000/companies/<company_id>/whatsapp/messages \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token"
```

Send a manual outbound test reply:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/whatsapp/outbound-messages \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d @docs/examples/whatsapp-outbound-message.json
```

Current behavior:

- normalizes provider payloads
- identifies active users by phone number if already created
- requires WhatsApp phone numbers to be unique across the platform
- stores inbound messages for audit
- marks messages from unknown numbers as `unknown_user`
- creates a first assistant parser result
- creates an assistant conversation state for confirmation, missing information, or professional redirect
- logs outbound assistant replies in `whatsapp_messages`
- simulates outbound delivery for `generic` and `test` providers
- queues outbound messages for real providers until Meta/provider credentials are configured

Send a manpower test webhook:

```bash
curl -X POST http://localhost:8000/webhooks/whatsapp/generic \
  -H "Content-Type: application/json" \
  -d @docs/examples/whatsapp-manpower.json
```

Send a material received test webhook:

```bash
curl -X POST http://localhost:8000/webhooks/whatsapp/generic \
  -H "Content-Type: application/json" \
  -d @docs/examples/whatsapp-material-received.json
```

List assistant parse results:

```bash
curl http://localhost:8000/companies/<company_id>/assistant/parse-results \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token"
```

List assistant conversation states:

```bash
curl http://localhost:8000/companies/<company_id>/assistant/conversation-states \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token"
```

Conversation states show what the assistant would do next:

- `awaiting_confirmation`: the entry looks complete and should be confirmed before saving
- `awaiting_missing_information`: the assistant needs missing details
- `redirected`: the message was irrelevant/offensive and should be handled professionally

## Reporting record API examples

Create a progress entry:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/projects/<project_id>/reporting/progress-entries \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"activity_name\":\"Plastering\",\"quantity\":50,\"unit_symbol\":\"sqm\",\"location_text\":\"Tower A Floor 2\",\"work_date\":\"2026-07-17\",\"status\":\"confirmed\"}"
```

Create a manpower entry:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/projects/<project_id>/reporting/manpower-entries \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"trade_name\":\"mason\",\"worker_count\":10,\"location_text\":\"Tower A\",\"work_date\":\"2026-07-17\",\"status\":\"confirmed\"}"
```

Create a material transaction:

```bash
curl -X POST http://localhost:8000/companies/<company_id>/projects/<project_id>/reporting/material-transactions \
  -H "Content-Type: application/json" \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token" \
  -d "{\"transaction_type\":\"received\",\"material_name\":\"cement\",\"quantity\":100,\"unit_symbol\":\"bags\",\"transaction_date\":\"2026-07-17\",\"proof_status\":\"not_attached\"}"
```

List records:

```bash
curl http://localhost:8000/companies/<company_id>/projects/<project_id>/reporting/progress-entries \
  -H "X-Platform-Admin-Token: local-dev-platform-admin-token"
```

The reporting APIs are still foundation APIs.
They are now connected to the first assistant confirmation-save workflow.
Dashboard charts are not connected yet.

## Assistant confirmation-save example

For a WhatsApp user assigned to exactly one active project:

1. Send a normal update:

```bash
curl -X POST http://localhost:8000/webhooks/whatsapp/generic \
  -H "Content-Type: application/json" \
  -d "{\"message_id\":\"progress-test-001\",\"phone\":\"+919999999999\",\"message_text\":\"Aaj Tower A Floor 2 me 50 sqm plaster complete hua\",\"provider_account_id\":\"local-test-account\"}"
```

2. Send a confirmation reply:

```bash
curl -X POST http://localhost:8000/webhooks/whatsapp/generic \
  -H "Content-Type: application/json" \
  -d "{\"message_id\":\"progress-confirm-001\",\"phone\":\"+919999999999\",\"message_text\":\"Yes\",\"provider_account_id\":\"local-test-account\"}"
```

The second message should save the pending update into the correct reporting table.
It also logs an outbound assistant reply such as "Saved. I have recorded this update."

Supported simple confirmation replies include:

- `Yes`
- `OK`
- `haan`
- `sahi hai`

If the user belongs to multiple possible projects, the system will not guess.
It marks the conversation as needing project selection.
The next message from the same user can be the project name or project code, for example:

```bash
curl -X POST http://localhost:8000/webhooks/whatsapp/generic \
  -H "Content-Type: application/json" \
  -d "{\"message_id\":\"project-select-001\",\"phone\":\"+919999999999\",\"message_text\":\"GR-001\",\"provider_account_id\":\"local-test-account\"}"
```

If the project matches one active project available to that user, the pending update is saved.
If it matches none or more than one, the system keeps waiting for a clearer project selection.

The save step also checks project permissions:

- progress requires `can_enter_progress`
- manpower requires `can_enter_manpower`
- material received/issued requires `can_enter_materials`

## Database migrations

Migrations run automatically when the backend container starts.

To run migrations manually inside the backend container:

```bash
docker compose exec backend alembic upgrade head
```

## Important safety rule

Never commit real credentials.

Use `.env` locally and keep `.env.example` as the safe template.
