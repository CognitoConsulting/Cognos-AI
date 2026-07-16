# 04 Feature Backlog

## P0: Must have for MVP pilot

### Platform foundation

- Create new backend using Python/FastAPI.
- Set up PostgreSQL.
- Create company, user, project, and project-user assignment tables.
- Create dashboard authentication.
- Add role-based access.
- Platform admin can create company and initial users.
- Company owner/admin can add more users later.
- Add company-level settings for WhatsApp provider and AI configuration.

### WhatsApp capture

- WhatsApp provider webhook.
- Provider-flexible WhatsApp adapter so the product is not locked to Twilio.
- Keep the architecture ready for Meta WhatsApp Cloud API webhook integration.
- Registered user identification by phone number.
- Natural assistant conversation without requiring special commands.
- Intelligent project selection or inference.
- Progress capture.
- Manpower capture.
- Material received capture.
- Material issued capture.
- Image capture.
- Voice note capture and transcription.
- Confirmation before saving.
- Missing-information follow-up questions.
- Professional handling of obscene, offensive, or irrelevant messages.
- Automatic daily WhatsApp summary.

### Dashboard

- Company dashboard.
- Project dashboard.
- Single-project and multi-project dropdown.
- Project knowledgebase upload.
- Downloadable sample templates.
- Date-wise filter.
- Date-range filter.
- Project manager summary cards.
- Total progress till date by area.
- Manpower distribution chart for last week/month.
- Plan vs actual dashboard.
- Tomorrow's activities based on completed work and schedule.
- Material stock dashboard.
- AI insights section for AI subscribers.
- Progress table.
- Manpower table.
- Material transactions table.
- Image/proof view.
- Excel export.
- AI configuration screen.
- WhatsApp provider configuration screen.

### Language support

- Hindi/Hinglish support for common progress messages.
- Hindi/Hinglish support for manpower messages.
- Hindi/Hinglish support for material messages.
- Hindi/Hinglish support for common voice notes.

### Data and audit

- Store all records in PostgreSQL.
- Store images in object storage.
- Store voice transcript.
- Save original WhatsApp message.
- Save WhatsApp provider name and provider message ID.
- Save who submitted each entry and when.
- Save daily summary messages and delivery status.
- Track material stock balance.
- Use uploaded project knowledgebase for validation.
- Store AI configuration choice per company.

### Project knowledgebase

- Upload project schedule.
- Upload BOQ.
- Upload user list with roles.
- Upload areas and sub-areas.
- Upload units.
- Upload activity list or schedule activities.
- Support scope of work as optional.
- Support resource plan as optional.
- Validate uploaded templates.
- Use project knowledgebase during WhatsApp data validation.

### AI configuration

- Platform-managed AI keys.
- Company-owned AI keys.
- Secure storage for company-owned keys.
- Ability to switch a company between platform keys and own keys.
- Usage tracking by company.

## P1: Soon after MVP

- Edit submitted entries.
- Manager approval workflow.
- Rejected entry correction.
- Automated weekly summary.
- Better image gallery.
- Activity master management.
- Material master management.
- User invitation flow.
- Improved permissions.
- Low stock alerts.

## P2: Later

- Knowledge graph database.
- AI-generated insights.
- Delay risk prediction.
- Material forecasting.
- PDF reports.
- Subscription billing.
- White-label branding.
- ERP/accounting integrations.
- Advanced audit/compliance.
