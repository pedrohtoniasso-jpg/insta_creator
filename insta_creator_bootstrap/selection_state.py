from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import re
from typing import Any, Mapping, Sequence

from .core import BootstrapValidationError
from .integration import ContentRunInput, normalize_content_run_input

_STATE_DIR = Path("state") / "latest-shortlist"
_SELECTION_RE = re.compile(r"^\s*(?:op(?:ç|c)ão\s*)?([1-5])\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class LatestShortlistState:
    project_id: str
    job_id: str
    source: str
    created_at: str
    shortlist: tuple[dict[str, Any], ...]
    project_spec_path: str | None = None
    visual_template_path: str | None = None
    output_format: str | None = None
    delivery_target: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "job_id": self.job_id,
            "source": self.source,
            "created_at": self.created_at,
            "shortlist": list(self.shortlist),
            "project_spec_path": self.project_spec_path,
            "visual_template_path": self.visual_template_path,
            "output_format": self.output_format,
            "delivery_target": self.delivery_target,
        }


def parse_selection_reply(text: str) -> int | None:
    """Return a 1-based selected option for replies like `5` or `Opção 5`."""

    match = _SELECTION_RE.match(text or "")
    if not match:
        return None
    return int(match.group(1))


def _state_path(project_id: str, *, root: str | Path = ".") -> Path:
    slug = re.sub(r"[^a-z0-9]+", "-", project_id.strip().lower()).strip("-")
    if not slug:
        raise BootstrapValidationError("project_id is required.")
    return Path(root).expanduser().resolve() / _STATE_DIR / f"{slug}.json"


def _normalize_shortlist(shortlist: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    if len(shortlist) != 5:
        raise BootstrapValidationError("Shortlist state must contain exactly 5 ideas.")
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(shortlist, start=1):
        data = dict(item)
        theme = data.get("theme") or data.get("title") or data.get("idea") or data.get("topic")
        if not str(theme or "").strip():
            raise BootstrapValidationError(f"Shortlist item {index} must include theme/title/idea/topic.")
        data.setdefault("number", index)
        data.setdefault("theme", str(theme).strip())
        normalized.append(data)
    return tuple(normalized)


def save_latest_shortlist(
    *,
    project_id: str,
    job_id: str,
    shortlist: Sequence[Mapping[str, Any]],
    root: str | Path = ".",
    source: str = "cron",
    project_spec_path: str | None = None,
    visual_template_path: str | None = None,
    output_format: str | None = None,
    delivery_target: str | None = None,
    created_at: str | None = None,
) -> LatestShortlistState:
    """Persist the latest project shortlist so a future one-digit reply can resume production."""

    state = LatestShortlistState(
        project_id=project_id,
        job_id=job_id,
        source=source,
        created_at=created_at or datetime.now(timezone.utc).isoformat(),
        shortlist=_normalize_shortlist(shortlist),
        project_spec_path=project_spec_path,
        visual_template_path=visual_template_path,
        output_format=output_format,
        delivery_target=delivery_target,
    )
    path = _state_path(project_id, root=root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def load_latest_shortlist(project_id: str, *, root: str | Path = ".") -> LatestShortlistState:
    path = _state_path(project_id, root=root)
    if not path.exists():
        raise BootstrapValidationError(f"No pending shortlist state found for project '{project_id}': {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise BootstrapValidationError("Latest shortlist state must be a JSON object.")
    shortlist_value = raw.get("shortlist")
    if not isinstance(shortlist_value, Sequence) or isinstance(shortlist_value, (str, bytes)):
        raise BootstrapValidationError("Latest shortlist state must include a shortlist array.")
    return LatestShortlistState(
        project_id=str(raw.get("project_id") or project_id),
        job_id=str(raw.get("job_id") or "unknown"),
        source=str(raw.get("source") or "cron"),
        created_at=str(raw.get("created_at") or ""),
        shortlist=_normalize_shortlist([dict(item) for item in shortlist_value if isinstance(item, Mapping)]),
        project_spec_path=str(raw["project_spec_path"]) if raw.get("project_spec_path") else None,
        visual_template_path=str(raw["visual_template_path"]) if raw.get("visual_template_path") else None,
        output_format=str(raw["output_format"]) if raw.get("output_format") else None,
        delivery_target=str(raw["delivery_target"]) if raw.get("delivery_target") else None,
    )


def resolve_selection_reply(
    reply: str,
    *,
    project_id: str,
    root: str | Path = ".",
) -> ContentRunInput:
    """Resolve a terse chat reply (`1`-`5` or `Option 5`) into a ContentRunInput."""

    selected_option = parse_selection_reply(reply)
    if selected_option is None:
        raise BootstrapValidationError("Reply is not a valid shortlist selection. Use 1-5 or 'Opção N'.")
    state = load_latest_shortlist(project_id, root=root)
    payload: dict[str, Any] = {
        "project_id": state.project_id,
        "selection": {
            "shortlist_id": f"cron:{state.job_id}",
            "selected_option": selected_option,
            "user_action": "select",
        },
        "shortlist": list(state.shortlist),
        "source": f"cron:{state.job_id}",
    }
    if state.output_format:
        payload["output_format"] = state.output_format
    if state.delivery_target:
        payload["delivery_target"] = state.delivery_target
    if state.project_spec_path:
        payload["project_spec_path"] = state.project_spec_path
    if state.visual_template_path:
        payload["visual_template_path"] = state.visual_template_path
    return normalize_content_run_input(payload, root=root)
