from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .core import (
    BootstrapValidationError,
    bootstrap_project,
    result_to_dict,
    validate_bootstrap_environment,
)
from .renderer import render_cards, render_result_to_dict
from .selection_state import (
    load_latest_shortlist,
    resolve_selection_reply,
    save_latest_shortlist,
)
from .integration import content_run_input_to_prompt
from .planner import (
    build_monthly_plan,
    build_production_queue,
    plan_month_to_dict,
    queue_to_dict,
    read_json_source,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="insta_creator_bootstrap",
        description="Bootstrap the shared Insta Creator workflow scaffold.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--target", required=True, help="Target directory to bootstrap")
        subparser.add_argument("--project-name", help="Project name to use in templates")
        subparser.add_argument(
            "--project-spec",
            help="Override path to the project spec Markdown file",
        )
        subparser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files")

    plan = subparsers.add_parser("plan", help="Show the actions the bootstrap would take")
    add_common(plan)

    apply = subparsers.add_parser("apply", help="Create or refresh the shared scaffold")
    add_common(apply)
    apply.add_argument("--dry-run", action="store_true", help="Show actions without writing files")

    validate = subparsers.add_parser("validate", help="Validate an existing bootstrap scaffold")
    validate.add_argument("--target", required=True, help="Target directory to validate")
    validate.add_argument("--project-spec", help="Override path to the project spec Markdown file")

    render = subparsers.add_parser("render", help="Render cards.json into PNG assets using a project spec and visual template")
    render.add_argument("--project-spec", required=True, help="Selected project spec Markdown path")
    render.add_argument("--visual-template", required=True, help="Selected visual template Markdown path")
    render.add_argument("--cards", required=True, help="cards.json path")
    render.add_argument("--out", required=True, help="Output assets directory")

    shortlist = subparsers.add_parser("shortlist", help="Manage persisted shortlist continuation state")
    shortlist_sub = shortlist.add_subparsers(dest="shortlist_command", required=True)
    shortlist_save = shortlist_sub.add_parser("save", help="Save the latest 5-item shortlist for a project")
    shortlist_save.add_argument("--project-id", required=True)
    shortlist_save.add_argument("--job-id", required=True)
    shortlist_save.add_argument("--shortlist-json", required=True, help="JSON array with exactly 5 idea objects")
    shortlist_save.add_argument("--root", default=".")
    shortlist_save.add_argument("--project-spec")
    shortlist_save.add_argument("--visual-template")
    shortlist_save.add_argument("--output-format")
    shortlist_save.add_argument("--delivery-target")

    shortlist_show = shortlist_sub.add_parser("show", help="Show the latest shortlist state for a project")
    shortlist_show.add_argument("--project-id", required=True)
    shortlist_show.add_argument("--root", default=".")

    shortlist_resolve = shortlist_sub.add_parser("resolve", help="Resolve a terse reply into a content-run handoff")
    shortlist_resolve.add_argument("--project-id", required=True)
    shortlist_resolve.add_argument("--reply", required=True)
    shortlist_resolve.add_argument("--root", default=".")
    shortlist_resolve.add_argument("--prompt", action="store_true", help="Print the orchestrator prompt instead of JSON")

    plan_month = subparsers.add_parser("plan-month", help="Build the monthly editorial plan for a project")
    plan_month.add_argument("--project-spec", required=True, help="Selected project spec Markdown path")
    plan_month.add_argument("--month", required=True, help="Target month in YYYY-MM format")
    plan_month.add_argument("--project-id", help="Override project identifier")
    plan_month.add_argument("--planner-profile", help="Optional project planner profile Markdown path")
    plan_month.add_argument("--timezone", default="America/Sao_Paulo", help="Timezone label for the plan")
    plan_month.add_argument("--scheduled-json", help="JSON file or inline JSON with already scheduled items")
    plan_month.add_argument("--history-json", help="JSON file or inline JSON with recent history items")
    plan_month.add_argument("--special-dates-json", help="JSON file or inline JSON with special date watch slots")
    plan_month.add_argument("--output", help="Optional path to write the plan JSON")

    queue_from_plan = subparsers.add_parser("queue-from-plan", help="Convert an approved monthly plan into a production queue")
    queue_from_plan.add_argument("--plan-json", required=True, help="Plan JSON file or inline JSON")
    queue_from_plan.add_argument("--approved-ids-json", help="JSON array of approved item IDs")
    queue_from_plan.add_argument("--output", help="Optional path to write the queue JSON")

    return parser


def _print_actions(data: dict[str, object]) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _load_json_payload(source: str) -> object:
    text = source.strip()
    if text.startswith("[") or text.startswith("{"):
        return json.loads(text)
    path = Path(text).expanduser()
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command in {"plan", "apply"}:
        result = bootstrap_project(
            target=Path(args.target),
            project_name=args.project_name,
            project_spec_path=args.project_spec,
            dry_run=(args.command == "plan") or args.dry_run,
            force=args.force,
        )
        _print_actions(result_to_dict(result))
        return 0

    if args.command == "validate":
        try:
            status = validate_bootstrap_environment(args.target, project_spec_path=args.project_spec)
        except BootstrapValidationError as exc:
            print(str(exc))
            return 1
        _print_actions(status)
        return 0

    if args.command == "render":
        try:
            result = render_cards(
                project_spec_path=args.project_spec,
                visual_template_path=args.visual_template,
                cards_json_path=args.cards,
                output_dir=args.out,
            )
        except BootstrapValidationError as exc:
            print(str(exc))
            return 1
        _print_actions(render_result_to_dict(result))
        return 0

    if args.command == "shortlist":
        try:
            if args.shortlist_command == "save":
                shortlist = json.loads(args.shortlist_json)
                if not isinstance(shortlist, list):
                    raise BootstrapValidationError("--shortlist-json must be a JSON array.")
                state = save_latest_shortlist(
                    project_id=args.project_id,
                    job_id=args.job_id,
                    shortlist=shortlist,
                    root=args.root,
                    project_spec_path=args.project_spec,
                    visual_template_path=args.visual_template,
                    output_format=args.output_format,
                    delivery_target=args.delivery_target,
                )
                _print_actions({"status": "saved", "state": state.to_dict()})
                return 0
            if args.shortlist_command == "show":
                state = load_latest_shortlist(args.project_id, root=args.root)
                _print_actions(state.to_dict())
                return 0
            if args.shortlist_command == "resolve":
                run_input = resolve_selection_reply(args.reply, project_id=args.project_id, root=args.root)
                if args.prompt:
                    print(content_run_input_to_prompt(run_input))
                else:
                    _print_actions({
                        "project_id": run_input.project_id,
                        "project_spec_path": run_input.project_spec_path,
                        "visual_template_path": run_input.visual_template_path,
                        "theme": run_input.theme,
                        "source": run_input.source,
                        "trace_id": run_input.trace_id,
                        "user_action": run_input.user_action,
                        "output_format": run_input.output_format,
                        "change_request": run_input.change_request,
                        "structured_fields": run_input.structured_fields,
                    })
                return 0
        except (BootstrapValidationError, json.JSONDecodeError) as exc:
            print(str(exc))
            return 1

    if args.command == "plan-month":
        try:
            plan = build_monthly_plan(
                project_spec_path=args.project_spec,
                month=args.month,
                project_id=args.project_id,
                planner_profile_path=args.planner_profile,
                timezone=args.timezone,
                scheduled_items=read_json_source(args.scheduled_json),
                history_items=read_json_source(args.history_json),
                special_dates=read_json_source(args.special_dates_json),
            )
            payload = plan_month_to_dict(plan)
            if args.output:
                Path(args.output).expanduser().write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            _print_actions(payload)
            return 0
        except (BootstrapValidationError, json.JSONDecodeError, OSError) as exc:
            print(str(exc))
            return 1

    if args.command == "queue-from-plan":
        try:
            plan_payload = _load_json_payload(args.plan_json)
            if not isinstance(plan_payload, dict):
                raise BootstrapValidationError("--plan-json must contain a JSON object.")
            approved_ids: list[str] = []
            if args.approved_ids_json:
                approved_payload = _load_json_payload(args.approved_ids_json)
                if not isinstance(approved_payload, list):
                    raise BootstrapValidationError("--approved-ids-json must be a JSON array.")
                approved_ids = [str(item) for item in approved_payload if str(item).strip()]
            queue = build_production_queue(plan_payload, approved_item_ids=approved_ids)
            payload = queue_to_dict(queue)
            if args.output:
                Path(args.output).expanduser().write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            _print_actions(payload)
            return 0
        except (BootstrapValidationError, json.JSONDecodeError, OSError) as exc:
            print(str(exc))
            return 1

    parser.error(f"Unknown command: {args.command}")
    return 2
