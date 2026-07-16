# 12 GitHub Branching and Repo Setup

## Target repository

The clean MVP repository should be:

```text
CognitoConsulting/Cognos-AI
```

The product name can remain:

```text
Cognos AI
```

## Repository rules

- repository should be private
- default branch should be `main`
- old prototype code should not be copied directly
- MVP documentation should be committed first
- code should be added through feature branches and pull requests

## Why a clean repository

The old repository is useful as a prototype and audit source.

The new MVP should have a clean foundation because:

- old code mixes several unfinished systems
- CSV database approach should be replaced
- WhatsApp provider should be flexible
- dashboard should be rebuilt cleanly
- authentication and permissions need a proper SaaS design

## Branch strategy

Use a simple branch strategy.

### main

Stable source of truth.

Rules:

- should always be safe
- only merge reviewed work
- no direct experimental commits

### feature branches

Use one feature branch per meaningful piece of work.

Examples:

```text
feature/docs-and-product-spec
feature/backend-foundation
feature/frontend-foundation
feature/database-foundation
feature/auth-roles
feature/project-knowledgebase
feature/whatsapp-provider-adapter
feature/ai-assistant-parser
feature/voice-transcription
feature/dashboard-analytics
feature/daily-summary
feature/excel-export
```

### fix branches

Use for bugs.

Examples:

```text
fix/material-stock-balance
fix/webhook-validation
fix/export-date-filter
```

### release branch

Use when preparing pilot release.

Example:

```text
release/mvp-pilot
```

## GitHub issue labels

Recommended labels:

- P0
- P1
- P2
- backend
- frontend
- database
- whatsapp
- ai
- dashboard
- security
- docs
- pilot
- bug
- enhancement

## GitHub milestones

Recommended milestones:

### MVP Foundation

Backend, frontend, database, authentication, company/project/user setup.

### MVP WhatsApp Workflows

Provider adapter, assistant parser, progress, manpower, materials, image, and voice.

### MVP Dashboard and Reporting

Dashboard filters, analytics, material stock, Excel export, daily WhatsApp summary.

### Pilot Readiness

Security hardening, seed setup, demo script, test plan, pilot feedback process.

## Pull request rules

Each pull request should explain:

- what changed
- why it changed
- how it was tested
- which issue it closes

For MVP speed, review can be lightweight, but every PR should still be understandable.

## Initial commit recommendation

First commit should include:

- README
- MVP documentation
- implementation backlog
- branching plan
- empty backend/frontend folders or starter skeleton

Suggested commit message:

```text
Initial MVP planning and clean repository setup
```

## Current blocker

The GitHub connector currently cannot access:

```text
CognitoConsulting/Cognos-AI
```

GitHub returns `404 Not Found`.

Likely causes:

- repository is private and connector access has not been granted
- repository was created under a different owner
- repository name differs by spelling/case
- GitHub app permissions need refresh

Do not push to:

```text
CognitoConsulting/CognosAI
```

That is a different repository and should be ignored for this MVP.
