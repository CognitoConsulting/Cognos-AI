# 03 Workflow Catalog

## Workflow 1: Natural WhatsApp conversation

### User

Site engineer, project manager, store incharge, or owner.

### Trigger

User sends any normal message on WhatsApp.

Examples:

```text
Hi, I want to update today's progress.
```

```text
Aaj Tower A floor 2 me 50 sqm plaster complete hua.
```

```text
100 cement bags received with photo.
```

### Steps

1. System reads WhatsApp phone number.
2. System checks whether user exists.
3. System checks whether user is active.
4. System understands the user’s intent from the message.
5. System loads assigned projects and project knowledgebase.
6. If project is unclear, assistant asks which project.
7. If required data is missing, assistant asks only for missing information.
8. If enough data is present, assistant summarizes the entry and asks for confirmation before saving.

### MVP requirement

Must work.

## Workflow 2: Record progress

### User

Site engineer or project manager.

### Trigger

User sends a progress update on WhatsApp.

Example:

```text
Aaj Tower A floor 2 me 50 sqm plaster complete hua
```

### Steps

1. Bot receives message.
2. Parser extracts activity, quantity, unit, and location.
3. System validates project, unit, activity, area, and sub-area using the project knowledgebase.
4. If information is missing or invalid, assistant asks a clear follow-up question.
5. If information is complete, assistant summarizes the entry professionally.
6. User confirms.
7. System saves progress entry.

### MVP requirement

Must work.

## Workflow 3: Capture images

### User

Site engineer, project manager, or store incharge.

### Trigger

User sends image on WhatsApp.

### Steps

1. System receives image from the configured WhatsApp provider.
2. System stores image in object storage.
3. System links image to project, user, timestamp, and caption.
4. If caption contains progress/material/manpower data, system processes caption.
5. If no caption is provided, assistant asks what the image relates to.

### MVP requirement

Must work.

## Workflow 4: Record manpower

### User

Site engineer or project manager.

### Trigger

User sends manpower update.

Example:

```text
10 mason, 5 helper Tower B par aaye
```

### Steps

1. Parser detects manpower/trade counts.
2. System validates project, trade/category, area, and sub-area using the project knowledgebase.
3. If information is missing, assistant asks for only the missing detail.
4. Bot asks for confirmation when the entry is clear.
5. User confirms.
6. System saves manpower record.

### MVP requirement

Must work.

## Workflow 5: Material received

### User

Store incharge or owner.

### Trigger

User reports material received.

Example:

```text
100 cement bags received from supplier ABC
```

### Steps

1. Parser extracts material, quantity, unit, supplier, project.
2. System validates material, unit, project, and location against project knowledgebase and BOQ where available.
3. User uploads proof image. For the pilot, proof image should be strongly required for material received.
4. Bot asks for confirmation.
5. System saves material received transaction.
6. Inventory balance updates.

### MVP requirement

Must work.

## Workflow 6: Material issued

### User

Store incharge, site engineer, or project manager.

### Trigger

User reports material issued.

Example:

```text
20 cement bags issued for plastering Tower A
```

### Steps

1. Parser extracts material, quantity, unit, purpose, location.
2. System validates material, unit, purpose, area, and sub-area against project knowledgebase.
3. System checks available stock.
4. User uploads proof image if available.
5. Bot asks for confirmation.
6. System saves material issued transaction.
7. Inventory balance updates.

### MVP requirement

Must work.

## Workflow 7: Dashboard review

### User

Owner, admin, project manager.

### Trigger

User opens dashboard.

### Steps

1. User logs in.
2. User selects one project or multiple projects.
3. User selects date or date range.
4. Dashboard shows progress, manpower, materials, images, and project manager analytics.
5. Dashboard shows total progress till date by area.
6. Dashboard shows manpower distribution for last week/month.
7. Dashboard shows plan vs actual.
8. Dashboard shows tomorrow's activities based on completed work and schedule.
9. Dashboard shows material stock.
10. AI subscribers see AI insights.
11. User exports Excel if needed.

### MVP requirement

Must work.

## Workflow 8: Project knowledgebase upload

### User

Company admin or project manager.

### Trigger

User uploads project setup data from the dashboard.

### Data types

- schedule
- scope of work
- BOQ
- resource plan
- user list with roles
- areas
- sub-areas

### Steps

1. User downloads sample template.
2. User fills project data.
3. User uploads completed template.
4. System validates the template format.
5. System imports project knowledgebase.
6. WhatsApp assistant uses this knowledgebase to validate future entries.

### MVP requirement

Must work for at least the essential templates required for validation.

## Workflow 9: Voice entry

### User

Site engineer, project manager, or store incharge.

### Trigger

User sends voice note on WhatsApp.

### Steps

1. System receives voice note.
2. System transcribes voice to text.
3. Parser extracts intent and data from transcript.
4. System validates data against project knowledgebase.
5. Assistant asks for missing information or confirms the entry.
6. System stores original transcript and final structured record.

### MVP requirement

Required for MVP, but can begin with support for common Hindi/Hinglish site updates.

## Workflow 10: Automatic daily WhatsApp summary

### User

Owner, project manager, or other configured summary recipient.

### Trigger

System reaches the configured daily summary time.

Default:

- 7:00 PM local project time

This should be configurable per project or company.

### Steps

1. System collects the day's confirmed entries.
2. System summarizes progress, manpower, material received, material issued, and important images/proof.
3. System highlights missing or unmatched entries that need review.
4. System sends the summary automatically on WhatsApp.
5. System stores the summary message and delivery status.

### MVP requirement

Must work for the pilot.

## Workflow 11: WhatsApp provider webhook

### User

System administrator or technical admin.

### Trigger

The company decides which WhatsApp provider/webhook will be used.

### Steps

1. Admin configures the selected WhatsApp provider.
2. Provider sends inbound WhatsApp messages to the application webhook.
3. System verifies the webhook request where supported.
4. System converts the provider payload into one internal message format.
5. Assistant processes the message normally.
6. System sends replies through the configured provider.
7. System stores provider name, provider message ID, and raw event metadata for audit.

### MVP requirement

The MVP should be built with provider flexibility. The final long-term provider can be Meta WhatsApp Cloud API or another Meta-compatible provider once the decision is finalized.

## Workflow 12: AI key configuration

### User

SaaS owner, company admin, or technical admin.

### Trigger

A company chooses whether to use platform-provided AI keys or its own AI keys.

### Steps

1. Admin opens AI settings.
2. Admin selects either platform-managed AI or company-owned AI keys.
3. If company-owned keys are selected, admin enters the required key/configuration.
4. System validates that the key works.
5. System stores the key securely.
6. Future AI parsing, transcription, and assistant replies use the selected configuration.

### MVP requirement

Should be supported in the product design. If full self-service setup is too much for the first pilot, the database and architecture should still support it from day one.
