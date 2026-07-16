# 02 MVP Scope

## MVP must include

### SaaS foundation

- multiple companies
- multiple projects per company
- multiple users per project
- role-based access
- platform admin creates companies and initial users
- company owner/admin can add more users later

### WhatsApp workflows

- natural WhatsApp conversation without requiring commands like `!hi` or `!start`
- WhatsApp integration should not be locked to Twilio
- allow future Meta WhatsApp Cloud API webhook integration when provider decision is finalized
- user identification by WhatsApp number
- intelligent project selection or inference
- progress data capture and validation
- manpower data capture and validation
- material received capture and validation
- material issued capture and validation
- image/proof capture
- text input
- voice input
- Hindi/Hinglish support
- professional, non-offensive assistant responses

### Dashboard

- login
- company/project view
- project dropdown with single-project and multi-project selection
- project knowledgebase upload
- sample upload templates
- team management
- project management
- date-wise view
- date-range filter
- progress table
- manpower table
- material table
- image/proof gallery or list
- project manager summary cards
- total progress till date by area
- manpower distribution chart for last week/month
- plan vs actual dashboard
- tomorrow's activities based on completed work and schedule
- material stock section
- AI insights section for AI subscribers
- Excel export

### Database

- replace CSV with PostgreSQL
- store structured records properly
- store project knowledgebase data
- preserve audit trail

### AI configuration

- allow SaaS owner to provide default AI keys
- allow each customer/company to add their own AI keys if they prefer
- store AI key configuration securely
- support switching AI provider/configuration without changing user workflows

### Project knowledgebase

The MVP should include a project knowledgebase where company users can upload project-specific data.

Mandatory for MVP:

- project schedule
- BOQ
- user list with roles
- project areas
- project sub-areas
- units
- activity list or schedule activities

Supported, but not mandatory for the first pilot:

- scope of work
- resource plan

The system should provide sample templates so customers can fill data in the expected format and upload it.

The uploaded project knowledgebase should be used to validate WhatsApp entries.

Example:

If a user reports work in `Tower C`, but the uploaded project areas only include `Tower A` and `Tower B`, the assistant should ask for clarification instead of blindly saving the entry.

If the user still cannot provide a valid match, the system should save the entry as `needs review` or `unmatched` instead of losing the information.

## Role rules for MVP

- Owner can access and manage everything across all projects in the company.
- Project Manager can enter and view data only for assigned projects.
- Site Engineer can enter and view data only for assigned projects.
- Supervisor can enter and view data only for assigned projects.
- Storekeeper can enter material received and material issued entries only for assigned projects.
- Platform Admin creates companies and initial users.
- Company users can add more users if they have the correct permission.

## Data confirmation rule

The assistant should summarize the interpreted entry and ask the user to confirm before saving.

This should happen even if the user gives all information in the first message.

## Image proof rule

- Material received should strongly require a proof image for the pilot.
- Progress images are optional but encouraged.
- Manpower images are optional.
- Material issued images are optional unless the company makes them mandatory later.

## Export rule

Excel export should include detailed data sheets, not summary sheets, for the MVP.

Export should include:

- progress
- manpower
- material received
- material issued
- image/proof links

Summary sheets can be added later if users ask for them.

## MVP should not include

These should be deferred unless absolutely required for the pilot:

- manager approval workflow
- PDF reports
- payment/billing
- white-label branding
- advanced AI analytics for non-AI subscribers
- delay prediction
- full knowledge graph database
- ERP/accounting integration
- mobile app
- complex document/drawing management

## Integration flexibility

The MVP should be designed so the WhatsApp provider can be changed later.

For the pilot, the exact WhatsApp webhook provider is still open.

The system should support a provider adapter approach:

- receive inbound WhatsApp messages from the selected provider
- normalize provider-specific payloads into one internal message format
- send outbound WhatsApp replies through the selected provider
- store the original provider message ID for audit and troubleshooting

Longer term, the likely direction is a Meta WhatsApp Cloud API webhook or another direct Meta-compatible setup.

The product should avoid assuming that Twilio is the permanent provider.

## MVP success criteria

The MVP is successful if:

- site users can submit progress, manpower, materials, and images through WhatsApp
- users can submit entries through text or voice
- users do not need to remember special commands
- the assistant can ask for missing information when needed
- the assistant can log complete entries directly after confirmation
- dashboard users can view all submissions by date/project/user
- project managers can see useful analytics, including plan vs actual and material stock
- daily WhatsApp summaries are sent automatically
- owners can export Excel reports
- multiple companies can use the system without seeing each other’s data
- Hindi/Hinglish messages work for common cases
- uploaded project knowledgebase is used for validation
- WhatsApp provider can be changed later without redesigning the product
- companies can either use platform AI keys or configure their own AI keys
- the system is reliable enough for a real pilot
