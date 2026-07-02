---
name: insta-creator-approval-package
description: Use when assembling the final Instagram review bundle after brief, cards, caption, visual assets, and audits already exist.
version: 1.1.0
author: Pedro Toniazzo
license: MIT
metadata:
  hermes:
    tags: [instagram, approval, review-bundle, packaging, audit]
    related_skills: [insta-creator, insta-creator-brief, insta-creator-cards, insta-creator-caption]
---

# Insta Creator Approval Package Skill

## Overview

This skill assembles the final review bundle for a post. It is a packaging step, not a generator. The goal is to keep internal artifacts traceable while sending the user only what they need to approve.

## When to Use

- Brief, cards JSON, caption, rendered images, and stage validations already exist.
- You need a single deterministic post folder.
- You need to prepare the final user-facing approval payload.

Do not use this skill for:
- generating content from scratch
- replacing the workflow orchestrator
- asking for intermediate approvals
- creating project-specific brand rules
- cron intake or growth queueing

## Approval package contents

The internal bundle should include:
- `manifest.json`
- `brief.md`
- `cards.json`
- `caption.md`
- `approval.md`
- `assets/01.png`, `assets/02.png`, etc.
- reply drafts when relevant to review

The user-facing approval output should include only:
- the final caption, preferably between backticks when delivered in chat
- the rendered card images already created for the post

Do not replace this with slide-by-slide prose, brief excerpts, JSON dumps, or audit checklists unless the user explicitly asks for them.

Internal JSON, brief, traceability, and audit logs stay in the bundle unless the user asks to inspect them.

## Approval rules

- Keep the package self-contained.
- Preserve the same post identifier in every artifact.
- Include a concise summary of the chosen content direction.
- Record stage checklist results in `approval.md`.
- Keep the reviewer’s decision path obvious.
- Keep any reply drafts in the bundle rather than as loose files.
- Do not present textual card outlines as “cards”; rendered images are required.
- Do not create a publication schedule from this package until the user explicitly approves it.

## Common Pitfalls

1. **Forgetting the manifest.** The manifest is the traceability anchor.
2. **Splitting the bundle.** The package should stay in one post folder.
3. **Dumping internal artifacts to the user.** The approval chat should show caption + images, not every internal file.
4. **Leaving out rendered images.** Without images, the package is not approval-ready.
5. **Skipping rejection learnings.** Rejections should become checklist/spec updates.

## Verification Checklist

- [ ] The bundle contains all required artifacts.
- [ ] The manifest matches the post folder and idea source.
- [ ] Rendered images exist with stable filenames.
- [ ] Stage validation results are recorded.
- [ ] The visible approval payload is caption + images.
- [ ] Reply drafts are included when relevant.
- [ ] The deterministic folder layout is respected.
- [ ] Publication remains blocked until explicit approval.
