"""Seed local SQLite job postings from a fixture JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from gethired.db import DEFAULT_DB_PATH, init_db, connect_db
from gethired.repositories.job_postings_repo import upsert_job_posting

DEFAULT_FIXTURE_PATH = Path("fixtures/job_listings.example.json")


def seed_job_listings(
    fixture_path: str | Path = DEFAULT_FIXTURE_PATH,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> int:
    fixture = Path(fixture_path)
    data = json.loads(fixture.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Fixture must contain a list of objects")

    init_db(db_path)
    inserted = 0
    with connect_db(db_path) as connection:
        for item in data:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            company = str(item.get("company", "")).strip()
            location = str(item.get("location", "")).strip()
            url = str(item.get("url", "")).strip()
            source = str(item.get("source", "fixture")).strip() or "fixture"
            description = str(item.get("summary", "")).strip()
            raw_text = str(item.get("description", "")).strip()
            detected_day = str(item.get("date", "")).strip() or "2026-01-01"
            detected_at = f"{detected_day}T00:00:00Z"
            canonical_key = "|".join([title.lower(), company.lower(), location.lower(), url])
            upsert_job_posting(
                connection,
                canonical_key=canonical_key,
                title=title,
                company=company,
                location=location,
                source=source,
                source_type="fixture_seed",
                url=url,
                posted_at=detected_day,
                detected_at=detected_at,
                description=description,
                raw_text=raw_text,
            )
            inserted += 1
    return inserted


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed GetHired SQLite job postings.")
    parser.add_argument(
        "--fixture-path",
        default=str(DEFAULT_FIXTURE_PATH),
        help="Path to fixture JSON.",
    )
    parser.add_argument(
        "--db-path",
        default=str(DEFAULT_DB_PATH),
        help="Path to SQLite database.",
    )
    args = parser.parse_args()

    inserted = seed_job_listings(args.fixture_path, args.db_path)
    print(f"Seeded {inserted} job rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
