# 09 Technical Decisions

## Decision 1: Use Python/FastAPI for new backend

Reason:

The product needs AI parsing, reporting, Excel exports, data processing, and future knowledge graph work.

Python is a strong fit for this.

## Decision 2: Use PostgreSQL as primary database

Reason:

CSV is not suitable for SaaS.

PostgreSQL supports:

- multi-company data
- reliable reporting
- filtering
- permissions
- audit history
- future scale

## Decision 3: Use a provider-flexible WhatsApp webhook layer

Reason:

The long-term WhatsApp provider is not finalized yet.

The product should not be locked to Twilio.

The MVP should use a WhatsApp provider adapter that can support:

- Meta WhatsApp Cloud API webhook
- Twilio, if needed for a pilot
- another Meta-compatible WhatsApp provider

The internal application should work with one normalized message format, regardless of provider.

This keeps the product ready to incorporate the final Meta webhook setup as soon as the provider decision is made.

## Decision 4: Store images in object storage

Reason:

Images should not live inside the app folder.

Use:

- AWS S3
- Cloudflare R2
- Azure Blob
- or similar

## Decision 5: Use PostgreSQL for graph-like MVP knowledge

Reason:

Knowledge graphs are useful, but a separate graph database may slow MVP delivery.

Start with relational tables for:

- activities
- synonyms
- materials
- units
- dependencies

Later consider Neo4j if needed.

## Decision 6: Dashboard is required for MVP

Reason:

The customer needs date-wise viewing, date-range filtering, team management, project management, analytics, and Excel export.

The dashboard should support:

- single-project and multi-project selection
- summary cards for project managers
- total progress till date by area
- manpower distribution for last week/month
- plan vs actual
- tomorrow's activities based on completed work and schedule
- material stock
- AI insights for AI subscribers

## Decision 7: Project knowledgebase is required for MVP

Reason:

User-entered WhatsApp data must be validated against actual project data.

The system should allow users to upload:

- schedule
- BOQ
- user list with roles
- areas and sub-areas
- units
- activities or schedule activities

Scope of work and resource plan should be supported, but they should not block the first pilot.

This is essential for accurate validation.

## Decision 8: Approval workflow is not MVP

Reason:

Approval is useful, but the pilot can save confirmed entries directly.

Add approval in a later version.

Entries that cannot be matched confidently to the project knowledgebase should be saved as `needs review` or `unmatched`, not silently discarded.

## Decision 9: Excel export before PDF

Reason:

Excel is enough for MVP and easier to deliver quickly.

## Decision 10: Natural assistant over command-driven bot

Reason:

Users should not need to remember commands like `!hi` or `!start`.

The assistant should understand natural text or voice messages, ask for missing details, and respond professionally.

Even when the assistant understands a complete message, it should summarize the interpreted entry and ask for confirmation before saving.

## Decision 11: Voice input is required

Reason:

Site users may prefer voice notes, especially in Hindi/Hinglish.

The system should transcribe voice and process it like text.

## Decision 12: Support platform AI keys and company-owned AI keys

Reason:

Some customers may prefer simplicity and use the SaaS owner's AI keys.

Other customers may want to provide their own AI keys for cost control, data governance, procurement, or internal policy reasons.

The product should support both modes:

- platform-managed AI keys
- company-owned AI keys

The AI key choice should be configured per company.

AI keys must be stored securely and should never appear in normal logs, exports, or user-facing screens after setup.

## Decision 13: Daily WhatsApp summary is required for MVP

Reason:

Owners and project managers should not have to open the dashboard every day to know what happened.

The system should automatically send a daily WhatsApp summary covering:

- progress
- manpower
- material received
- material issued
- important proof/images
- unmatched or needs-review entries

The default send time should be 7:00 PM local project time.

Admins should be able to configure the summary time.

## Decision 14: Platform admin creates companies first

Reason:

For the ASAP pilot, public self-signup would add unnecessary complexity.

The platform admin should create the company and initial users.

After that, company owners/admins can add more users.

## Decision 15: AI insight access should be subscription-controlled

Reason:

Basic AI parsing is part of the product workflow.

Advanced AI insights should be available only to AI subscribers.
