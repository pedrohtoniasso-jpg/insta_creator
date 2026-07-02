from __future__ import annotations

from calendar import monthrange
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
import json
import re
from typing import Any, Iterable, Sequence

from .core import BootstrapValidationError
from .integration import load_project_spec


_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
_BULLET_RE = re.compile(r"^[-*]\s+(.+?)\s*$")
_MONTH_RE = re.compile(r"^(\d{4})-(\d{2})$")
_WORD_RE = re.compile(r"[a-z0-9À-ÿ]+", re.IGNORECASE)

DEFAULT_POST_WEEKDAYS = (1, 3)
DEFAULT_STORY_WEEKDAYS = (0, 2, 4, 6)
DEFAULT_GENERIC_PILLARS = (
    {
        "name": "education",
        "themes": ("budget basics", "50-30-20", "emergency fund", "card habits"),
        "objective": "save",
        "format": "carousel",
    },
    {
        "name": "pain",
        "themes": ("hidden leaks", "cash flow confusion", "invoice surprise", "overspending"),
        "objective": "comment",
        "format": "carousel",
    },
    {
        "name": "product",
        "themes": ("automation", "beta onboarding", "categorization", "visibility"),
        "objective": "dm",
        "format": "carousel",
    },
    {
        "name": "seasonal",
        "themes": ("month start", "salary cycle", "close the month", "special dates"),
        "objective": "share",
        "format": "carousel",
    },
    {
        "name": "stories",
        "themes": ("quiz", "poll", "question box", "dm prompt"),
        "objective": "comment",
        "format": "story",
    },
)
DEFAULT_HIGHLIGHTS = ("Comece aqui", "Como funciona", "Dúvidas")
DEFAULT_WATCH_CATEGORIES = (
    "banking policy changes",
    "payment updates",
    "tax and salary cycle",
    "consumer behavior shifts",
)


@dataclass(frozen=True)
class PlannerProfile:
    path: Path | None
    title: str
    cadence_posts_per_week: int
    cadence_story_sequences_per_week: int
    pillars: tuple[dict[str, Any], ...]
    highlight_targets: tuple[str, ...]
    watch_slot_categories: tuple[str, ...]
    history_window_days: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path) if self.path else None,
            "title": self.title,
            "cadence_posts_per_week": self.cadence_posts_per_week,
            "cadence_story_sequences_per_week": self.cadence_story_sequences_per_week,
            "pillars": [
                {
                    "name": pillar["name"],
                    "themes": list(pillar["themes"]),
                    "objective": pillar["objective"],
                    "format": pillar["format"],
                }
                for pillar in self.pillars
            ],
            "highlight_targets": list(self.highlight_targets),
            "watch_slot_categories": list(self.watch_slot_categories),
            "history_window_days": self.history_window_days,
        }


@dataclass(frozen=True)
class PlannedItem:
    item_id: str
    date: str
    format: str
    category: str
    pillar: str
    theme: str
    objective: str
    cta: str
    evergreen: bool
    highlight_target: str | None
    approval_state: str
    source_kind: str
    status: str
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "date": self.date,
            "format": self.format,
            "category": self.category,
            "pillar": self.pillar,
            "theme": self.theme,
            "objective": self.objective,
            "cta": self.cta,
            "evergreen": self.evergreen,
            "highlight_target": self.highlight_target,
            "approval_state": self.approval_state,
            "source_kind": self.source_kind,
            "status": self.status,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class MonthlyEditorialPlan:
    project_id: str
    project_name: str
    project_spec_path: str
    month: str
    timezone: str
    planner_profile_path: str | None
    summary: dict[str, Any]
    history_summary: dict[str, Any]
    items: tuple[PlannedItem, ...]
    skipped_watch_slots: tuple[dict[str, Any], ...]
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        posts = [item.to_dict() for item in self.items if item.category == "post"]
        stories = [item.to_dict() for item in self.items if item.category == "story"]
        highlights = [item.to_dict() for item in self.items if item.category == "highlight"]
        watch_slots = [item.to_dict() for item in self.items if item.category == "watch"]
        return {
            "version": "monthly-plan-v1",
            "project_id": self.project_id,
            "project_name": self.project_name,
            "project_spec_path": self.project_spec_path,
            "month": self.month,
            "timezone": self.timezone,
            "planner_profile_path": self.planner_profile_path,
            "summary": self.summary,
            "history_summary": self.history_summary,
            "posts": posts,
            "stories": stories,
            "highlights": highlights,
            "watch_slots": watch_slots,
            "skipped_watch_slots": list(self.skipped_watch_slots),
            "items": [item.to_dict() for item in self.items],
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class ProductionQueueItem:
    queue_id: str
    source_item_id: str
    project_id: str
    month: str
    date: str
    format: str
    category: str
    pillar: str
    theme: str
    objective: str
    cta: str
    evergreen: bool
    highlight_target: str | None
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "queue_id": self.queue_id,
            "source_item_id": self.source_item_id,
            "project_id": self.project_id,
            "month": self.month,
            "date": self.date,
            "format": self.format,
            "category": self.category,
            "pillar": self.pillar,
            "theme": self.theme,
            "objective": self.objective,
            "cta": self.cta,
            "evergreen": self.evergreen,
            "highlight_target": self.highlight_target,
            "status": self.status,
        }


@dataclass(frozen=True)
class ProductionQueue:
    project_id: str
    month: str
    approved_item_ids: tuple[str, ...]
    items: tuple[ProductionQueueItem, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": "production-queue-v1",
            "project_id": self.project_id,
            "month": self.month,
            "approved_item_ids": list(self.approved_item_ids),
            "items": [item.to_dict() for item in self.items],
        }


def _parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal current, buffer
        if current is not None:
            sections[current] = "\n".join(buffer).strip()
        current = None
        buffer = []

    for line in text.splitlines():
        match = _SECTION_RE.match(line.strip())
        if match:
            flush()
            current = match.group(1).strip().lower()
            continue
        if current is not None:
            buffer.append(line)
    flush()
    return sections


def _bullet_list(text: str | None) -> tuple[str, ...]:
    if not text:
        return ()
    items: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        bullet = _BULLET_RE.match(line)
        if bullet:
            items.append(bullet.group(1).strip())
        elif line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4.") or line.startswith("5."):
            items.append(line.split(".", 1)[1].strip())
    return tuple(item for item in items if item)


def _coerce_int(text: str | None, label: str, default: int) -> int:
    if not text:
        return default
    match = re.search(rf"{re.escape(label)}\s*[:=]\s*(\d+)", text, re.IGNORECASE)
    if match:
        return max(1, int(match.group(1)))
    return default


def _parse_pillar_item(raw: str) -> dict[str, Any]:
    cleaned = raw.strip().strip("-•*")
    if " — " in cleaned:
        name, theme_blob = cleaned.split(" — ", 1)
    elif " - " in cleaned:
        name, theme_blob = cleaned.split(" - ", 1)
    elif ":" in cleaned:
        name, theme_blob = cleaned.split(":", 1)
    else:
        name, theme_blob = cleaned, cleaned
    themes = [part.strip() for part in re.split(r"[;,/|]", theme_blob) if part.strip()]
    if not themes:
        themes = [name.strip()]
    objective = "save"
    lowered = name.lower()
    if any(token in lowered for token in ["pain", "diagn", "proble", "erro", "vaz", "leak"]):
        objective = "comment"
    elif any(token in lowered for token in ["product", "produto", "beta", "automation", "automação"]):
        objective = "dm"
    elif any(token in lowered for token in ["season", "sazon", "data", "momento", "context"]):
        objective = "share"
    elif any(token in lowered for token in ["story", "stories", "inter", "quiz", "poll", "enquete"]):
        objective = "comment"
    return {
        "name": name.strip(),
        "themes": tuple(themes),
        "objective": objective,
        "format": "story" if "story" in lowered or "stories" in lowered else "carousel",
    }


def _default_profile() -> PlannerProfile:
    return PlannerProfile(
        path=None,
        title="Default planner profile",
        cadence_posts_per_week=2,
        cadence_story_sequences_per_week=4,
        pillars=tuple(DEFAULT_GENERIC_PILLARS),
        highlight_targets=DEFAULT_HIGHLIGHTS,
        watch_slot_categories=DEFAULT_WATCH_CATEGORIES,
        history_window_days=30,
    )


def load_planner_profile(path: str | Path | None) -> PlannerProfile:
    if path is None:
        return _default_profile()
    profile_path = Path(path).expanduser().resolve()
    raw = profile_path.read_text(encoding="utf-8")
    sections = _parse_sections(raw)
    title = profile_path.stem.replace("-", " ").title()
    if raw.strip().startswith("#"):
        first_line = next((line.strip()[1:].strip() for line in raw.splitlines() if line.strip().startswith("# ")), None)
        if first_line:
            title = first_line
    cadence = sections.get("cadence", "")
    pillars = tuple(_parse_pillar_item(item) for item in _bullet_list(sections.get("content pillars")))
    if not pillars:
        pillars = tuple(DEFAULT_GENERIC_PILLARS)
    highlight_targets = _bullet_list(sections.get("highlight destinations")) or DEFAULT_HIGHLIGHTS
    watch_slot_categories = _bullet_list(sections.get("watch slot categories")) or DEFAULT_WATCH_CATEGORIES
    history_window_days = _coerce_int(cadence, "history window days", 30)
    posts_per_week = _coerce_int(cadence, "posts per week", 2)
    story_sequences_per_week = _coerce_int(cadence, "story sequences per week", 4)
    return PlannerProfile(
        path=profile_path,
        title=title,
        cadence_posts_per_week=posts_per_week,
        cadence_story_sequences_per_week=story_sequences_per_week,
        pillars=pillars,
        highlight_targets=tuple(highlight_targets),
        watch_slot_categories=tuple(watch_slot_categories),
        history_window_days=history_window_days,
    )


def _parse_month(month: str) -> tuple[int, int]:
    match = _MONTH_RE.match(month.strip())
    if not match:
        raise BootstrapValidationError("month must use YYYY-MM format.")
    year = int(match.group(1))
    month_num = int(match.group(2))
    if not 1 <= month_num <= 12:
        raise BootstrapValidationError("month must use YYYY-MM format.")
    return year, month_num


def _month_dates(year: int, month: int) -> list[date]:
    return [date(year, month, day) for day in range(1, monthrange(year, month)[1] + 1)]


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    text = str(value)
    if len(text) >= 10:
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return None
    return None


def _normalize_text(value: Any) -> str:
    text = str(value or "").strip().lower()
    return " ".join(part for part in _WORD_RE.findall(text))


def _theme_counts(history_items: Sequence[dict[str, Any]], window_days: int) -> Counter[str]:
    counts: Counter[str] = Counter()
    cutoff = date.today() - timedelta(days=window_days)
    for item in history_items:
        if not isinstance(item, dict):
            continue
        item_date = _parse_date(item.get("published_at") or item.get("date") or item.get("created_at"))
        if item_date is not None and item_date < cutoff:
            continue
        for key in ("theme", "pillar", "topic", "title"):
            normalized = _normalize_text(item.get(key))
            if normalized:
                counts[normalized] += 1
                break
    return counts


def _build_history_summary(history_items: Sequence[dict[str, Any]], window_days: int) -> dict[str, Any]:
    counts = _theme_counts(history_items, window_days)
    return {
        "window_days": window_days,
        "tracked_items": len(history_items),
        "top_themes": counts.most_common(5),
    }


def _pick_slot_weekdays(count: int, *, for_stories: bool) -> tuple[int, ...]:
    if for_stories:
        presets = {
            1: (2,),
            2: (1, 4),
            3: (0, 3, 5),
            4: DEFAULT_STORY_WEEKDAYS,
        }
    else:
        presets = {
            1: (2,),
            2: DEFAULT_POST_WEEKDAYS,
            3: (1, 3, 5),
            4: (0, 2, 4, 6),
        }
    return presets.get(count, presets[max(presets)])


def _dates_on_weekdays(dates: Sequence[date], weekdays: Sequence[int]) -> list[date]:
    return [day for day in dates if day.weekday() in weekdays]


def _shift_to_free_day(candidate: date, occupied: set[date], month_end: date) -> date | None:
    if candidate not in occupied:
        return candidate
    for delta in range(1, 4):
        shifted = candidate + timedelta(days=delta)
        if shifted.month != candidate.month or shifted > month_end:
            break
        if shifted not in occupied:
            return shifted
    return None


def _derive_cta(objective: str, format_name: str) -> str:
    if format_name == "story":
        if objective == "dm":
            return "Responder no direct"
        if objective == "comment":
            return "Responder ao sticker"
        return "Interagir no story"
    if objective == "share":
        return "Compartilhar"
    if objective == "comment":
        return "Comentar"
    if objective == "dm":
        return "Enviar no direct"
    return "Salvar"


def _derive_story_type(pillar_name: str, objective: str) -> str:
    lowered = pillar_name.lower()
    if any(token in lowered for token in ["product", "produto", "beta", "automation", "automação"]):
        return "dm_prompt"
    if any(token in lowered for token in ["pain", "proble", "erro", "vaz"]):
        return "question_box"
    if any(token in lowered for token in ["season", "sazon", "data", "momento"]):
        return "poll_this_or_that"
    if objective == "save":
        return "quick_tip"
    if objective == "share":
        return "myth_fact"
    return "poll_preference"


def _story_sticker(story_type: str, theme: str) -> dict[str, Any]:
    if story_type == "dm_prompt":
        return {"type": "dm_prompt", "prompt": f"Me chama sobre {theme}", "options": []}
    if story_type == "question_box":
        return {"type": "question_box", "prompt": f"Qual sua dúvida sobre {theme}?", "options": []}
    if story_type == "poll_this_or_that":
        return {"type": "poll", "prompt": f"Qual opção você prefere em {theme}?", "options": ["A", "B"]}
    if story_type == "quiz":
        return {"type": "quiz", "prompt": f"O que você sabe sobre {theme}?", "options": ["Verdade", "Mito"]}
    return {"type": "poll", "prompt": f"O que você acha de {theme}?", "options": ["Quero", "Depois"]}


def _story_highlight_target(index: int, targets: Sequence[str]) -> str | None:
    if not targets:
        return None
    return targets[index % len(targets)]


def _recent_theme_set(history_counts: Counter[str]) -> set[str]:
    return {key for key, count in history_counts.items() if count > 0}


def _select_theme(pillar: dict[str, Any], history_counts: Counter[str], used_themes: set[str]) -> tuple[str, list[str]]:
    notes: list[str] = []
    for theme in pillar["themes"]:
        normalized = _normalize_text(theme)
        if normalized not in history_counts and normalized not in used_themes:
            used_themes.add(normalized)
            return theme, notes
    for theme in pillar["themes"]:
        normalized = _normalize_text(theme)
        if normalized not in used_themes:
            used_themes.add(normalized)
            if normalized in history_counts:
                notes.append("theme repeats recent history; kept because no fresher option was available")
            return theme, notes
    fallback = pillar["themes"][0]
    normalized = _normalize_text(fallback)
    used_themes.add(normalized)
    if normalized in history_counts:
        notes.append("theme repeats recent history; kept as fallback")
    return fallback, notes


def _build_planned_item(
    *,
    project_id: str,
    month: str,
    kind: str,
    index: int,
    planned_date: date,
    pillar: dict[str, Any],
    theme: str,
    objective: str,
    evergreen: bool = False,
    highlight_target: str | None = None,
    source_kind: str = "planner",
    notes: Sequence[str] = (),
) -> PlannedItem:
    item_id = _normalize_text(f"{month}-{kind}-{index}-{pillar['name']}-{theme}").replace(" ", "-")
    return PlannedItem(
        item_id=f"{project_id}-{item_id}".strip("-"),
        date=planned_date.isoformat(),
        format="story" if kind in {"story", "highlight"} else "carousel",
        category=kind,
        pillar=pillar["name"],
        theme=theme,
        objective=objective,
        cta=_derive_cta(objective, "story" if kind in {"story", "highlight"} else "carousel"),
        evergreen=evergreen,
        highlight_target=highlight_target,
        approval_state="draft",
        source_kind=source_kind,
        status="planned",
        notes=tuple(notes),
    )


def _special_slot_is_relevant(slot: dict[str, Any], categories: Sequence[str]) -> bool:
    explicit_flags = [slot.get(key) for key in ("relevant", "is_relevant", "relevant_now") if key in slot]
    if explicit_flags:
        return any(bool(flag) for flag in explicit_flags)
    label = _normalize_text(slot.get("label") or slot.get("title") or slot.get("theme"))
    signal = _normalize_text(slot.get("signal") or slot.get("category") or slot.get("event_type"))
    for category in categories:
        cat = _normalize_text(category)
        if cat and (cat in label or cat in signal):
            return True
    return False


def build_monthly_plan(
    *,
    project_spec_path: str | Path,
    month: str,
    project_id: str | None = None,
    planner_profile_path: str | Path | None = None,
    timezone: str = "America/Sao_Paulo",
    scheduled_items: Sequence[dict[str, Any]] = (),
    history_items: Sequence[dict[str, Any]] = (),
    special_dates: Sequence[dict[str, Any]] = (),
) -> MonthlyEditorialPlan:
    spec = load_project_spec(project_spec_path)
    profile = load_planner_profile(planner_profile_path)
    year, month_num = _parse_month(month)
    dates = _month_dates(year, month_num)
    month_end = dates[-1]
    plan_project_id = project_id or _normalize_text(spec.project_name or spec.title or Path(project_spec_path).stem)
    history_counts = _theme_counts(history_items, profile.history_window_days)
    history_summary = _build_history_summary(history_items, profile.history_window_days)
    occupied: set[date] = set()
    for scheduled in scheduled_items:
        if not isinstance(scheduled, dict):
            continue
        scheduled_date = _parse_date(scheduled.get("date") or scheduled.get("planned_date") or scheduled.get("next_run_at"))
        if scheduled_date is not None and scheduled_date.year == year and scheduled_date.month == month_num:
            occupied.add(scheduled_date)
    used_themes: set[str] = _recent_theme_set(history_counts)
    items: list[PlannedItem] = []
    skipped_watch_slots: list[dict[str, Any]] = []
    summary: dict[str, Any] = {
        "posts_per_week": profile.cadence_posts_per_week,
        "story_sequences_per_week": profile.cadence_story_sequences_per_week,
        "pillars": [pillar["name"] for pillar in profile.pillars],
        "highlight_targets": list(profile.highlight_targets),
        "watch_slot_categories": list(profile.watch_slot_categories),
        "scheduled_conflicts_avoided": 0,
    }

    post_weekdays = _pick_slot_weekdays(profile.cadence_posts_per_week, for_stories=False)
    story_weekdays = _pick_slot_weekdays(profile.cadence_story_sequences_per_week, for_stories=True)
    post_candidates = _dates_on_weekdays(dates, post_weekdays)
    story_candidates = _dates_on_weekdays(dates, story_weekdays)

    pillar_counts: Counter[str] = Counter()
    post_index = 0
    for candidate in post_candidates:
        placement = _shift_to_free_day(candidate, occupied, month_end)
        if placement is None:
            summary["scheduled_conflicts_avoided"] += 1
            continue
        if placement != candidate:
            summary["scheduled_conflicts_avoided"] += 1
        occupied.add(placement)
        pillar = min(profile.pillars, key=lambda p: (pillar_counts[p["name"]], p["name"]))
        theme, notes = _select_theme(pillar, history_counts, used_themes)
        pillar_counts[pillar["name"]] += 1
        post_index += 1
        items.append(
            _build_planned_item(
                project_id=plan_project_id,
                month=month,
                kind="post",
                index=post_index,
                planned_date=placement,
                pillar=pillar,
                theme=theme,
                objective=pillar["objective"],
                evergreen=True,
                source_kind="planner",
                notes=notes,
            )
        )

    story_index = 0
    highlight_index = 0
    for candidate in story_candidates:
        placement = _shift_to_free_day(candidate, occupied, month_end)
        if placement is None:
            summary["scheduled_conflicts_avoided"] += 1
            continue
        if placement != candidate:
            summary["scheduled_conflicts_avoided"] += 1
        occupied.add(placement)
        pillar = min(profile.pillars, key=lambda p: (pillar_counts[p["name"]], p["name"]))
        theme, notes = _select_theme(pillar, history_counts, used_themes)
        pillar_counts[pillar["name"]] += 1
        story_index += 1
        story_type = _derive_story_type(pillar["name"], pillar["objective"])
        evergreen = pillar["name"].lower() not in {"stories", "interaction"}
        highlight_target = _story_highlight_target(highlight_index, profile.highlight_targets) if evergreen else None
        if highlight_target is not None and evergreen:
            highlight_index += 1
        notes = list(notes)
        notes.append(f"story_type={story_type}")
        if evergreen and highlight_target:
            notes.append(f"highlight_target={highlight_target}")
        story_slug = _normalize_text(f"{month}-story-{story_index}-{pillar['name']}-{theme}").replace(" ", "-")
        items.append(
            PlannedItem(
                item_id=f"{plan_project_id}-{story_slug}",
                date=placement.isoformat(),
                format="story",
                category="story",
                pillar=pillar["name"],
                theme=theme,
                objective=pillar["objective"],
                cta=_derive_cta(pillar["objective"], "story"),
                evergreen=evergreen,
                highlight_target=highlight_target,
                approval_state="draft",
                source_kind=story_type,
                status="planned",
                notes=tuple(notes),
            )
        )

    for slot_index, slot in enumerate(special_dates, start=1):
        if not isinstance(slot, dict):
            continue
        slot_date = _parse_date(slot.get("date") or slot.get("planned_date"))
        if slot_date is None or slot_date.year != year or slot_date.month != month_num:
            continue
        label = str(slot.get("label") or slot.get("title") or slot.get("theme") or "special event").strip()
        if not _special_slot_is_relevant(slot, profile.watch_slot_categories):
            skipped_watch_slots.append(
                {
                    "date": slot_date.isoformat(),
                    "label": label,
                    "signal": slot.get("signal") or slot.get("category") or slot.get("event_type"),
                    "reason": "no relevant signal",
                    "action": "skip",
                }
            )
            continue
        placement = _shift_to_free_day(slot_date, occupied, month_end)
        if placement is None:
            skipped_watch_slots.append(
                {
                    "date": slot_date.isoformat(),
                    "label": label,
                    "signal": slot.get("signal") or slot.get("category") or slot.get("event_type"),
                    "reason": "conflict with occupied dates",
                    "action": "skip",
                }
            )
            continue
        if placement != slot_date:
            summary["scheduled_conflicts_avoided"] += 1
        occupied.add(placement)
        pillar = min(profile.pillars, key=lambda p: (pillar_counts[p["name"]], p["name"]))
        theme = label
        objective = str(slot.get("objective") or pillar["objective"])
        item_format = str(slot.get("format") or slot.get("output_format") or pillar["format"] or "carousel")
        evergreen = bool(slot.get("evergreen", False))
        highlight_target = slot.get("highlight_target") if evergreen else None
        watch_slug = _normalize_text(f"{month}-watch-{slot_index}-{label}").replace(" ", "-")
        items.append(
            PlannedItem(
                item_id=f"{plan_project_id}-{watch_slug}",
                date=placement.isoformat(),
                format=item_format,
                category="watch",
                pillar=pillar["name"],
                theme=theme,
                objective=objective,
                cta=_derive_cta(objective, item_format),
                evergreen=evergreen,
                highlight_target=highlight_target,
                approval_state="draft",
                source_kind=str(slot.get("signal") or slot.get("category") or "watch"),
                status="planned",
                notes=(f"special_date={slot_date.isoformat()}",),
            )
        )

    highlight_items: list[PlannedItem] = []
    highlight_pillars = [pillar for pillar in profile.pillars if pillar["name"].lower() not in {"stories", "interaction"}]
    for idx, target in enumerate(profile.highlight_targets, start=1):
        if not story_candidates:
            break
        base_pillar = highlight_pillars[(idx - 1) % len(highlight_pillars)] if highlight_pillars else profile.pillars[0]
        theme, notes = _select_theme(base_pillar, history_counts, used_themes)
        highlight_slug = _normalize_text(f"{month}-highlight-{idx}-{target}").replace(" ", "-")
        highlight_items.append(
            PlannedItem(
                item_id=f"{plan_project_id}-{highlight_slug}",
                date=dates[min(len(dates) - 1, (idx - 1) * 7)].isoformat(),
                format="story",
                category="highlight",
                pillar=base_pillar["name"],
                theme=theme,
                objective=base_pillar["objective"],
                cta=_derive_cta(base_pillar["objective"], "story"),
                evergreen=True,
                highlight_target=target,
                approval_state="draft",
                source_kind="highlight",
                status="planned",
                notes=tuple([*notes, f"highlight={target}"]),
            )
        )

    items.extend(highlight_items)
    items.sort(key=lambda item: (item.date, item.category, item.item_id))
    summary["planned_items"] = len(items)
    summary["post_count"] = sum(1 for item in items if item.category == "post")
    summary["story_count"] = sum(1 for item in items if item.category == "story")
    summary["highlight_count"] = sum(1 for item in items if item.category == "highlight")
    summary["watch_count"] = sum(1 for item in items if item.category == "watch")
    summary["evergreen_story_count"] = sum(1 for item in items if item.category in {"story", "highlight"} and item.evergreen)

    return MonthlyEditorialPlan(
        project_id=plan_project_id,
        project_name=spec.project_name or spec.title,
        project_spec_path=str(Path(project_spec_path).expanduser().resolve()),
        month=month,
        timezone=timezone,
        planner_profile_path=str(profile.path) if profile.path else None,
        summary=summary,
        history_summary=history_summary,
        items=tuple(items),
        skipped_watch_slots=tuple(skipped_watch_slots),
        created_at=datetime.utcnow().isoformat(timespec="seconds") + "Z",
    )


def build_production_queue(plan: MonthlyEditorialPlan | dict[str, Any], approved_item_ids: Sequence[str] | None = None) -> ProductionQueue:
    if isinstance(plan, dict):
        plan_items = [
            PlannedItem(
                item_id=str(item["item_id"]),
                date=str(item["date"]),
                format=str(item["format"]),
                category=str(item["category"]),
                pillar=str(item["pillar"]),
                theme=str(item["theme"]),
                objective=str(item["objective"]),
                cta=str(item["cta"]),
                evergreen=bool(item.get("evergreen", False)),
                highlight_target=item.get("highlight_target"),
                approval_state=str(item.get("approval_state") or "draft"),
                source_kind=str(item.get("source_kind") or "planner"),
                status=str(item.get("status") or "planned"),
                notes=tuple(str(note) for note in item.get("notes", []) if str(note).strip()),
            )
            for item in plan.get("items", [])
            if isinstance(item, dict)
        ]
        plan = MonthlyEditorialPlan(
            project_id=str(plan.get("project_id") or "unknown"),
            project_name=str(plan.get("project_name") or "Unknown"),
            project_spec_path=str(plan.get("project_spec_path") or ""),
            month=str(plan.get("month") or "unknown"),
            timezone=str(plan.get("timezone") or "America/Sao_Paulo"),
            planner_profile_path=plan.get("planner_profile_path"),
            summary=dict(plan.get("summary") or {}),
            history_summary=dict(plan.get("history_summary") or {}),
            items=tuple(plan_items),
            skipped_watch_slots=tuple(plan.get("skipped_watch_slots") or ()),
            created_at=str(plan.get("created_at") or ""),
        )
    approved_set = {str(item_id) for item_id in (approved_item_ids or ()) if str(item_id).strip()}
    queue_items: list[ProductionQueueItem] = []
    for item in plan.items:
        if approved_set and item.item_id not in approved_set:
            continue
        if not approved_set and item.approval_state != "approved":
            continue
        queue_items.append(
            ProductionQueueItem(
                queue_id=f"queue-{item.item_id}",
                source_item_id=item.item_id,
                project_id=plan.project_id,
                month=plan.month,
                date=item.date,
                format=item.format,
                category=item.category,
                pillar=item.pillar,
                theme=item.theme,
                objective=item.objective,
                cta=item.cta,
                evergreen=item.evergreen,
                highlight_target=item.highlight_target,
                status="queued",
            )
        )
    return ProductionQueue(
        project_id=plan.project_id,
        month=plan.month,
        approved_item_ids=tuple(sorted(approved_set)),
        items=tuple(queue_items),
    )


def read_json_source(source: str | Path | None) -> list[dict[str, Any]]:
    if source is None:
        return []
    text = str(source).strip()
    if not text:
        return []
    if text.startswith("[") or text.startswith("{"):
        payload = json.loads(text)
    else:
        path = Path(text).expanduser()
        payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        if isinstance(payload.get("items"), list):
            return [item for item in payload["items"] if isinstance(item, dict)]
        if isinstance(payload.get("schedule"), list):
            return [item for item in payload["schedule"] if isinstance(item, dict)]
    raise BootstrapValidationError("JSON source must be a list or an object containing an items list.")


def plan_month_to_dict(plan: MonthlyEditorialPlan) -> dict[str, Any]:
    return plan.to_dict()


def queue_to_dict(queue: ProductionQueue) -> dict[str, Any]:
    return queue.to_dict()
