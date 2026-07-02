# Brand Spec Template

This document is a generic template for project-specific Instagram brand specs.
Fill it with the active project’s real rules before running content production.

## Project name

## Target platform
- Instagram feed carousels, default 4:5 portrait unless overridden.

## Brand personality
- Mood:
- Character:
- Emotional range:
- Brand posture:

## Brand voice
- Tone:
- Form of address:
- Vocabulary preferences:
- Level of directness:
- Rhythm / sentence length:

## Visual rules
- Visual identity:
- Background style:
- Layout preferences:
- Slide density:
- Carousel storytelling style:
  - hook / problem / data or context / impact / principle or rule / dedicated CTA
- Explicit visual anti-patterns:

## Color palette
- Background primary:
- Background secondary:
- Accent primary:
- Accent secondary:
- Text primary:
- Text muted:

## Typography direction
- Preferred family:
- Secondary/fallback:
- Visual feeling:
- Headline weight:
- Subtitle/body weight:
- Starting card title size defaults:
- Starting card subtitle size defaults:

## Logo / mark rules
- Mark type:
- Placement:
- Size:
- When to use wordmark:
- When not to use wordmark:

## CTA conventions
- Primary CTA:
- Secondary CTA:
- Link/profile reference style:
- Hashtag conventions:
- Beta/trial prompt, if relevant:

## Growth strategy
- Follow/unfollow policy:
- Comment like policy:
- Reply strategy:
- Approval rules for engagement actions:
- Rate limits or safety constraints:
- Timing/spread rules for automated actions:

## Idea selection gate
- Discovery cron returns exactly 5 numbered options.
- The user can continue by replying only with `1`-`5`.
- Each option should include theme, angle, why it matters now, and recommended format.
- Do not generate the final post until a numbered choice or explicit theme is confirmed.

## Approval behavior
- Approval channel: main channel
- User approves only at the final package stage.
- Monthly-plan approval does not approve individual post packages or publication.
- After the plan is approved, produce and approve one post/story package at a time.
- Visible approval payload:
  - final caption
  - rendered card images already created for the post
- Internal artifacts stay in the bundle unless requested:
  - `manifest.json`
  - `brief.md`
  - `cards.json`
  - `caption.md`
  - `approval.md`
  - `assets/`
- Stage checklists required:
  - brief
  - narrative
  - cards/caption
  - visual assets
  - final package
- Repeated errors become new checklist questions and project-spec rules.

## Prohibited angles
- Unsafe claims:
- Off-brand messaging:
- Forbidden comparisons:
- Legal or compliance constraints:

## Asset constraints
- Required asset formats:
- Recommended dimensions:
- File naming or organization rules:
- Logo treatment specifics:

## Operational notes
- Optional implementation or review notes:
- Content structure preferences:
- Revision learnings to carry forward:
