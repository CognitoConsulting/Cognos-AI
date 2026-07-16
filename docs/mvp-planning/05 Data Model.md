# 05 Data Model

## Database choice

Use PostgreSQL for MVP.

Do not continue with CSV as the main database.

## Core tables

### companies

Stores each construction company using the SaaS product.

Important fields:

- id
- name
- status
- ai_key_mode
- ai_subscription_enabled
- created_at

### users

Stores all users.

Important fields:

- id
- company_id
- name
- phone
- email
- role
- is_active
- created_at

### projects

Stores project information.

Important fields:

- id
- company_id
- name
- code
- location
- status
- start_date
- end_date

### project_users

Maps users to projects.

Important fields:

- project_id
- user_id
- role_on_project
- can_enter_progress
- can_enter_manpower
- can_enter_materials
- can_view_dashboard

### project_locations

Stores project-specific areas.

Examples:

- tower
- floor
- zone
- block
- basement

Should support hierarchy:

```text
Area → Sub-area
Tower A → Floor 2
Block B → Basement
```

### project_knowledge_uploads

Tracks files uploaded to build the project knowledgebase.

Important fields:

- company_id
- project_id
- uploaded_by
- upload_type
- file_name
- storage_url
- status
- uploaded_at

Upload types:

- schedule
- scope_of_work
- BOQ
- resource_plan
- user_roles
- areas_subareas
- units
- activities

For MVP, the mandatory knowledgebase uploads are:

- users and roles
- areas and sub-areas
- activities or schedule activities
- BOQ/material list
- units

Scope of work and resource plan should be supported, but they do not need to block the first pilot.

### project_schedule_items

Stores schedule data imported from project templates.

Important fields:

- company_id
- project_id
- activity_id
- planned_start_date
- planned_end_date
- area_id
- sub_area_id
- planned_quantity
- unit_id

### project_scope_items

Stores scope of work items.

Important fields:

- company_id
- project_id
- scope_item
- description
- area_id
- sub_area_id

### boq_items

Stores BOQ data.

Important fields:

- company_id
- project_id
- item_code
- item_description
- planned_quantity
- unit_id
- material_name
- activity_id

### resource_plan_items

Stores planned manpower/resources.

Important fields:

- company_id
- project_id
- trade
- planned_count
- area_id
- sub_area_id
- planned_date

### activities

Stores construction activities.

Examples:

- plastering
- brickwork
- excavation
- concreting

### activity_synonyms

Stores alternate words in English, Hindi, and Hinglish.

Example:

- plaster
- plastering
- plaster ka kaam
- plaster complete hua

### units

Stores measurement units.

Examples:

- sqm
- sqft
- bags
- kg
- pieces

### progress_entries

Stores work completed.

Important fields:

- company_id
- project_id
- user_id
- activity_id
- quantity
- unit_id
- location_id
- work_date
- original_message
- input_type
- transcript_text
- status

### manpower_entries

Stores manpower data.

Important fields:

- company_id
- project_id
- user_id
- trade
- count
- location_id
- work_date
- original_message
- input_type
- transcript_text

### material_transactions

Stores material received and issued.

Important fields:

- company_id
- project_id
- user_id
- material_name
- transaction_type
- quantity
- unit_id
- supplier
- purpose
- location_id
- transaction_date
- original_message
- input_type
- transcript_text
- proof_required
- proof_status

### material_stock_balances

Stores the current material stock balance for each project.

Important fields:

- company_id
- project_id
- material_name
- unit_id
- quantity_received
- quantity_issued
- current_balance
- last_updated_at

This allows the dashboard to show material stock without manually calculating it every time.

### media_files

Stores image/document metadata.

Important fields:

- company_id
- project_id
- uploaded_by
- storage_url
- media_type
- caption
- linked_record_type
- linked_record_id
- uploaded_at

### whatsapp_messages

Stores original inbound and outbound WhatsApp messages.

Important fields:

- company_id
- user_id
- phone
- direction
- message_text
- provider_name
- provider_message_id
- raw_provider_payload_url
- received_at

### whatsapp_provider_accounts

Stores WhatsApp integration settings for each company or platform account.

Important fields:

- company_id
- provider_name
- provider_account_id
- webhook_url
- phone_number_id
- status
- created_at

Examples of provider_name:

- meta_cloud_api
- twilio
- other_meta_partner

The purpose is to avoid locking the product to one WhatsApp vendor.

### company_ai_settings

Stores how each company wants to use AI.

Important fields:

- company_id
- ai_key_mode
- provider_name
- encrypted_api_key_reference
- default_model
- transcription_model
- is_active
- created_at

AI key modes:

- platform_managed: company uses the SaaS owner's AI keys
- company_owned: company provides its own AI keys

The actual secret key should not be stored as plain text in the database.
It should be encrypted or stored in a dedicated secrets manager.

### voice_notes

Stores voice note metadata and transcription.

Important fields:

- company_id
- project_id
- user_id
- media_file_id
- transcript_text
- language_detected
- transcription_status
- created_at

### daily_summary_messages

Stores automatic daily WhatsApp summaries.

Important fields:

- company_id
- project_id
- recipient_user_id
- summary_date
- summary_text
- whatsapp_message_id
- provider_name
- delivery_status
- sent_at

The summary should include progress, manpower, materials, proof/image highlights, and entries that need review.

### daily_summary_settings

Stores when and how daily summaries should be sent.

Important fields:

- company_id
- project_id
- recipient_user_id
- summary_time_local
- timezone
- is_enabled
- created_at
- updated_at

Default:

- summary_time_local: 19:00
- timezone: project local timezone

The default daily summary time should be 7:00 PM local project time, but admins should be able to change it.

### ai_insights

Stores AI-generated insights for companies that have AI insight access.

Important fields:

- company_id
- project_id
- insight_type
- insight_text
- source_date_range
- created_at

AI insights should only be visible when the company has AI insight access enabled.

### audit_logs

Tracks important actions.

Important fields:

- company_id
- user_id
- action
- entity_type
- entity_id
- timestamp
