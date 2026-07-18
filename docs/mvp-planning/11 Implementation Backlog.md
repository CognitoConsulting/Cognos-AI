# 11 Implementation Backlog

## Purpose

This document converts the MVP product decisions into buildable work.

It is written so a founder, product manager, designer, or developer can understand what needs to be built and why.

## Priority meaning

- P0: required for first pilot
- P1: important soon after pilot
- P2: later enhancement

## Epic 1: Product and engineering foundation

### 1.1 Create clean MVP repository

Priority: P0

Business reason:

The old intern-built codebase is useful for learning, but the MVP should start from a clean technical foundation.

Acceptance criteria:

- private GitHub repository exists
- repository name is `Cognos-AI`
- default branch is `main`
- old prototype is not copied blindly into the new repo
- MVP documentation pack is included
- README explains what the product is

Dependencies:

- GitHub repository access

### 1.2 Create backend project foundation

Priority: P0

Business reason:

The product needs a reliable backend for WhatsApp messages, dashboard APIs, AI parsing, database storage, and exports.

Acceptance criteria:

- Python/FastAPI backend is created
- environment configuration is supported
- health check endpoint exists
- basic error handling exists
- local development setup is documented

Dependencies:

- clean repo

### 1.3 Create frontend dashboard foundation

Priority: P0

Business reason:

The dashboard is required for viewing project data, analytics, team management, exports, and project knowledgebase uploads.

Acceptance criteria:

- dashboard app is created
- login screen placeholder exists
- app layout exists
- navigation exists for dashboard, projects, team, knowledgebase, reports, and settings
- frontend can call backend health endpoint

Dependencies:

- clean repo
- backend foundation

## Epic 2: Database and data model

### 2.1 Set up PostgreSQL

Priority: P0

Business reason:

CSV storage is not suitable for a SaaS product.

Acceptance criteria:

- PostgreSQL is configured for local development
- database connection works
- migrations are supported
- seed data approach is documented

Dependencies:

- backend foundation

### 2.2 Create core SaaS tables

Priority: P0

Business reason:

The platform must support multiple companies, multiple projects, and multiple users per project from day one.

Acceptance criteria:

- companies table exists
- users table exists
- projects table exists
- project_users table exists
- roles and project assignments are stored
- company-level data separation is enforced in queries

Dependencies:

- PostgreSQL setup

### 2.3 Create construction reporting tables

Priority: P0

Business reason:

The MVP depends on structured progress, manpower, material, and image records.

Acceptance criteria:

- progress_entries table exists
- manpower_entries table exists
- material_transactions table exists
- material_stock_balances table exists
- media_files table exists
- records include company, project, user, date, original message, and status
- foundation APIs exist to create and list these records during development

Dependencies:

- core SaaS tables

### 2.4 Create project knowledgebase tables

Priority: P0

Business reason:

The assistant must validate user entries against real project data.

Acceptance criteria:

- project_knowledge_uploads table exists
- project_locations table supports areas and sub-areas
- activities table exists
- units table exists
- BOQ/material list table exists
- schedule activity table exists
- optional scope of work and resource plan tables are supported
- foundation APIs exist for manually creating units, activities, locations, BOQ items, schedule items, and knowledge upload records

Dependencies:

- core SaaS tables

### 2.5 Create audit and message tables

Priority: P0

Business reason:

The system must keep a trustworthy history of what was submitted, changed, sent, and received.

Acceptance criteria:

- whatsapp_messages table exists
- voice_notes table exists
- audit_logs table exists
- daily_summary_messages table exists
- original provider message IDs can be stored

Dependencies:

- core SaaS tables

## Epic 3: Authentication, roles, and permissions

### 3.1 Platform admin onboarding

Priority: P0

Business reason:

For the first pilot, companies should be created by platform admin, not through public self-signup.

Acceptance criteria:

- platform admin can create a company
- platform admin can create initial owner/admin users
- company starts active/inactive based on platform admin setting

Dependencies:

- backend foundation
- core SaaS tables

### 3.1a Dashboard login foundation

Priority: P0

Business reason:

Users need a normal login screen before the dashboard can be tested like a real SaaS product.

Acceptance criteria:

- users can be created with a password hash
- dashboard has a login screen
- backend supports login by email or phone number
- backend returns a signed bearer token after successful login
- dashboard can load the signed-in user's company context
- seed demo data prints usable demo login credentials
- signed login tokens are not treated as platform-admin tokens

Dependencies:

- core SaaS tables
- user setup APIs

### 3.2 Company user management

Priority: P0

Business reason:

Company owners/admins must be able to add project team members.

Acceptance criteria:

- owner/admin can add users
- owner/admin can deactivate users
- owner/admin can assign users to projects
- user phone number is captured for WhatsApp identification
- dashboard can list company users for owner/admin users
- dashboard can create company users with a temporary password
- dashboard can list selected-project assignments
- dashboard can assign users to selected projects with progress, manpower, material, and dashboard permissions
- dashboard edit/deactivate/remove-assignment actions are still future work

Dependencies:

- authentication
- project management

### 3.3 Role-based access control

Priority: P0

Business reason:

Different users should only access what they are allowed to access.

Acceptance criteria:

- owner can access all company projects
- project manager can access assigned projects only
- site engineer can access assigned projects only
- supervisor can access assigned projects only
- storekeeper can enter material received/issued only for assigned projects
- platform admin can manage companies
- backend APIs enforce company isolation
- backend reporting APIs enforce progress, manpower, and material permissions separately
- storekeepers are blocked from progress and manpower reporting APIs
- project users are blocked from other companies' data
- dashboard navigation and reporting sections adapt to the signed-in user's role
- dashboard handles restricted reporting APIs gracefully instead of showing a generic error

Dependencies:

- user management
- project assignments

## Epic 4: Project setup and knowledgebase

### 4.1 Project management

Priority: P0

Business reason:

Every report must belong to a project.

Acceptance criteria:

- owner/admin can create projects
- owner/admin can edit projects
- project has name, code, location, status, start date, and end date
- users can be assigned to projects
- dashboard can create projects with name, code, location, schedule dates, status, and timezone
- dashboard can show selected-project setup details
- dashboard project edit/archive/delete actions are still future work

Dependencies:

- company setup
- user management

### 4.2 Downloadable project templates

Priority: P0

Business reason:

Customers need a simple way to provide project data in a clean format.

Acceptance criteria:

- downloadable templates exist for users/roles
- downloadable templates exist for areas/sub-areas
- downloadable templates exist for activities/schedule
- downloadable templates exist for BOQ/material list
- downloadable templates exist for units
- optional templates exist for scope of work and resource plan
- foundation API can generate `.xlsx` templates for units, activities, locations, BOQ, and schedule

Dependencies:

- dashboard foundation

### 4.3 Project knowledgebase upload

Priority: P0

Business reason:

Uploaded project data becomes the reference used to validate WhatsApp entries.

Acceptance criteria:

- user can upload completed templates
- system validates template format
- system shows validation errors
- system imports valid rows
- upload history is visible
- knowledgebase is linked to the correct project
- foundation API can import `.xlsx` templates for units, activities, locations, BOQ, and schedule
- dashboard can download `.xlsx` templates for units, activities, locations, BOQ, and schedule
- dashboard can upload completed `.xlsx` templates for the selected project
- dashboard can show selected-project knowledgebase upload history
- dashboard editing of imported knowledgebase records is still future work

Dependencies:

- project templates
- project knowledgebase tables

### 4.4 Knowledgebase-based validation

Priority: P0

Business reason:

The assistant should not blindly accept wrong locations, units, materials, or activities.

Acceptance criteria:

- progress entries are checked against activities, units, and locations
- material entries are checked against BOQ/material list and units
- manpower entries are checked against project locations and trade/resource terms where available
- invalid or unclear entries trigger clarification
- unresolved entries can be saved as `needs review` or `unmatched`

Dependencies:

- project knowledgebase upload
- AI assistant/parser

## Epic 5: WhatsApp provider integration

### 5.1 Provider-flexible WhatsApp adapter

Priority: P0

Business reason:

The product should not be locked to Twilio. It should be ready for Meta WhatsApp Cloud API or another provider.

Acceptance criteria:

- inbound provider payload is normalized into one internal message format
- outbound replies use one internal sending interface
- provider name is stored
- provider message ID is stored
- raw provider metadata can be stored for troubleshooting
- inbound generic/test and Meta-style text message payloads can be received and stored

Dependencies:

- backend foundation

### 5.2 Pilot WhatsApp webhook

Priority: P0

Business reason:

Users need to submit data through WhatsApp.

Acceptance criteria:

- webhook receives inbound messages
- webhook validates request where provider supports validation
- system identifies user by WhatsApp phone number
- system rejects inactive or unknown users politely
- system routes valid messages to assistant workflow

Dependencies:

- WhatsApp adapter
- user management

### 5.3 WhatsApp outbound replies

Priority: P0

Business reason:

The assistant must ask follow-up questions, send confirmations, and send daily summaries.

Acceptance criteria:

- assistant can send text replies
- assistant can send confirmation prompts
- assistant can send daily summaries
- outbound messages are logged
- delivery status is stored where available
- generic/test outbound replies are simulated locally for development
- provider-specific outbound messages are queued until real Meta/provider credentials are configured

Dependencies:

- WhatsApp adapter

## Epic 6: AI assistant and natural conversation

### 6.1 Natural message parser

Priority: P0

Business reason:

Users should not need commands like `!start`. The assistant should understand normal text.

Acceptance criteria:

- parser detects progress intent
- parser detects manpower intent
- parser detects material received intent
- parser detects material issued intent
- parser detects image/proof relationship
- parser extracts project, location, activity/material/trade, quantity, unit, and date where available
- parser asks only for missing information
- first parser output is stored separately from raw WhatsApp messages for audit and review

Dependencies:

- backend foundation
- AI configuration

### 6.2 Professional assistant behavior

Priority: P0

Business reason:

The assistant should feel useful, structured, and professional, not robotic or offensive.

Acceptance criteria:

- assistant avoids command-first language
- assistant supports English, Hindi, and Hinglish common cases
- assistant responds professionally to obscene, offensive, or irrelevant messages
- assistant redirects user back to project reporting
- assistant does not make offensive comments

Dependencies:

- natural parser

### 6.3 Confirmation before save

Priority: P0

Business reason:

AI can misunderstand field data. Confirmation protects trust.

Acceptance criteria:

- assistant summarizes interpreted entry
- user can confirm
- user can correct details
- system saves only after confirmation
- original message and final structured record are both stored
- foundation conversation state is stored after each parsed WhatsApp message
- conversation state shows whether the assistant is waiting for confirmation, missing information, or redirecting the user professionally
- dashboard can show assistant parse results, missing fields, and conversation states for owner/admin users
- first confirmed-save workflow stores progress, manpower, and material records after simple replies like `Yes`, `OK`, or `haan`
- first correction workflow updates pending confirmations for simple quantity, unit, location, activity, material, and manpower changes before save
- first missing-information follow-up workflow completes pending drafts from short replies before save
- project-selection follow-up supports users assigned to multiple active projects

Dependencies:

- parser
- reporting tables

### 6.4 AI configuration by company

Priority: P0 foundation, P1 self-service UI

Business reason:

Some customers may use platform AI keys; others may bring their own keys.

Acceptance criteria:

- company can use platform-managed AI keys
- company can be configured for company-owned AI keys
- owner/admin dashboard can update AI mode and AI insights subscription status
- backend exposes a company AI settings endpoint
- keys are stored securely
- keys are never logged
- real company-owned key entry, validation, masking, and encrypted storage are still future secure-secret work

Dependencies:

- company settings
- secrets management

## Epic 7: Voice and media

### 7.1 Voice note transcription

Priority: P0

Business reason:

Field users may prefer voice notes, especially in Hindi/Hinglish.

Acceptance criteria:

- system receives voice note
- voice note is stored as media
- voice is transcribed
- transcript is processed like text
- transcript and original media reference are stored

Dependencies:

- WhatsApp adapter
- object storage
- AI/transcription service

### 7.2 Image/proof capture

Priority: P0

Business reason:

Images create trust and proof for site progress and material movement.

Acceptance criteria:

- system receives image
- final production image binary is stored in object storage
- image is linked to project, user, and timestamp
- first foundation stores generic/Meta image references in `media_files` for single-project users
- system asks for project name/code when the sender has multiple active projects
- next project name/code reply can link the pending image/proof to the selected project
- caption is processed if present
- if caption is missing, assistant asks what the image relates to
- downloading provider media into long-term object storage is still future work

Dependencies:

- WhatsApp adapter
- object storage

## Epic 8: Core reporting workflows

### 8.1 Progress workflow

Priority: P0

Business reason:

Progress reporting is one of the main reasons the product exists.

Acceptance criteria:

- user can report progress by text
- user can report progress by voice
- assistant extracts activity, quantity, unit, location, date, and project
- entry is validated against project knowledgebase
- assistant summarizes and confirms
- confirmed entry is saved
- optional image can be linked

Dependencies:

- parser
- knowledgebase validation
- progress table

### 8.2 Manpower workflow

Priority: P0

Business reason:

Project managers need to understand labor allocation and site attendance patterns.

Acceptance criteria:

- user can report manpower by text
- user can report manpower by voice
- assistant extracts trade/category, count, location, date, and project
- assistant summarizes and confirms
- confirmed entry is saved
- manpower dashboard can use the data

Dependencies:

- parser
- manpower table

### 8.3 Material received workflow

Priority: P0

Business reason:

Material received data supports stock tracking and proof of delivery.

Acceptance criteria:

- storekeeper/owner can report material received
- assistant extracts material, quantity, unit, supplier, project, and date
- material is validated against BOQ/material list where available
- proof image is strongly required for pilot
- assistant summarizes and confirms
- confirmed entry updates stock balance

Dependencies:

- parser
- material transactions
- media capture
- stock balance

### 8.4 Material issued workflow

Priority: P0

Business reason:

Material issued data helps understand consumption and current stock.

Acceptance criteria:

- storekeeper/owner can report material issued
- assistant extracts material, quantity, unit, purpose, location, project, and date
- system checks available stock
- assistant summarizes and confirms
- confirmed entry updates stock balance

Dependencies:

- parser
- material transactions
- stock balance

## Epic 9: Dashboard and analytics

### 9.1 Dashboard project filters

Priority: P0

Business reason:

Users need to view one project or multiple projects across selected dates.

Acceptance criteria:

- project dropdown supports one project
- project dropdown supports multiple projects
- filters support date and date range
- filters support user, activity, and material where relevant

Dependencies:

- dashboard foundation
- project data APIs

### 9.2 Project manager summary cards

Priority: P0

Business reason:

Project managers need fast, daily visibility without reading every row.

Acceptance criteria:

- card for today's progress entries
- card for today's manpower
- card for today's material received
- card for today's material issued
- card for current low-stock materials
- card for unmatched/needs-review entries
- card for images uploaded today
- first live dashboard view can load saved progress, manpower, material, stock, and media records
- first project-manager analytics cards show progress by area, manpower distribution, material stock highlights, and attention items
- reporting workspace shows proof gaps, low stock, and image/proof counts for the selected project/date range
- reporting tables show helper text, row counts, clear empty states, and role-aware restricted messages

Dependencies:

- reporting APIs

### 9.3 Progress analytics

Priority: P0

Business reason:

Managers need to understand total completed work and compare it with plan.

Acceptance criteria:

- total progress till date by area is visible
- plan vs actual view is visible
- user can filter by project/date range
- data comes from confirmed progress entries and schedule/BOQ where available

Dependencies:

- progress workflow
- project schedule/BOQ

### 9.4 Manpower analytics

Priority: P0

Business reason:

Managers need to understand workforce distribution over time.

Acceptance criteria:

- manpower distribution chart exists
- chart supports last week
- chart supports last month
- chart can be filtered by project
- chart can be filtered by trade/category

Dependencies:

- manpower workflow

### 9.5 Tomorrow's activities

Priority: P0

Business reason:

Project managers need help knowing what should happen next based on plan and actual progress.

Acceptance criteria:

- dashboard shows tomorrow's planned activities from schedule
- dashboard considers completed work where available
- dashboard flags delayed or pending activities where possible
- output is understandable to project managers

Dependencies:

- schedule upload
- progress workflow

### 9.6 Material stock dashboard

Priority: P0

Business reason:

Material stock visibility is required for the MVP.

Acceptance criteria:

- current stock is visible by material
- total received is visible
- total issued is visible
- current balance is visible
- low-stock alert placeholder exists

Dependencies:

- material received workflow
- material issued workflow

### 9.7 AI insights for subscribers

Priority: P0 if AI subscription is part of pilot, otherwise P1

Business reason:

AI insights can become a premium feature.

Acceptance criteria:

- dashboard has AI insights section
- section is visible only to AI subscribers
- non-subscribers do not see premium insights
- insights can summarize risks, unusual patterns, or missing data

Dependencies:

- AI configuration
- dashboard analytics

## Epic 10: Reports, summaries, and exports

### 10.1 Excel export

Priority: P0

Business reason:

Excel is the MVP reporting format.

Acceptance criteria:

- export supports selected project/date range
- export includes progress sheet
- export includes manpower sheet
- export includes material received sheet
- export includes material issued sheet
- export includes image/proof links sheet
- export does not include summary sheets for MVP
- dashboard export creates one `.xlsx` workbook for the selected project/date range
- workbook contains separate accessible sheets for progress, manpower, material movement, stock, and media/proof records
- workbook generation currently happens in the browser without an external spreadsheet dependency

Dependencies:

- dashboard filters
- reporting APIs

### 10.2 Daily WhatsApp summary

Priority: P0

Business reason:

Owners and project managers need a daily snapshot without opening the dashboard.

Acceptance criteria:

- summary is sent automatically on WhatsApp
- default time is 7:00 PM local project time
- summary time is configurable
- summary recipients are configurable
- summary includes progress, manpower, material received, material issued, stock highlights, proof/image highlights, and unmatched entries
- summary message and delivery status are stored
- foundation API can preview and manually send the summary before the scheduler is added
- default foundation recipients are active project users with dashboard access and WhatsApp phone numbers
- in-app scheduler checks enabled settings and sends due summaries automatically
- scheduler avoids sending the same project/date summary more than once
- dashboard can configure summary settings, preview message text, send manually, and show send history
- dashboard can show inbound/outbound WhatsApp message audit logs for owner/admin users
- dashboard can create and list WhatsApp provider accounts for owner/admin users

Dependencies:

- WhatsApp outbound replies
- reporting APIs
- daily summary settings

## Epic 11: Security, reliability, and audit

### 11.1 Secret management

Priority: P0

Business reason:

AI keys, WhatsApp credentials, and database credentials must be protected.

Acceptance criteria:

- no credentials are hardcoded
- secrets are loaded from environment or secrets manager
- AI keys are encrypted or stored by reference
- secrets are not printed in logs

Dependencies:

- backend foundation

### 11.2 Webhook security

Priority: P0

Business reason:

The WhatsApp webhook should reject suspicious or invalid requests where provider verification is available.

Acceptance criteria:

- webhook validation is implemented where supported
- invalid requests are rejected
- request bodies are not logged unnecessarily
- provider-specific verification is isolated inside provider adapter

Dependencies:

- WhatsApp adapter

### 11.3 Audit logging

Priority: P0

Business reason:

The product must track who did what and when.

Acceptance criteria:

- key create/update actions are logged
- WhatsApp submissions are traceable to user and provider message
- dashboard actions are traceable to user
- daily summaries are logged

Dependencies:

- database
- authentication

## Epic 12: Pilot readiness

### 12.1 Pilot seed setup

Priority: P0

Business reason:

The first pilot should be easy to configure and test.

Acceptance criteria:

- pilot company can be created
- pilot project can be created
- pilot users can be assigned
- sample knowledgebase templates can be uploaded
- test WhatsApp numbers can be configured
- repeatable demo seed script creates realistic dashboard data for testing and demos

Dependencies:

- company/project/user management
- knowledgebase upload
- WhatsApp provider

### 12.2 MVP demo script

Priority: P0

Business reason:

A clear demo helps sell, test, and onboard.

Acceptance criteria:

- demo script covers text progress entry
- demo script covers voice entry
- demo script covers material received with image
- demo script covers dashboard analytics
- demo script covers Excel export
- demo script covers daily summary

Dependencies:

- core workflows

### 12.3 Pilot feedback tracker

Priority: P0

Business reason:

The team needs to learn quickly from the first users.

Acceptance criteria:

- feedback categories exist
- bugs can be logged
- feature requests can be logged
- workflow confusion can be logged
- weekly review process is defined

Dependencies:

- pilot plan

## Suggested build sequence

1. Clean repository and documentation baseline
2. Backend foundation
3. PostgreSQL and migrations
4. Core SaaS tables
5. Authentication and roles
6. Company, project, and user management
7. Project knowledgebase templates and upload
8. WhatsApp provider adapter
9. Natural assistant parser
10. Progress workflow
11. Manpower workflow
12. Material received/issued workflow
13. Image and voice support
14. Dashboard tables and filters
15. Dashboard analytics
16. Excel export
17. Daily WhatsApp summary
18. Security hardening
19. Pilot seed setup
20. Pilot demo and feedback process

## First sprint recommendation

Sprint 1 should not try to build the full assistant.

Recommended Sprint 1 scope:

- clean repo setup
- backend skeleton
- frontend skeleton
- PostgreSQL setup
- core company/user/project tables
- basic authentication placeholder
- initial project knowledgebase template definitions
- implementation issue list in GitHub

The goal of Sprint 1 is to create the foundation that every other feature depends on.
