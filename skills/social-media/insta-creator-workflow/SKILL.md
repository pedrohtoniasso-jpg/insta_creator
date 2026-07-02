---
name: insta-creator
description: Use when turning a selected Instagram idea into a complete approval-ready package with hidden orchestration, stage validation, rendered card images, and final caption.
version: 1.1.0
author: Pedro Toniazzo
license: MIT
metadata:
  hermes:
    tags: [instagram, social-media, workflow, orchestrator, traceability, approval]
    related_skills: [insta-creator-brief, insta-creator-cards, insta-creator-caption, insta-creator-approval-package]
---

# Insta Creator Workflow Orchestrator

## Overview

This skill is the single execution entrypoint for the Insta Creator production pipeline. It coordinates brief, narrative, cards, caption, rendered images, audit, storage, and approval packaging while routing brand-specific decisions to the project spec.

The workflow runs end-to-end without asking the user for intermediate approvals. The only human approval point is the final payload: caption + rendered card images.
When delivering the approval payload in chat, send the rendered card images as native media attachments and present the caption in a copy-friendly code block so the user can paste it directly.
Do not replace that approval payload with slide-by-slide descriptions, card JSON, brief text, or audit notes unless the user explicitly asks to inspect internals.

## When to Use

- A user selected a theme from the discovery shortlist.
- A cron-fed idea is ready to become a post package.
- A post needs a complete bundle: `manifest.json`, `brief.md`, `cards.json`, `caption.md`, `approval.md`, and rendered assets.

Do not use this skill for:
- writing the brand spec itself
- discovery/shortlist generation
- public posting or growth actions

## Non-negotiable boundaries

- The user is not the orchestrator.
- Stage-specific skills are internal workers, not final user-visible outputs.
- Do not expose brief, narrative, card JSON, or audit drafts unless the user explicitly asks.
- Do not stop at a textual outline when the user asks for cards; cards means generated visual assets.
- Do not request approval until caption and rendered card images exist and have been audited.
- Do not schedule publication or create a publish cron before that specific post package is explicitly approved.

## Workflow

1. Read the selected project spec, selected visual template, shared content workflow contract, and the format-specific contract (`docs/carousel-workflow-contract.md` for carousels, `docs/story-workflow-contract.md` for Stories).
2. Normalize the selected idea and trace context.
2.1 If the user replied to a shortlist, normalize the reply into a selection handoff with `project_id`, `selection.shortlist_id`, `selection.selected_option` or `selection.theme`, and `selection.user_action`.
2.2 If the user reply is only `1`-`5` or `Opção N`, resolve it from `state/latest-shortlist/<project_id>.json` before generating content. Prefer `python -m insta_creator_bootstrap shortlist resolve --project-id <project_id> --reply "<reply>" --root <workspace> --prompt` when available.
3. Build the brief.
3.1 Validate the brief with a checklist.
4. Define the carousel narrative arc before card copy.
4.1 Validate the narrative with a checklist.
5. Generate cards JSON and caption from the brief/narrative.
5.1 Validate cards JSON and caption with a checklist.
6. Render card images from cards JSON, selected project spec, and selected visual template.
6.1 Validate rendered images against the project spec and visual template.
7. Run the final package audit.
8. Assemble the deterministic post folder.
9. Deliver only the final user-facing approval payload: caption + rendered card images.
10. Wait for explicit approval or revision before scheduling, publishing, or moving to the next planned post.

## Carousel narrative standard

When the output format is a carousel, use a continuous story arc rather than isolated slide copy. Also apply `docs/carousel-workflow-contract.md`: the deck must have a specific hook, carousel type, save/share reason, one primary CTA, and a justified slide arc.

Default sequence:
1. Cover / promise
2. Problem or stakes
3. Context, cause, or mechanism
4. Practical impact, example, or reframing
5. Saveable rule, checklist, or takeaway
6. Dedicated CTA slide: save, share, comment, or DM

Use more slides only when the topic needs room and every extra slide adds value. Prefer clarity and progression over density.

## Required outputs

The package must contain:
- `manifest.json`
- `brief.md`
- `cards.json`
- `caption.md`
- `approval.md`
- `assets/01.png`, `assets/02.png`, etc.

## Project visual baseline

Render visuals from the selected project spec, not from the shared workflow. The spec must define:
- color palette and background direction
- typography direction and size defaults
- logo / mark rules
- layout constraints
- visual anti-patterns
- approval payload expectations

If a project requires a fixed template, load that project’s visual template or rendering contract before generating assets. Do not invent layout elements such as counters, boxes, decorative labels, or random metadata unless the project spec/template explicitly requires them.

## Traceability rules

- Keep one post identifier across all artifacts.
- Preserve the originating idea in the manifest.
- Reference the source project spec path/version.
- Record stage validation status in `approval.md` or manifest notes.
- Keep revisions in the same folder instead of fragmenting the bundle.

## Common Pitfalls

1. **Exposing internal stages.** The user should not receive every step; only final approval.
2. **Skipping stage validation.** Checklist validation must happen after brief, narrative, cards/caption, visual assets, and final package.
3. **Treating cards as prose.** Cards must become rendered images before approval.
4. **Ignoring project visual rules.** Brand behavior belongs in the project spec and must be applied before image rendering.
5. **Assembling approval too early.** Approval only happens after artifacts and images exist and pass audit.
6. **Sending internals instead of the approval payload.** The approval message is cards + caption, not slide descriptions.
7. **Batching publication before approvals.** Each post must be approved before scheduling or publishing.

## Verification Checklist

- [ ] The workflow starts from a selected idea, not from raw discovery.
- [ ] The project spec was read and applied.
- [ ] Brief checklist passed.
- [ ] Narrative checklist passed.
- [ ] Cards JSON and caption checklist passed.
- [ ] Rendered card images exist in `assets/`.
- [ ] Visual audit passed against project spec.
- [ ] Final approval payload contains caption + images only.
- [ ] Post folder is deterministic and traceable.
- [ ] Publication/scheduling remains blocked until this package is explicitly approved.

## Reference material

- `docs/content-workflow-contract.md` — shared workflow order, validation stages, storage, and approval rules.
- `docs/insta-creator-system-spec.md` — system boundaries and orchestration behavior.
- `docs/project-integration.md` — normalized cron intake, selection gate, and trace context.
- selected project spec path — active project brand rules; e.g. `docs/projects/granaflow/project-spec.md`.
