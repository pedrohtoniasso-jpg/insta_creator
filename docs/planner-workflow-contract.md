# Instagram Monthly Planner Workflow Contract

This document defines the reusable monthly planner that turns a content strategy into a calendar, an evergreen story map, and a production queue.

The planner is **generic**. Project-specific content pillars, highlight targets, and watch-slot preferences belong in a project branch file such as `docs/projects/<project>/content-planner.md`.

## Planner responsibilities

1. Inspect already scheduled content before placing anything new.
2. Build a monthly plan that balances posts, stories, highlights, and special-date slots.
3. Treat uncertain dates as **watch slots**: only use them if there is a genuinely relevant signal.
4. Keep story sequences that should become Highlights clearly marked as evergreen.
5. Keep history awareness so the month does not repeat the same theme too quickly.
6. Output a plan for approval before any production queue is created.
7. Convert the approved plan into a production queue only after approval.

## Core outputs

The monthly planner should be able to emit these artifacts:

- `editorial-plan.md` — human-readable summary of the month
- `calendar.json` — machine-readable calendar with dates and statuses
- `highlights-plan.md` — story-to-highlight mapping
- `production-queue.json` — approved items only
- `special-dates.json` — event watch slots and skip decisions

## Planner JSON shape

A planner output should contain at minimum:

- `version`
- `project_id`
- `project_name`
- `project_spec_path`
- `month` in `YYYY-MM`
- `timezone`
- `summary`
- `history_summary`
- `posts`
- `stories`
- `highlights`
- `watch_slots`
- `skipped_watch_slots`
- `items`
- `created_at`

### Item shape

Each planned item should include:

- `item_id`
- `date`
- `format` (`carousel` or `story`)
- `category` (`post`, `story`, `highlight`, `watch`)
- `pillar`
- `theme`
- `objective`
- `cta`
- `evergreen`
- `highlight_target`
- `approval_state`
- `source_kind`
- `status`
- `notes`

## Story → Highlight rule

Stories that are intended to become Highlights must be marked evergreen at planning time.

Suggested rules:

- `evergreen: true` means the story sequence can be reused in a Highlight.
- `highlight_target` names the destination Highlight.
- One evergreen story sequence can support one highlight destination, or a small group if the project asks for that.
- Temporary engagement stories do **not** need highlight targets.
- If a story does not belong in a Highlight, leave `highlight_target` empty.

## Watch-slot rule

Use watch slots for uncertain or external events that may matter, but only if they become relevant.

Examples:

- policy or platform changes
- banking/payment changes
- tax, salary, or consumer-cycle moments
- news that clearly affects the audience’s behavior

If the month brings no strong signal, skip the slot and record the reason.

## History-awareness rule

The planner should look at recent output and avoid repeating the same theme too soon.

Minimum expectations:

- count recent themes and pillars
- prefer fresher topics when multiple options exist
- if repetition is unavoidable, record a note explaining why
- use recent history to balance the month instead of relying on memory alone

## Human delivery format

When the planner presents the monthly plan in chat for approval, it must use an itemized block format and must not use Markdown tables.

Required presentation pattern:

```text
02/07
- Tema: xxxx
- Tipo: xxxx
- Desenvolvimento: xxxx
```

Rules:

- One date block per planned item.
- `Tipo` should name the visible content type, such as `Post carrossel`, `Story evergreen`, `Story temporário`, or `Watch slot`.
- `Desenvolvimento` should explain the angle or execution briefly, not dump internal production notes.
- Do not present the monthly approval plan as a Markdown table.
- The planner approval message is a monthly overview, not the final per-post approval payload.

## Approval-to-queue rule

The planner output is not yet a production queue.

To convert a plan into a queue:

1. Receive approval for specific item IDs or the whole plan.
2. Keep only the approved items.
3. Mark those items as queued for production.
4. Preserve traceability back to the original plan item IDs.

Monthly-plan approval does **not** approve individual post packages or publication.

After the plan is approved:

1. Generate only the first approved item.
2. Deliver only that item's final approval payload as `caption + rendered card images`.
3. Wait for explicit human approval or revision.
4. Only then continue to the next approved item.
5. Do not create a publication cron or publish a post before that specific post package is approved.

## Validation checklist

- [ ] Already scheduled content was checked first
- [ ] The month has a balanced mix of posts, stories, and evergreen story sequences
- [ ] Uncertain dates are optional watch slots
- [ ] Skipped watch slots keep a reason
- [ ] Stories destined for Highlights are marked evergreen
- [ ] Recent history influenced topic selection
- [ ] Approved items can be converted into a queue without losing traceability
- [ ] The human-facing monthly plan uses the required itemized format, not a table
- [ ] Per-post production remains sequential after plan approval
