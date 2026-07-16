# 07 Dashboard Requirements

## Dashboard purpose

The dashboard is required for MVP.

It should let company users view, filter, and export data captured from WhatsApp.

## Main dashboard users

- company owner
- admin
- project manager
- site engineer
- supervisor
- back-office user

## Required screens

### Login

Users log in securely.

### Company dashboard

Shows company-level overview.

MVP widgets:

- active projects
- users
- today's progress entries
- today's manpower count
- today's material transactions
- current material stock alerts
- projects needing review

### Project dashboard

Shows one project or multiple selected projects.

Required filters:

- project dropdown with single-project and multi-project selection
- date
- date range
- user
- activity
- material

Required project manager analytics:

- summary cards for today's key activity
- total progress till date by area
- manpower distribution chart for last week/month
- plan vs actual progress
- tomorrow's activities based on completed work and project schedule
- material stock
- entries needing review
- AI insights section for AI subscribers

Suggested summary cards:

- progress entries today
- total quantity completed today
- manpower today
- material received today
- material issued today
- current low-stock materials
- pending/unmatched entries
- images uploaded today

### Progress view

Table showing:

- date
- activity
- quantity
- unit
- location
- reported by
- original message
- linked images

### Manpower view

Table showing:

- date
- trade/category
- count
- location
- reported by

### Materials view

Table showing:

- date
- material
- received or issued
- quantity
- unit
- supplier or purpose
- proof image
- reported by

The dashboard should also show current stock balance:

- total received
- total issued
- current balance
- last updated

### Image/proof view

Shows images linked to:

- progress
- manpower
- materials
- general site updates

### Team management

Admins can:

- add users
- deactivate users
- assign users to projects
- set roles

Role behavior:

- Owner can access everything across all projects.
- Project Manager can enter and view data for assigned projects.
- Site Engineer can enter and view data for assigned projects.
- Supervisor can enter and view data for assigned projects.
- Storekeeper can enter material received and material issued for assigned projects.

### Project management

Admins can:

- create project
- edit project
- add project locations
- upload project knowledgebase
- download sample templates
- assign users

### Project knowledgebase

Admins/project managers can upload:

- schedule
- scope of work
- BOQ
- resource plan
- user list with roles
- areas and sub-areas

Dashboard should show:

- upload type
- upload date
- uploaded by
- validation status
- import errors, if any
- last updated timestamp

This knowledgebase is used by the WhatsApp assistant to validate user entries.

### Integration settings

Admins should be able to view and eventually configure technical settings.

WhatsApp provider settings should show:

- selected WhatsApp provider
- connected WhatsApp number
- webhook status
- last successful inbound message
- last outbound message status

The dashboard should be designed so the provider can later be Meta WhatsApp Cloud API or another Meta-compatible provider.

AI settings should allow:

- use platform-managed AI keys
- use company-owned AI keys
- validate company-owned keys
- switch AI key mode without changing user workflows

Company-owned AI keys should be stored securely and should not be visible again after saving.

### Excel export

Export selected project/date range.

Export should include:

- progress
- manpower
- material received
- material issued
- image links

Export should not include summary sheets in MVP.

Summary exports can be added later if customers ask for them.

### Daily WhatsApp summary settings

Admins/project managers should be able to configure:

- summary recipients
- summary time
- project or projects included
- whether unmatched entries should be highlighted

Daily summaries should be sent automatically on WhatsApp.

Default:

- 7:00 PM local project time

The time should be configurable.
