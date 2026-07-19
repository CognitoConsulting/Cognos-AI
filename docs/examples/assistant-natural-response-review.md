# Assistant natural response review

This file captures the expected behavior for the current rule-based assistant foundation.

The assistant is still not a full LLM assistant. It should, however, sound professional and summarize common site updates without exposing technical field names.

## Expected examples

| User message | Expected interpretation | Expected assistant style |
| --- | --- | --- |
| `Aaj Tower A Floor 2 me 50 sqm plaster complete hua` | progress: plastering, 50 sqm, Tower A Floor 2 | `Got it. I read this as progress: plastering, 50 sqm at Tower A Floor 2.` |
| `Tower A slab casting 35 cum completed today` | progress: slab casting, 35 cum, Tower A | `Got it. I read this as progress: slab casting, 35 cum at Tower A.` |
| `RCC work 20 cum done at Block B` | progress: concreting, 20 cum, Block B | `Got it. I read this as progress: concreting, 20 cum at Block B.` |
| `Shuttering completed 200 sqft at Tower C Floor 1` | progress: shuttering, 200 sqft, Tower C Floor 1 | `Got it. I read this as progress: shuttering, 200 sqft at Tower C Floor 1.` |
| `Bar bending 500 kg completed at Tower A` | progress: bar bending, 500 kg, Tower A | `Got it. I read this as progress: bar bending, 500 kg at Tower A.` |
| `Blockwork 300 sqft done at Tower B` | progress: blockwork, 300 sqft, Tower B | `Got it. I read this as progress: blockwork, 300 sqft at Tower B.` |
| `Labour 15 and mason 6 at Tower A` | manpower: 15 labour, 6 mason, Tower A | `Got it. I read this as manpower: 15 labour, 6 mason at Tower A.` |
| `TMT 500 kg received at Tower A` | material received: 500 kg steel, Tower A | `Got it. I read this as material received: 500 kg of steel at Tower A.` |

## Missing information style

If a user sends:

```text
Tower A plaster done 50
```

The assistant should ask only for the missing detail:

```text
I understood this as a progress update. I still need the unit. Please reply with just the missing detail.
```

## Professional redirect style

If a user sends irrelevant or offensive content, the assistant should stay professional:

```text
I can help record site progress, manpower, material movement, and proofs. Please send the project update in simple work-related language.
```

## Still pending

- full LLM-based flexible parsing
- project knowledgebase validation in the assistant response
- richer Hindi responses
- multi-entry extraction from one WhatsApp message
- editing already-saved records
