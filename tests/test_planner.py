from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from insta_creator_bootstrap.planner import (
    build_monthly_plan,
    build_production_queue,
    load_planner_profile,
    plan_month_to_dict,
    queue_to_dict,
    read_json_source,
)


class PlannerTests(unittest.TestCase):
    def _write_spec(self, root: Path) -> Path:
        spec = root / "project-spec.md"
        spec.write_text(
            """# Brand Spec: GranaFlow

## Project name
GranaFlow

## Target platform
Instagram feed carousels, primarily 4:5 portrait.

## Brand voice
Clear and practical.

## Visual rules
Dark premium fintech.

## CTA conventions
Use one clear CTA.

## Growth strategy
Keep approval-gated.

## Approval behavior
Approval channel: main channel
Send caption + images.

## Prohibited angles
No exaggerated claims.

## Asset constraints
Use PNG assets.
""",
            encoding="utf-8",
        )
        return spec

    def _write_profile(self, root: Path) -> Path:
        profile = root / "content-planner.md"
        profile.write_text(
            """# GranaFlow Content Planner Profile

## Cadence
- posts per week: 2
- story sequences per week: 4
- history window days: 30

## Content pillars
- Education — budget basics, 50-30-20, reserve
- Pain — invoice surprise, hidden leaks, overspending
- Product — beta, automation, visibility
- Seasonal — month start, salary cycle, close the month
- Interaction — poll, quiz, question box

## Highlight destinations
- Comece aqui
- Como funciona
- Beta
- Dúvidas

## Watch slot categories
- banking policy changes
- payment updates
- Pix updates
- tax and salary cycle

## Special date policy
- Use special dates only when they connect to money.
- If the date is low-signal, skip it.

## History rules
- Avoid repeating the same theme within 30 days.
- Keep the month balanced.
""",
            encoding="utf-8",
        )
        return profile

    def test_load_planner_profile_reads_project_branch(self) -> None:
        with TemporaryDirectory() as tmp:
            profile = load_planner_profile(self._write_profile(Path(tmp)))
            self.assertEqual(profile.cadence_posts_per_week, 2)
            self.assertEqual(profile.cadence_story_sequences_per_week, 4)
            self.assertEqual(profile.highlight_targets[0], "Comece aqui")
            self.assertIn("Education", profile.pillars[0]["name"])

    def test_build_monthly_plan_keeps_watch_slots_optional_and_uses_history(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self._write_spec(root)
            profile = self._write_profile(root)
            scheduled = [{"date": "2026-07-02", "format": "carousel", "theme": "already planned"}]
            history = [
                {"published_at": "2026-06-15", "theme": "50-30-20"},
                {"published_at": "2026-06-18", "theme": "50-30-20"},
                {"published_at": "2026-06-20", "theme": "invoice surprise"},
            ]
            special_dates = [
                {"date": "2026-07-09", "label": "Pix update", "signal": "banking policy changes", "relevant": False},
                {"date": "2026-07-15", "label": "Banking rule update", "signal": "banking policy changes", "relevant": True},
            ]
            plan = build_monthly_plan(
                project_spec_path=spec,
                planner_profile_path=profile,
                month="2026-07",
                project_id="granaflow",
                scheduled_items=scheduled,
                history_items=history,
                special_dates=special_dates,
            )
            data = plan_month_to_dict(plan)
            self.assertEqual(data["month"], "2026-07")
            self.assertGreaterEqual(data["summary"]["post_count"], 1)
            self.assertGreaterEqual(data["summary"]["story_count"], 1)
            self.assertEqual(len(data["skipped_watch_slots"]), 1)
            self.assertEqual(data["skipped_watch_slots"][0]["reason"], "no relevant signal")
            story_items = [item for item in data["items"] if item["category"] == "story"]
            evergreen_stories = [item for item in story_items if item["evergreen"]]
            self.assertTrue(evergreen_stories)
            self.assertTrue(any(item["highlight_target"] for item in evergreen_stories))
            self.assertTrue(any("theme repeats recent history" in " ".join(item["notes"]) for item in data["items"]))

    def test_production_queue_filters_to_approved_items(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self._write_spec(root)
            profile = self._write_profile(root)
            plan = build_monthly_plan(
                project_spec_path=spec,
                planner_profile_path=profile,
                month="2026-07",
                project_id="granaflow",
                history_items=[],
                special_dates=[],
            )
            plan_dict = plan_month_to_dict(plan)
            approved_ids = [plan_dict["items"][0]["item_id"], plan_dict["items"][1]["item_id"]]
            queue = build_production_queue(plan_dict, approved_item_ids=approved_ids)
            queue_dict = queue_to_dict(queue)
            self.assertEqual(queue_dict["approved_item_ids"], sorted(approved_ids))
            self.assertEqual(len(queue_dict["items"]), 2)
            self.assertTrue(all(item["queue_id"].startswith("queue-") for item in queue_dict["items"]))

    def test_read_json_source_accepts_file_and_inline_json(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.json"
            path.write_text(json.dumps({"items": [{"theme": "A"}, {"theme": "B"}]}), encoding="utf-8")
            self.assertEqual(len(read_json_source(path)), 2)
            self.assertEqual(len(read_json_source('[{"theme":"A"}]')), 1)


if __name__ == "__main__":
    unittest.main()
