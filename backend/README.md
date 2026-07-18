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
- WhatsApp image/proof capture into `media_files` for users with one active project
- WhatsApp voice-note capture into `voice_notes`, with provider-supplied transcripts processed like text
- OpenAI transcription adapter for supported downloadable voice/audio files
- Meta WhatsApp media-ID URL resolution for inbound media/voice references
- local object-storage-style persistence for inbound WhatsApp media files
- S3-compatible media storage provider interface for AWS S3, Cloudflare R2, and similar services
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
- generic/test image payloads with media URL/provider media ID
- Meta WhatsApp Cloud API style image/video/document references

It normalizes inbound provider payloads and stores them in `whatsapp_messages`.

For image/proof messages, the webhook can create `media_files` records when the sender belongs to exactly one active project. If the sender belongs to multiple projects, the system asks for the project name/code and can use the next text reply to link the pending image/proof to the selected project.

When a photo/proof arrives within 30 minutes of the same user's latest saved progress, manpower, or material entry for that project, the media record is linked to that entry. Material transactions also move from `not_attached` to `attached` proof status.

This media foundation stores the supplied media URL or provider media reference. It does not yet download provider media into long-term object storage.

For voice notes, the webhook creates a `voice_notes` audit record. If the inbound provider or test payload includes a transcript, that transcript is processed through the same assistant workflow as a typed WhatsApp message. If no transcript is available, the voice note is stored and the user is asked to type the update until real transcription is configured.

If `VOICE_TRANSCRIPTION_ENABLED=true`, `VOICE_TRANSCRIPTION_PROVIDER=openai`, and the correct OpenAI key is available, the backend can download supported audio files and send them to OpenAI's Audio Transcriptions API. The default model is `gpt-4o-mini-transcribe`.

For Meta WhatsApp Cloud API payloads that contain only a media ID, the backend can now resolve that media ID into a short-lived downloadable media URL before attempting transcription. This follows the Meta media flow: media ID -> media URL -> media download.

Meta media download uses runtime secrets only. Set either:

```text
META_WHATSAPP_ACCESS_TOKEN
```

or a phone/account-specific token:

```text
META_WHATSAPP_ACCESS_TOKEN_<PHONE_NUMBER_ID_OR_PROVIDER_ACCOUNT_ID>
```

The resolved Meta media URL is treated as runtime-only. It is not stored permanently in `media_files`, `voice_notes`, or the Cognos audit payload because Meta media URLs are short-lived and should be treated as sensitive.

Inbound WhatsApp media is now persisted through a provider-neutral storage adapter. The local development provider writes files under `MEDIA_STORAGE_LOCAL_ROOT`, which defaults to `media`, and stores durable `storage://local/...` references in `media_files` and `voice_notes`.

Local media storage settings:

```text
MEDIA_STORAGE_PROVIDER=local_filesystem
MEDIA_STORAGE_LOCAL_ROOT=media
MEDIA_STORAGE_MAX_BYTES=104857600
```

The storage layer is intentionally separate from WhatsApp and OpenAI. `local_filesystem` can be used for development, while `s3_compatible` can be used for AWS S3, Cloudflare R2, or another S3-compatible object storage provider without changing the user-facing WhatsApp workflow.

S3-compatible media storage settings:

```text
MEDIA_STORAGE_PROVIDER=s3_compatible
MEDIA_STORAGE_S3_BUCKET=<bucket-name>
MEDIA_STORAGE_S3_REGION=<region>
MEDIA_STORAGE_S3_ENDPOINT_URL=<optional-r2-or-custom-endpoint>
MEDIA_STORAGE_S3_PUBLIC_BASE_URL=<optional-public-cdn-base-url>
MEDIA_STORAGE_S3_PREFIX=<optional-key-prefix>
MEDIA_STORAGE_S3_ACCESS_KEY_ID=<access-key-id>
MEDIA_STORAGE_S3_SECRET_ACCESS_KEY=<secret-access-key>
MEDIA_STORAGE_S3_PRESIGNED_URL_TTL_SECONDS=600
```

If `MEDIA_STORAGE_S3_PUBLIC_BASE_URL` is provided, the database stores a public/CDN URL. Otherwise, it stores an internal reference like `storage://s3_compatible/<bucket>/<object-key>`.

Stored media should be opened through the backend, not by exposing internal storage paths directly:

```text
GET /companies/{company_id}/projects/{project_id}/reporting/media-files/{media_file_id}/access
GET /companies/{company_id}/whatsapp/voice-notes/{voice_note_id}/access
```

These access endpoints check the user's company/project permission first. Local files are returned as file responses. Private S3-compatible files are returned as short-lived presigned links. If a public/CDN base URL is configured, the endpoint redirects there after permission is checked.

Platform-managed AI mode uses `OPENAI_API_KEY`.

Company-owned AI mode does not store raw keys in the database. For local/pilot testing, provide the key as:

```text
COGNOS_COMPANY_OPENAI_API_KEY_<COMPANY_ID_WITH_HYPHENS_REPLACED_BY_UNDERSCORES>
```

Example:

```text
COGNOS_COMPANY_OPENAI_API_KEY_11111111_1111_1111_1111_111111111111
```

The current adapter supports downloadable files in OpenAI-supported formats such as flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, and webm. Azure Blob is still future work; the MVP now has local and S3-compatible provider paths.

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
- `media_files`: photos and proof files linked to a project or reporting record
- `voice_notes`: WhatsApp voice/audio submissions, transcript status, transcript text when available, and original provider media reference

These tables are intentionally separate from raw WhatsApp messages.
Raw messages preserve what the user sent.
Reporting records store the cleaned business data that dashboards, analytics, and exports will use.

Important user-identification rule:

- one WhatsApp phone number should map to one platform user
- this keeps inbound WhatsApp message routing unambiguous

