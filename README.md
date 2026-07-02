# Insta Creator System

A reusable Instagram content creation system for autonomous agents.

It combines:
- a shared bootstrap package for new environments
- a reusable monthly planner with explicit approval gates
- reusable content workflow skills for briefs, cards, captions, audits, and approval packages
- project-specific spec loading and idea intake
- approval-gated growth workflows
- deterministic validation checks

## What this repository provides

- `insta_creator_bootstrap`: a local Python package that can plan, apply, and validate a shared scaffold
- a planner/queue flow for monthly calendars with per-post approval gates
- a reusable skill suite for turning selected ideas into complete content packages
- project documentation and contracts for storage, project specs, workflow boundaries, and audit checks
- verification artifacts for deterministic reuse

## Quick start

### 1) Set up a project scaffold

Install locally in editable mode first:

```bash
python -m pip install -e .
```

```bash
python -m insta_creator_bootstrap --help
python -m insta_creator_bootstrap plan --target <dir>
python -m insta_creator_bootstrap apply --target <dir>
python -m insta_creator_bootstrap validate --target <dir>
```

### 1.5) Plan a month of content

```bash
python -m insta_creator_bootstrap plan-month --project-spec <path> --month YYYY-MM --planner-profile <path>
python -m insta_creator_bootstrap queue-from-plan --plan-json <plan.json> --approved-ids-json <ids.json>
```

Approval semantics:
- `plan-month` produces a calendar for human approval.
- `queue-from-plan` only selects items for production; it does **not** approve publication.
- After the plan is approved, produce and approve one post at a time.

### 2) Fill the project spec

Use the project spec template created by the bootstrap and make sure the required sections are present:
- project name
- target platform
- brand personality
- brand voice
- visual rules
- color palette
- typography direction
- logo / mark rules
- CTA conventions
- approval behavior
- prohibited angles
- asset constraints
- operational notes

### 3) Prepare project context

Before running a new agent or workflow, make sure these inputs exist and are current:

- the active `project-spec.md`
- any brand visual template used by the renderer
- the shortlist or approved plan item that should drive production
- any external context source your team uses for project memory or business background

### 4) Run the shared content workflow

The shared workflow is split into specialized skills for:
- brief generation
- carousel narrative planning
- carousel cards in validated JSON
- caption generation
- visual asset rendering / audit
- approval package assembly

Useful references:
- `docs/visual-template-contract.md`
- `docs/project-spec.md`
- `docs/content-workflow-contract.md`
- `docs/carousel-workflow-contract.md`
- `docs/story-workflow-contract.md`
- `docs/planner-workflow-contract.md`
- `docs/insta-creator-system-spec.md`
- `docs/project-integration.md`
- `schemas/cards.schema.json`
- `skills/social-media/insta-creator-workflow/SKILL.md`
- `skills/social-media/insta-creator-brief/SKILL.md`
- `skills/social-media/insta-creator-cards/SKILL.md`
- `skills/social-media/insta-creator-caption/SKILL.md`
- `skills/social-media/insta-creator-approval-package/SKILL.md`

## Recommended content flow

**Single entrypoint:** always start production with `skills/social-media/insta-creator-workflow/SKILL.md` (`insta-creator`).

1. Discovery cron returns exactly 5 numbered ideas and persists them to `state/latest-shortlist/<project_id>.json`.
2. User selects one idea by number or explicit theme.
3. If the reply is only `1`-`5` or a terse option reference, resolve it from the persisted latest-shortlist state before production.
4. Cron discovery uses 5 numbered ideas; user reply is normalized into a selection handoff.
5. Orchestrator reads the selected project spec, selected visual template, and trace context.
6. Build the brief.
7. Validate the brief with checklist.
8. Shape the carousel narrative before drafting cards.
9. Validate the narrative with checklist.
10. Generate cards JSON and caption.
11. Validate cards/caption with checklist.
12. Render card images.
13. Validate rendered images against the project spec.
14. Run final package audit.
15. Assemble deterministic bundle.
16. Send the approval payload: caption + rendered card images.
17. Wait for explicit approval before scheduling/publication or before generating the next post from the monthly plan.

The user should not receive internal stages unless they explicitly ask for them.

## Audit workflow

The audit pass is stage-based and question-driven.

Required stages:
- brief audit
- narrative audit
- cards/caption audit
- visual assets audit
- packaging / delivery audit
- revision loop audit

Rule of thumb:
- every error, objection, or change request should become a new checklist question for the next run
- repeated mistakes should be promoted into the project baseline so future posts start with them already covered

## Cron presets

Use cron to automate discovery and follow-up queues. Production should begin only after a selection signal.

Detailed prompt templates live in `docs/cron-templates.md`.

Suggested schedules:

- **Content ideas / trend intake**
  - schedule: `0 8 * * *`
  - purpose: collect recent signals and return exactly 5 candidate topics
  - for Carousels: return exactly 5 swipeable value assets with `output_format: carousel`, `carousel_type`, hook, save/share reason, primary CTA, and compact slide arc; do not return only broad topics
  - for Stories: return exactly 5 single Story units with `output_format: story`, `story_type`, hook, native sticker prompt/options, CTA, and visual direction; do not return sequences of posts

- **Content production**
  - trigger: selected idea / explicit theme
  - purpose: generate the brief, narrative, cards JSON, caption, rendered images, audit, and approval payload
  - rule: do one post at a time; wait for approval before generating the next planned post

- **Publication**
  - trigger: explicit approval of one specific post package
  - purpose: publish only the already approved package
  - rule: never create this schedule before that post is approved

- **Growth actions**
  - schedule: `*/30 * * * *`
  - purpose: queue low-sensitivity actions automatically and batch reply drafts for approval

- **Review / follow-up queue**
  - schedule: `0 17 * * 1-5`
  - purpose: review pending approval items, revise outputs, and prepare the next content cycle

Notes:
- keep growth actions approval-gated when they involve public replies or sensitive engagement
- keep project-specific cron logic outside the shared bootstrap
- when the discovery cron is used, make it return exactly 5 numbered ideas so the user can answer only with `1`-`5`
- after generating the shortlist, persist it with `python -m insta_creator_bootstrap shortlist save --project-id <project_id> --job-id <job_id> --shortlist-json '<json-array>' --project-spec <path> --visual-template <path>` so a later one-digit reply can be resolved without the user naming the cron
- normalize the reply into a selection handoff containing `project_id`, `selection.shortlist_id`, `selection.selected_option` or `selection.theme`, and `selection.user_action`
- use the project spec to decide which actions are automatic and which need review

## Verification

- `python -m unittest discover -s tests -v`

## Routine for a new agent

1. Install the package and validate the scaffold.
2. Load the active project spec before content generation.
3. If a monthly plan exists, choose exactly one approved item for production.
4. Use the orchestrator as the content-production entrypoint.
5. Deliver only the approval payload to the human reviewer.
6. Wait for explicit approval before publication or before moving to the next planned item.

## Notes

Keep the shared workflow generic, and keep brand or project-specific rules in the project spec.
