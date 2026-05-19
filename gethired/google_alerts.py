"""Generate Google Alert queries from search profiles."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Iterable, Sequence

from gethired.search_profile import SearchProfile, load_search_profile

LOGGER = logging.getLogger(__name__)

DEFAULT_ATS_DOMAINS: tuple[str, ...] = (
    "boards.greenhouse.io",
    "jobs.lever.co",
    "jobs.personio.de",
    "jobs.smartrecruiters.com",
    "teamtailor.com",
)


def generate_google_alert_queries(
    profile: SearchProfile,
    *,
    ats_domains: Sequence[str] = DEFAULT_ATS_DOMAINS,
    include_priority_keywords: bool = False,
    max_queries: int = 50,
) -> list[str]:
    """Generate conservative Google Alert queries for manual Google Alerts setup."""
    if max_queries < 1:
        raise ValueError("max_queries must be at least 1")

    queries: list[str] = []

    for domain in _clean_items(ats_domains):
        for title in profile.job_titles:
            for location in profile.locations:
                queries.append(_build_query(domain, title, location))

        if include_priority_keywords:
            for keyword in profile.priority_keywords:
                for location in profile.locations:
                    queries.append(_build_query(domain, keyword, location))

    deduped_queries = _dedupe_preserving_order(queries)
    limited_queries = deduped_queries[:max_queries]

    if len(deduped_queries) > max_queries:
        LOGGER.warning(
            "Google Alert query generation reached max_queries=%s and skipped %s queries",
            max_queries,
            len(deduped_queries) - max_queries,
        )

    LOGGER.info("Generated %s Google Alert queries", len(limited_queries))
    return limited_queries


def _build_query(domain: str, phrase: str, location: str) -> str:
    return f'site:{domain} "{phrase}" {location}'


def _clean_items(items: Iterable[str]) -> list[str]:
    return [item.strip() for item in items if item and item.strip()]


def _dedupe_preserving_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []

    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)

    return deduped


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate Google Alert queries from a Search Profile JSON file."
    )
    parser.add_argument("profile_path", help="Path to a Search Profile JSON file.")
    parser.add_argument(
        "--include-priority-keywords",
        action="store_true",
        help="Also generate selected priority keyword queries.",
    )
    parser.add_argument(
        "--max-queries",
        type=int,
        default=50,
        help="Maximum number of queries to output. Defaults to 50.",
    )

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    try:
        profile = load_search_profile(args.profile_path)
        queries = generate_google_alert_queries(
            profile,
            include_priority_keywords=args.include_priority_keywords,
            max_queries=args.max_queries,
        )
    except (FileNotFoundError, ValueError) as exc:
        LOGGER.error("Could not generate Google Alert queries: %s", exc)
        return 1

    sys.stdout.write("\n".join(queries))
    if queries:
        sys.stdout.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
