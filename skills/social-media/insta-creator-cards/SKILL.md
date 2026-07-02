---
name: insta-creator-cards
description: Use when turning a brief into structured carousel cards JSON for the shared Instagram workflow. Validates slide order, card roles, and copy structure.
version: 1.0.0
author: Pedro Toniazzo
license: MIT
metadata:
  hermes:
    tags: [instagram, cards, json, validation, carousel]
    related_skills: [insta-creator, insta-creator-brief, insta-creator-caption, insta-creator-approval-package]
---

# Insta Creator Cards Skill

## Overview

This skill turns a brief into structured cards JSON for carousel-style content. Cards must remain machine-checkable and deterministic so later phases can validate the content package without guessing.

## When to Use

- The brief is ready and you need slide-by-slide content.
- You want structured JSON rather than free-form slide prose.
- You need a validated set of cards that can be stored in the post bundle.

Do not use this skill for:
- caption writing
- approval packaging
- brand-spec creation

## Cards contract

Recommended top-level shape:
- `version`
- `post_id`
- `subject`
- `slide_count`
- `cards[]`
- `traceability`

Each card should include:
- `slide`
- `role`
- `headline`
- `body`
- `visual_note`
- optional `cta_note`
- optional `source_notes[]`

Storytelling guidance:
- The cards must read as one continuous narrative.
- The opening card should make the topic obvious when that improves clarity.
- The middle cards should add reasoning or progression, not just repeat the premise.
- Prefer more simple cards over fewer crowded cards when the topic needs room to breathe.
- Keep the text on each card short enough to stay legible in mobile-first layouts.
- The CTA card should feel like the natural end of the same argument.

## Validation rules

- Slides must be ordered sequentially.
- `slide_count` must match the number of cards.
- Every card must carry the same post identifier as the rest of the package.
- Copy should stay concise enough for the slide role.
- The JSON must remain schema-compatible with `schemas/cards.schema.json`.

## Common Pitfalls

1. **Writing prose instead of JSON.** The output needs to be parseable.
2. **Letting slide order drift.** Slide numbers must be stable and sequential.
3. **Dropping traceability.** The cards must still point back to the idea and brief.

## Verification Checklist

- [ ] JSON parses cleanly.
- [ ] Slide numbers are sequential.
- [ ] `slide_count` matches the card array length.
- [ ] Required fields are present.
- [ ] Traceability metadata is included.
- [ ] The output matches the shared cards schema.

## Reference material
- `references/storytelling-patterns.md` — generic carousel flow, hook structure, continuity rules, and visual guidance.
