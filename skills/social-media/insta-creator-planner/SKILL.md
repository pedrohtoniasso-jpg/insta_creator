---
name: insta-creator-planner
description: Use when planning monthly Instagram calendars, replacing recurring content crons, handling special dates or news hooks, or avoiding schedule conflicts across posts, stories, and highlights.
version: 1.0.0
author: Pedro Toniazzo
license: MIT
metadata:
  hermes:
    tags: [instagram, planner, calendar, approval, monthly]
    related_skills: [insta-creator, insta-creator-approval-package, insta-creator-stories]
---

# Insta Creator Planner

## Overview

A monthly editorial planner for Instagram. It turns intake into a calendar, a production queue candidate, and highlight-ready story plans. The planner stays generic; project-specific behavior belongs in a project branch file.

## When to Use

- The user wants a monthly content plan before production
- Existing content crons should be replaced or paused
- Posts, stories, and highlights need a coordinated schedule
- Some dates are uncertain and should only be used if they become relevant
- You need to avoid collisions with already scheduled posts

## Core Flow

1. Read the active project spec and the project branch file, if one exists.
2. Inspect already scheduled content and mark hard conflicts.
3. Build content pillars and target outcomes for the month.
4. Place fixed posts first, then stories, then optional opportunity slots.
5. Treat uncertain dates as watch slots:
   - if a relevant event/news hook exists, convert the slot into content
   - if nothing is relevant, skip the slot with no replacement
6. Map evergreen story sequences to future Highlights.
7. Deliver the monthly plan for approval before any per-piece production.
8. After the plan is approved, hand off only one item at a time to `insta-creator`.

## Human delivery format

When presenting the monthly plan in chat, use this exact itemized shape and do not use Markdown tables:

```text
02/07
- Tema: xxxx
- Tipo: xxxx
- Desenvolvimento: xxxx
```

Rules:

- One date block per item.
- `Tipo` should be human-readable, e.g. `Post carrossel`, `Story evergreen`, `Story temporário`, or `Watch slot`.
- `Desenvolvimento` should summarize the angle briefly.
- Do not dump internal artifacts or production notes here.
- Do not send the monthly plan as a Markdown table.

## Approval rules

- Monthly-plan approval is not post approval.
- After the plan is approved, generate only the first approved post/story package.
- Deliver only the final approval payload for that package: caption + rendered card images.
- Wait for explicit approval or revision.
- Only then move to the next planned item.
- Do not create publication crons before the specific package is approved.

## Planning Rules

- Use a small number of strong pillars instead of random variety
- Keep at least one conversion path per month
- Spread posts so the profile feels active without flooding the feed
- Reserve room for dates that only matter if something relevant happens
- Never force a post just because a calendar cell exists
- Stories intended for Highlights must be labeled evergreen and grouped by destination

## Watch Slot Rule

Use watch slots for events that are unpredictable or only worth covering if they matter to the audience.

Examples:
- policy or product changes
- market or platform updates
- news that changes user behavior
- brand-relevant moments that may or may not happen

If no useful signal appears, leave the slot empty and move on.

## Output Artifacts

- `editorial-plan.md`
- `calendar.json`
- `special-dates.json`
- `highlights-plan.md`
- `production-queue.json`

## Common Mistakes

1. Turning the planner into a generator too early
2. Forcing content into every date
3. Ignoring already scheduled posts
4. Mixing project-specific rules into the generic skill
5. Forgetting that Highlights need evergreen story sequences
6. Treating plan approval as permission to generate or schedule many posts at once
7. Sending the monthly plan as a table instead of the required itemized format

## Verification Checklist

- [ ] The month has a coherent content mix
- [ ] Scheduled posts were checked before planning
- [ ] Watch slots are optional and may be skipped
- [ ] Stories intended for Highlights are marked evergreen
- [ ] The plan is ready for approval before production
- [ ] The human-facing monthly plan uses the required itemized format
- [ ] Post production remains sequential after plan approval
