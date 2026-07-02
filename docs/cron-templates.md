# Cron Templates

These templates are the recommended starting point when installing `insta-creator` into a new agent or workspace.

## 1) Monthly planning cron

Purpose: generate the editorial plan for one month and stop for approval.

### Behavior rules
- Inspect already scheduled content first.
- Deliver the monthly plan in the required itemized format.
- Do not use Markdown tables.
- Do not create production or publication jobs from this planner step.

### Prompt template

```text
You are the monthly editorial planner for <PROJECT_NAME> using the `insta-creator-planner` skill.

Goal: create the editorial plan for <MONTH> and deliver it for human approval.

Requirements:
- inspect already scheduled content before placing anything new
- plan posts, stories, highlights, and watch slots
- keep history awareness so themes do not repeat too soon
- present the plan in this exact human format, one block per item, with no Markdown table:

DD/MM
- Tema: ...
- Tipo: ...
- Desenvolvimento: ...

Rules:
- the monthly plan is for approval only
- do not generate post packages here
- do not create publication jobs here
- if a date is only relevant when a real signal appears, mark it as a watch slot
```

## 2) Sequential production cron / prompt

Purpose: produce one approved item from the monthly plan and stop for post-level approval.

### Behavior rules
- Accept one specific approved plan item.
- Generate only one post/story package.
- Deliver only the final approval payload.
- Do not automatically continue to the next item.

### Prompt template

```text
Use `insta-creator` to generate the final package for exactly one approved plan item.

Approved item:
- project: <PROJECT_NAME>
- item_id: <ITEM_ID>
- theme: <THEME>
- format: <FORMAT>
- target date: <DATE>

Rules:
- generate only this one package
- deliver only the approval payload: caption + rendered card images
- do not paste brief.md, cards.json, approval.md, or slide-by-slide descriptions unless explicitly requested
- do not schedule publication yet
- stop and wait for explicit approval or revision
```

## 3) Publication cron template

Purpose: publish one already approved package.

### Behavior rules
- Only use after explicit approval of the specific package.
- Point to one deterministic post folder.
- Never assume monthly-plan approval is enough.

### Prompt template

```text
Publish the already approved Instagram package below.

Approved package path:
- <POST_FOLDER>

Rules:
- use caption.md as the copy-ready caption
- use only the rendered media in assets/
- publish only this package
- do not revise content in this step
- do not touch any other planned item
```
