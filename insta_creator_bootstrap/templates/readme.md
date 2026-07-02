# {{ project_name }}

This scaffold was created by the reusable Insta Creator bootstrap package.

## Next steps
1. Install the package locally: `python -m pip install -e .`
2. Fill in `docs/project-spec.md` with the active project’s real brand rules.
3. Confirm visual identity, typography, logo/mark rules, CTA conventions, and approval behavior.
4. Wire discovery cron to return exactly 5 numbered ideas.
5. Let the user continue by replying with `1`-`5` or explicitly naming a theme.
6. Run content production through `skills/social-media/insta-creator-workflow/SKILL.md`.
7. Review `docs/cron-templates.md` and adapt the planner / production / publication prompts.
8. Validate the scaffold:

```bash
python -m insta_creator_bootstrap validate --target .
```

## Production rule
The user should see only the shortlist/selection gate and the final approval payload. Internal brief, narrative, checklist, JSON, and rendering steps are orchestrator-owned.

If the workflow starts from a monthly plan, approval remains sequential: plan approval does not approve every post. Generate and approve one package at a time before moving to the next item.

## Approval payload
Final approval should include:
- final caption
- rendered card images already created for the post

The internal bundle still keeps:
- `manifest.json`
- `brief.md`
- `cards.json`
- `caption.md`
- `approval.md`
- `assets/`
