# 08 WhatsApp Message Examples

## Progress examples

```text
Completed 50 sqm plastering in Tower A Floor 3
```

```text
Aaj Tower A floor 2 me 50 sqm plaster complete hua
```

```text
Brickwork 200 sqft done at Block B
```

```text
Basement waterproofing completed 100 sqm
```

## Manpower examples

```text
10 masons and 5 helpers present at Tower A
```

```text
Aaj site pe 12 mazdoor aaye
```

```text
Tower B me 4 electrician, 3 plumber available
```

```text
8 labour basement area me kaam kar rahe hain
```

## Material received examples

```text
100 cement bags received from ABC supplier
```

```text
Aaj 2 ton steel site par receive hua
```

```text
500 bricks received for PQR Villa
```

## Material issued examples

```text
20 cement bags issued for plastering Tower A
```

```text
Tower B ke liye 100 tiles issue kiye
```

```text
5 steel rods issued for slab work
```

## Image examples

Image with caption:

```text
Tower A Floor 3 plastering completed
```

Image with material proof caption:

```text
100 cement bags received
```

## Bot commands

The MVP should not require users to remember special commands.

The assistant should understand normal messages like:

```text
I want to update today's progress.
```

```text
Aaj ka manpower update karna hai.
```

```text
Material received entry add karo.
```

Special commands can exist internally or as fallback help shortcuts, but they should not be the primary user experience.

## Voice examples

Voice note transcript:

```text
Aaj Tower A second floor par 50 square meter plaster complete hua.
```

Voice note transcript:

```text
Site par 10 mason aur 5 helper aaye hain.
```

Voice note transcript:

```text
100 cement bags receive hue, photo bhej raha hoon.
```

## Unclear message examples

```text
Plaster complete hua.
```

Assistant should ask:

```text
Which project/location and how much plastering was completed?
```

## Confirmation example

User:

```text
Aaj Tower A Floor 2 me 50 sqm plaster complete hua.
```

Assistant:

```text
Please confirm this entry:

Project: Tower A project
Location: Tower A, Floor 2
Activity: Plastering
Quantity: 50 sqm
Date: Today

Reply Yes to save, or tell me what to change.
```

## Daily WhatsApp summary example

```text
Daily Site Summary - 16 July

Project: Green Residency

Progress:
- Tower A Floor 2 plastering: 50 sqm completed
- Block B brickwork: 200 sqft completed

Manpower:
- Masons: 10
- Helpers: 5

Materials:
- Cement received: 100 bags
- Cement issued: 20 bags
- Current cement stock: 80 bags

Needs review:
- 1 entry has unmatched location and needs checking
```

## Offensive or irrelevant message handling

If a user sends obscene, offensive, or irrelevant content, the assistant should respond professionally and redirect the user.

Example response:

```text
I can help with project updates such as progress, manpower, materials, and site images. Please share the site update you want to record.
```

## Parser requirements

The parser should identify:

- intent
- activity
- material
- manpower trade
- quantity
- unit
- location
- project
- date
- proof image relationship
- missing required information
- confirmation summary
- stock update
- daily summary content
- offensive or irrelevant content
