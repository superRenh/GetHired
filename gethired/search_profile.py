"""Search Profile config model and loading helpers."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SearchProfile:
    """Configuration for one job discovery search profile."""

    profile_name: str
    job_titles: tuple[str, ...]
    keywords: tuple[str, ...] = field(default_factory=tuple)
    priority_keywords: tuple[str, ...] = field(default_factory=tuple)
    locations: tuple[str, ...] = field(default_factory=tuple)
    exclude_keywords: tuple[str, ...] = field(default_factory=tuple)
    enabled_email_sources: tuple[str, ...] = field(default_factory=tuple)
    google_alert_queries: tuple[str, ...] = field(default_factory=tuple)
    scan_frequency_minutes: int = 30
    notification_score_threshold: int = 70

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SearchProfile":
        profile = cls(
            profile_name=_required_string(data, "profile_name"),
            job_titles=_string_tuple(data, "job_titles"),
            keywords=_string_tuple(data, "keywords"),
            priority_keywords=_string_tuple(data, "priority_keywords"),
            locations=_string_tuple(data, "locations"),
            exclude_keywords=_string_tuple(data, "exclude_keywords"),
            enabled_email_sources=_string_tuple(data, "enabled_email_sources"),
            google_alert_queries=_string_tuple(data, "google_alert_queries"),
            scan_frequency_minutes=_integer(
                data,
                "scan_frequency_minutes",
                default=30,
                minimum=1,
            ),
            notification_score_threshold=_integer(
                data,
                "notification_score_threshold",
                default=70,
                minimum=0,
            ),
        )
        profile.validate()
        return profile

    def validate(self) -> None:
        if not self.job_titles:
            raise ValueError("Search Profile must include at least one job title")
        if not self.locations:
            raise ValueError("Search Profile must include at least one location")
        if self.notification_score_threshold > 100:
            raise ValueError("notification_score_threshold must be between 0 and 100")


def load_search_profile(path: str | Path) -> SearchProfile:
    """Load a Search Profile from a JSON file."""
    profile_path = Path(path)
    with profile_path.open("r", encoding="utf-8") as profile_file:
        data = json.load(profile_file)

    if not isinstance(data, dict):
        raise ValueError("Search Profile JSON must contain an object")

    profile = SearchProfile.from_dict(data)
    LOGGER.info("Search profile loaded: %s", profile.profile_name)
    return profile


def _required_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _string_tuple(data: dict[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key, [])
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list of strings")

    items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{key} must be a list of strings")
        cleaned = item.strip()
        if cleaned:
            items.append(cleaned)

    return tuple(items)


def _integer(
    data: dict[str, Any],
    key: str,
    *,
    default: int,
    minimum: int,
) -> int:
    value = data.get(key, default)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    if value < minimum:
        raise ValueError(f"{key} must be at least {minimum}")
    return value
