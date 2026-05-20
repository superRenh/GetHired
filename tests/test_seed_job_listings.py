from __future__ import annotations

from pathlib import Path

from gethired.db import connect_db, init_db
from gethired.repositories.job_postings_repo import list_job_postings
from gethired.seed_job_listings import seed_job_listings


def test_seed_job_listings_inserts_fixture_rows(tmp_path: Path):
    fixture = tmp_path / "jobs.json"
    db_path = tmp_path / "gethired.sqlite3"
    fixture.write_text(
        """
        [
          {
            "title": "Data Scientist",
            "company": "Example GmbH",
            "location": "Berlin, Germany",
            "source": "Google Alerts",
            "url": "https://example.com/jobs/1",
            "date": "2026-05-20"
          }
        ]
        """,
        encoding="utf-8",
    )

    init_db(db_path)
    inserted = seed_job_listings(fixture, db_path)
    assert inserted == 1

    with connect_db(db_path) as connection:
        rows = list_job_postings(connection)

    assert len(rows) == 1
    assert rows[0].title == "Data Scientist"
    assert rows[0].company == "Example GmbH"
