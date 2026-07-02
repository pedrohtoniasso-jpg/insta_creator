from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from string import Template
from typing import Iterable, Sequence
import json
import re


class BootstrapError(RuntimeError):
    """Base error for bootstrap failures."""


class BootstrapValidationError(BootstrapError):
    """Raised when an existing spec or scaffold fails validation."""


@dataclass(frozen=True)
class BootstrapAction:
    path: Path
    description: str
    content: str


@dataclass(frozen=True)
class BootstrapResult:
    target: Path
    actions: tuple[BootstrapAction, ...]
    written: tuple[Path, ...]
    dry_run: bool


REQUIRED_SPEC_SECTIONS = [
    "project name",
    "target platform",
    "brand voice",
    "visual rules",
    "cta conventions",
    "growth strategy",
    "approval behavior",
    "prohibited angles",
    "asset constraints",
]

OPTIONAL_SPEC_SECTIONS = ["operational notes"]

_SECTION_SYNONYMS = {
    "voice": "brand voice",
    "brand voice": "brand voice",
    "project name": "project name",
    "name": "project name",
    "target platform": "target platform",
    "platform": "target platform",
    "visual rules": "visual rules",
    "cta conventions": "cta conventions",
    "growth strategy": "growth strategy",
    "approval behavior": "approval behavior",
    "prohibited angles": "prohibited angles",
    "prohibited angles or topics": "prohibited angles",
    "asset constraints": "asset constraints",
    "operational notes": "operational notes",
    "revision and learning loop": "revision and learning loop",
    "story storytelling style": "story storytelling style",
    "story style": "story storytelling style",
    "story format": "story storytelling style",
    "stories": "story storytelling style",
}

def normalize_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return slug.strip("-") or "insta-creator"


def infer_project_name(target: Path) -> str:
    name = target.name.replace("-", " ").replace("_", " ").strip()
    if not name:
        return "Insta Creator Project"
    return " ".join(part.capitalize() for part in name.split())


def _template_text(template_name: str) -> str:
    return resources.files(__package__).joinpath("templates", template_name).read_text(encoding="utf-8")


def render_template(template_name: str, **context: str) -> str:
    return Template(_template_text(template_name)).safe_substitute(context)


def _normalize_heading(heading: str) -> str:
    heading = heading.strip().lower()
    return _SECTION_SYNONYMS.get(heading, heading)


def _extract_sections(markdown: str) -> list[str]:
    sections: list[str] = []
    for line in markdown.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line.strip())
        if match:
            sections.append(_normalize_heading(match.group(1)))
    return sections


def _extract_section_body(markdown: str, heading: str) -> str:
    target = _normalize_heading(heading)
    collecting = False
    body: list[str] = []

    for line in markdown.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line.strip())
        if match:
            current = _normalize_heading(match.group(1))
            if collecting and current != target:
                break
            collecting = current == target
            continue
        if collecting:
            body.append(line)

    return "\n".join(body).strip()


def validate_project_spec(text: str) -> None:
    sections = _extract_sections(text)
    if not sections:
        raise BootstrapValidationError("Project spec does not contain any '##' sections.")

    missing = [section for section in REQUIRED_SPEC_SECTIONS if section not in sections]
    if missing:
        raise BootstrapValidationError(
            "Project spec is missing required sections: " + ", ".join(missing)
        )

    ordered_required = [section for section in sections if section in REQUIRED_SPEC_SECTIONS]
    required_in_order = [section for section in REQUIRED_SPEC_SECTIONS if section in ordered_required]
    if ordered_required[: len(required_in_order)] != required_in_order:
        raise BootstrapValidationError(
            "Project spec required sections are out of order; expected: "
            + ", ".join(REQUIRED_SPEC_SECTIONS)
        )

    approval_behavior = _extract_section_body(text, "approval behavior").lower()
    if "approval channel" not in approval_behavior and "main channel" not in approval_behavior:
        raise BootstrapValidationError(
            "Project spec approval behavior must define an approval channel or main channel."
        )


def _project_spec_path(target: Path) -> Path:
    return target / "docs" / "project-spec.md"


def _read_existing(path: Path) -> str | None:
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8")
    return None


def build_plan(
    target: Path,
    project_name: str | None = None,
    project_spec_path: Path | None = None,
    force: bool = False,
) -> tuple[BootstrapAction, ...]:
    target = target.expanduser().resolve()
    resolved_name = project_name or infer_project_name(target)
    resolved_slug = normalize_slug(resolved_name)
    project_spec_path = project_spec_path or _project_spec_path(target)

    actions: list[BootstrapAction] = []

    def add(path: Path, description: str, template_name: str, **ctx: str) -> None:
        existing = _read_existing(path)
        if existing is not None and not force:
            if path == project_spec_path:
                validate_project_spec(existing)
            return
        content = render_template(template_name, project_name=resolved_name, project_slug=resolved_slug, **ctx)
        actions.append(BootstrapAction(path=path, description=description, content=content))

    # Directory scaffold
    for directory in [target, target / "docs", target / "content", target / "content" / "posts"]:
        if not directory.exists():
            actions.append(
                BootstrapAction(
                    path=directory,
                    description=f"Create directory {directory.relative_to(target)}",
                    content="",
                )
            )

    # Core scaffold files
    add(target / "README.md", "Create project README", "readme.md")
    add(
        project_spec_path,
        "Create or refresh the project spec template",
        "project_spec.md",
    )
    add(target / "content" / "posts" / ".gitkeep", "Keep the post storage folder in git", "gitkeep.txt")

    return tuple(actions)


def _apply_action(action: BootstrapAction) -> None:
    if action.path.suffix == "":
        action.path.mkdir(parents=True, exist_ok=True)
        return
    action.path.parent.mkdir(parents=True, exist_ok=True)
    action.path.write_text(action.content, encoding="utf-8")


def bootstrap_project(
    target: str | Path,
    project_name: str | None = None,
    project_spec_path: str | Path | None = None,
    dry_run: bool = False,
    force: bool = False,
) -> BootstrapResult:
    target_path = Path(target).expanduser().resolve()
    spec_path = Path(project_spec_path).expanduser().resolve() if project_spec_path else None

    actions = build_plan(target_path, project_name=project_name, project_spec_path=spec_path, force=force)

    written: list[Path] = []
    if not dry_run:
        for action in actions:
            _apply_action(action)
            written.append(action.path)
    return BootstrapResult(target=target_path, actions=actions, written=tuple(written), dry_run=dry_run)


def result_to_dict(result: BootstrapResult) -> dict[str, object]:
    return {
        "target": str(result.target),
        "dry_run": result.dry_run,
        "planned_actions": [
            {
                "path": str(action.path),
                "description": action.description,
            }
            for action in result.actions
        ],
        "written": [str(path) for path in result.written],
    }


def validate_bootstrap_environment(target: str | Path, project_spec_path: str | Path | None = None) -> dict[str, object]:
    target_path = Path(target).expanduser().resolve()
    spec_path = Path(project_spec_path).expanduser().resolve() if project_spec_path else _project_spec_path(target_path)

    if not target_path.exists():
        raise BootstrapValidationError(f"Target directory does not exist: {target_path}")

    issues: list[str] = []
    expected_paths: Sequence[Path] = [
        target_path / "README.md",
        spec_path,
        target_path / "content" / "posts",
    ]

    for path in expected_paths:
        if not path.exists():
            issues.append(f"Missing expected path: {path.relative_to(target_path) if path.is_relative_to(target_path) else path}")

    if spec_path.exists() and spec_path.is_file():
        validate_project_spec(spec_path.read_text(encoding="utf-8"))
    elif spec_path.exists():
        raise BootstrapValidationError(f"Project spec path exists but is not a file: {spec_path}")

    if issues:
        raise BootstrapValidationError("; ".join(issues))

    return {"target": str(target_path), "project_spec": str(spec_path), "status": "ready"}
