---
name: insta-creator-stories
description: Use when turning a brief into structured Instagram Story frames for the shared workflow. Validates frame order, 9:16 composition, and concise copy.
version: 1.0.0
author: Pedro Toniazzo
license: MIT
metadata:
  hermes:
    tags: [instagram, stories, frames, json, validation, vertical]
    related_skills: [insta-creator-workflow-orchestrator, insta-creator-brief, insta-creator-cards, insta-creator-caption, insta-creator-approval-package]
---

# Insta Creator Stories Skill

## Overview

This skill turns a brief into structured Instagram Story frames for the shared workflow. Story output should stay machine-checkable and deterministic, while making the 9:16 format explicit so downstream packaging and review stay aligned.

## When to Use

- The brief calls for Instagram Stories instead of a feed carousel.
- You need a frame-by-frame sequence optimized for vertical viewing.
- You want story copy that stays concise but still follows a clear arc.

Do not use this skill for:
- long-form feed posts
- caption-only content
- approval packaging
- project-specific brand spec creation

## Story contract

Recommended package shape:
- `version`
- `post_id`
- `subject`
- `format: story`
- `slide_count`
- `cards[]`
- `traceability`

Each story frame should include:
- `slide`
- `role`
- `headline`
- `body`
- `visual_note`
- optional `cta_note`
- optional `source_notes[]`

Storytelling guidance:
- Use 9:16 full-screen frames.
- Keep each frame focused on one idea.
- Make the sequence easy to tap through.
- Open with the core topic early when clarity matters.
- End with a simple, low-friction CTA or next step.

## Output rules

- Keep the sequence short unless the idea genuinely needs more room.
- Use concise copy that reads fast on mobile.
- Preserve the same post identifier used by the rest of the content package.
- Keep traceability references aligned with the brief and project spec.
- Represent the sequence as structured JSON, not prose.

## Common Pitfalls

1. **Writing a carousel and calling it a story.** Stories need vertical framing and tighter copy.
2. **Overcrowding frames.** One frame should carry one main thought.
3. **Dropping traceability.** The story frames still need the same post identifier and source references.
4. **Forgetting the CTA.** A story sequence still needs a clear end state.

## Verification Checklist

- [ ] The output is structured JSON.
- [ ] `format` is explicitly set to `story` when used.
- [ ] Frames are sequential and concise.
- [ ] The sequence is designed for 9:16 viewing.
- [ ] Traceability metadata is present.
- [ ] The frame arc is clear from opening to CTA.

## Reference material

- `skills/social-media/insta-creator-cards/references/storytelling-patterns.md` — generic narrative pattern and continuity guidance that also helps story sequences.
