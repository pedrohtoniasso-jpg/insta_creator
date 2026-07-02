---
name: insta-creator-brief
description: Use when turning an idea into a reusable content brief for the shared Instagram workflow. Captures the angle, audience, constraints, and traceability before downstream generation.
version: 1.0.0
author: Pedro Toniazzo
license: MIT
metadata:
  hermes:
    tags: [instagram, brief, planning, traceability, social-media]
    related_skills: [insta-creator, insta-creator-cards, insta-creator-caption, insta-creator-approval-package]
---

# Insta Creator Brief Skill

## Overview

This skill turns an idea into a clean, reusable brief that downstream skills can rely on. The brief is the shared anchor for the content workflow: it captures the objective, audience, angle, constraints, and traceability without drifting into final copy.

## When to Use

- You have an idea and need the first structured step of the content package.
- You want a brief that cards and caption generation can safely reuse.
- You need to preserve traceability before creating final content assets.

Do not use this skill for:
- final caption drafting
- slide/card layout generation
- approval package assembly

## Brief structure

A strong brief should contain:
- idea source and post identifier
- core message in one sentence
- target audience
- desired action from the audience
- key constraints from the project spec
- visual direction notes
- risks, exclusions, and sensitive topics
- traceability references

## Output rules

- Keep the brief concise but complete.
- Use the project spec for brand-specific decisions.
- Do not write final polished social copy inside the brief.
- Preserve the same post identifier that will later appear in `cards.json`, `caption.md`, and `approval.md`.

## Common Pitfalls

1. **Overwriting the idea with copy.** The brief should guide the content, not replace it.
2. **Skipping constraints.** Downstream skills need explicit boundaries.
3. **Losing traceability.** The brief must point back to the originating idea and project spec.

## Verification Checklist

- [ ] The brief has a clear objective.
- [ ] The audience and desired action are explicit.
- [ ] Project-spec constraints are captured.
- [ ] Traceability fields are present.
- [ ] The brief stays separate from final copy.
