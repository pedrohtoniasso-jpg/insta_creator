# Content Workflow Contract

This document defines the reusable shared workflow that turns an idea into an approval-ready Instagram content package.

For Instagram carousels, also follow `docs/carousel-workflow-contract.md`. Carousel requests must be engineered as swipeable value assets with a specific hook, justified slide arc, and a save/share/comment/DM objective.

For Instagram Stories, also follow `docs/story-workflow-contract.md`. Story requests must produce a single 9:16 interaction unit by default, not a carousel or a sequence of posts.

## Execution boundary
- The workflow starts only after a user selects a theme from discovery intake.
- The orchestrator is responsible for all production steps.
- The user is not the orchestrator: do not ask for intermediate approval during production.
- The only user approval point is the final package, after caption and rendered card images exist.
- The approval payload must be the final caption plus rendered card images only, unless the user explicitly asks to inspect internals.
- A plan approval does not authorize scheduling or publication; post-level approval is still required.

## Workflow order
1. Load the selected project spec, selected visual template, and trace context.
2. Build the brief from the selected idea and project spec.
2.1 Validate the brief with a checklist before moving on.
3. Shape the format-specific narrative arc before drafting cards/story frames.
3.1 Validate the narrative with a checklist before moving on.
4. Generate cards JSON and caption content from the approved internal brief/narrative.
4.1 Validate cards JSON and caption with a checklist before moving on.
5. Render card images from `cards.json`, selected project spec, and selected visual template.
5.1 Validate rendered images against the project spec and visual template before moving on.
6. Run the final package audit.
7. Assemble the approval package.
8. Store everything in a deterministic per-post folder.
9. Send the user-facing approval payload as:
   - rendered card images as native media attachments
   - caption in a copy-friendly block the user can paste directly
   - carousel shorthand: caption + rendered card images
10. Wait for explicit approval or revision.
11. Only after explicit approval may the post move to scheduling or publication.

## Format selection rule

The selected idea must carry or resolve to an output format before production:
- `carousel`: use the carousel engagement contract in `docs/carousel-workflow-contract.md` and the carousel narrative standard below.
- `story`: use the Story micro-arc in `docs/story-workflow-contract.md`.

If a carousel idea arrives as a broad topic, sharpen it into a specific promise before production. The production brief must identify the carousel type, hook, save/share reason, primary CTA, and slide arc.

If a Story idea arrives as a sequence of posts, compress it into one interactive Story unit instead of producing multiple frames. Use one hook, one sticker prompt, one CTA, and one 9:16 visual direction.

## Carousel narrative standard
For carousel posts, prefer a consistent story arc:
1. Open with the theme or problem.
2. Show the problem with supporting data or evidence.
3. Explain the context, cause, or mechanism.
4. Connect the issue to the audience’s real decision.
5. Offer the organizing principle, rule, or takeaway.
6. End with a dedicated CTA slide that drives the objective.

The default pattern should feel like a single continuous story, not isolated slide-by-slide facts.
For news, regulatory, or product-update topics, the opening slide must name the actor, the decision/change, and the immediate consequence; avoid vague hooks when a concrete headline exists.
The deck must also satisfy the engagement standard: the cover earns the swipe, the middle slides build value, and the final CTA asks for one relevant action — save, share, comment, or DM.

## Deterministic folder layout
Each post lives in its own folder under the project-configured storage root, with a local default of `content/posts/`.

Expected files:
- `manifest.json`
- `brief.md`
- `cards.json`
- `caption.md`
- `approval.md`
- `assets/01.png`, `assets/02.png`, ...

Recommended naming pattern:
- `YYYY.MM.DD - Short subject`

## Shared typography defaults
For card generation, use these as the starting point unless the project spec overrides them:
- Card title size: 86–104 px on 1080×1350, extrabold/black.
- Card subtitle/body size: 34–48 px on 1080×1350, regular/medium.
- Sizes may be adjusted during review or audit; legibility wins over fixed values.

## Stage checklist structure
Each validation step must be question-driven, not a single pass/fail label.

### Brief checklist
- Does the brief name the selected idea and source?
- Does it define audience, objective, core message, risk, CTA, and visual direction?
- Does it cite the project spec as the visual/voice source of truth?
- For carousels, does it name the carousel type, hook, save/share reason, primary CTA, and slide arc?

### Narrative checklist
- Does the story move from hook → evidence/context → practical impact → takeaway → CTA?
- Does each slide add one new step instead of repeating the premise?
- Does the CTA feel like the natural ending of the same argument?
- If the output format is `carousel`, does the first slide earn a swipe and does every slide justify its place?
- If the output format is `story`, did we use the story micro-arc instead of carousel logic?

### Cards/caption checklist
- Does `cards.json` parse and match the schema?
- Are slide numbers sequential and equal to `slide_count`?
- Are headline/body strings short enough for mobile?
- For every card, do wrapped lines avoid orphan/single-word breaks?
- Does the caption support the same story and keep hashtags at the end?
- For carousels, is there one primary engagement CTA matched to the topic objective?
- For Stories, is there exactly one primary interaction and a native sticker directive instead of a feed caption?

### Visual assets checklist
- Are all rendered images present in `assets/` with stable filenames?
- Do the visuals match the project spec identity?
- Do the visuals apply the selected project spec exactly, including its color palette, typography, logo/mark rules, layout constraints, and explicit anti-patterns?
- Is the text legible on mobile and free of cutoffs?

### Final package checklist
- Does the bundle contain all required files?
- Does `approval.md` summarize the checks and final decision state?
- Is the user-facing approval payload only caption + images, not internal drafts?
- Did any rejection/change request become a new checklist question or project-spec rule?
- Is publication/scheduling still blocked until this specific package is approved?

## Shared artifact roles

### `manifest.json`
The manifest is the traceability anchor. It should record:
- a stable post identifier
- the idea source
- the project spec path or version identifier
- the selected content angle
- artifact filenames, including rendered images
- validation status by stage
- approval status

### `brief.md`
The brief captures the problem, audience, angle, content objective, risks, CTA direction, visual direction, and traceability.

### `cards.json`
Cards are structured JSON. They must be deterministic, ordered, easy to validate, and shaped like a single narrative rather than disconnected mini-posts.

### Card images / visual assets
When the workflow says “cards”, the reviewer expects generated card images or image-ready assets, not a textual outline of slide contents. The visual assets must be produced and audited before approval.

### `caption.md`
The caption should keep a predictable structure that supports the same narrative arc as the cards: hook, body, CTA, hashtags. For approval delivery, format the caption as copy-ready text and include emojis when they improve readability or emphasis. Limit hashtags to at most 5.

### `approval.md`
The approval package summarizes the chosen direction, stage validations, visual audit, and final visible payload.

It is an internal bundle artifact. When sending the user-facing approval message, do not paste `approval.md`, `brief.md`, `cards.json`, or slide-by-slide textual outlines unless the user explicitly asks for them.

## Traceability rules
- Every artifact must reference the same post identifier.
- The brief, cards, caption, images, and approval package must all point back to the originating idea.
- Revisions should preserve the same folder and increment traceability metadata rather than scattering files.

## Validation rules
- Cards JSON must be syntactically valid and schema-compatible.
- Rendered images must exist before final approval.
- The content package must contain all required files before approval.
- The shared workflow remains generic; project-specific branding belongs in the project spec.
- Publication scheduling must happen only after explicit approval of that post package.
