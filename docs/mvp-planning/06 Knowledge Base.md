# 06 Knowledge Base

## Purpose

The knowledge base helps the system understand construction language.

It should preserve learnings from the old prototype while supporting Hindi and Hinglish.

## MVP knowledge areas

### Project knowledgebase

Each project should have its own knowledgebase uploaded by the company or project team.

Mandatory for MVP:

- schedule
- BOQ
- user list with roles
- areas
- sub-areas
- units
- activity list or schedule activities

Supported but optional for the first pilot:

- scope of work
- resource plan

The system should provide sample templates for these uploads.

The assistant should use this project knowledgebase when validating WhatsApp entries.

### Activities

Examples:

- plastering
- brickwork
- excavation
- concreting
- waterproofing
- painting
- tiling

### Activity synonyms

Examples:

- plaster
- plastering
- plaster ka kaam
- plaster complete
- plaster hua

### Units

Examples:

- sqm
- sqft
- cum
- bags
- kg
- tons
- pieces
- meters

### Materials

Examples:

- cement
- sand
- steel
- bricks
- tiles
- aggregate
- paint

### Trades

Examples:

- mason
- helper
- electrician
- plumber
- carpenter
- painter

### Locations

Project-specific locations:

- tower
- floor
- block
- zone
- basement
- parking

## Knowledge graph approach

For MVP, use PostgreSQL tables to model graph-like relationships.

Example:

```text
Plastering
→ has synonyms
→ uses cement and sand
→ measured in sqm
→ usually happens after brickwork
→ belongs to BOQ item
→ planned in schedule
→ valid in specific project areas
```

This allows useful validation without adding a separate graph database immediately.

## Validation examples

If a user reports an area that does not exist in the project knowledgebase, the assistant should ask for clarification.

If a user reports a material not present in the BOQ, the assistant should warn or ask for confirmation.

If a user reports progress far outside the planned scope, the assistant should flag it for review.

If a user sends incomplete data, the assistant should ask only for the missing information.

## Assistant behavior

The assistant should:

- sound professional
- be concise
- avoid robotic command-driven language
- support Hindi/Hinglish naturally
- avoid offensive or inappropriate language
- respond professionally to obscene, offensive, or irrelevant messages
- guide the user back to useful site reporting

## Future graph database

Later, consider Neo4j or another graph database for:

- advanced construction reasoning
- activity dependencies
- risk detection
- AI recommendations
- cross-project benchmarking
