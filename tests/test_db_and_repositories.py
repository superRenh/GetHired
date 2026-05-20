from __future__ import annotations

from pathlib import Path

from gethired.db import connect_db, init_db
from gethired.repositories.job_postings_repo import list_job_postings, upsert_job_posting
from gethired.repositories.sync_state_repo import get_sync_state, upsert_sync_state


def test_init_db_creates_schema_tables(tmp_path: Path):
    db_path = tmp_path / "gethired.sqlite3"
    init_db(db_path)

    with connect_db(db_path) as connection:
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert "schema_version" in tables
    assert "sync_state" in tables
    assert "gmail_messages" in tables
    assert "parsed_jobs" in tables
    assert "job_postings" in tables
    assert "job_posting_sources" in tables


def test_sync_state_upsert_and_get(tmp_path: Path):
    db_path = tmp_path / "gethired.sqlite3"
    init_db(db_path)

    with connect_db(db_path) as connection:
        upsert_sync_state(
            connection,
            source_key="gmail:GetHired/Job Alerts",
            gmail_label_name="GetHired/Job Alerts",
            last_history_id="12345",
        )
        state = get_sync_state(connection, "gmail:GetHired/Job Alerts")

    assert state is not None
    assert state.last_history_id == "12345"
    assert state.gmail_label_name == "GetHired/Job Alerts"


def test_list_job_postings_supports_search_and_range_filters(tmp_path: Path):
    db_path = tmp_path / "gethired.sqlite3"
    init_db(db_path)

    with connect_db(db_path) as connection:
        upsert_job_posting(
            connection,
            canonical_key="key-berlin-1",
            title="Data Scientist",
            company="Example Berlin GmbH",
            location="Berlin, Germany",
            source="gmail",
            source_type="google_alert",
            url="https://example.com/job/1",
            detected_at="2026-05-20T10:00:00Z",
        )
        upsert_job_posting(
            connection,
            canonical_key="key-munich-1",
            title="ML Engineer",
            company="Munich AI AG",
            location="Munich, Germany",
            source="gmail",
            source_type="google_alert",
            url="https://example.com/job/2",
            detected_at="2026-05-18T08:00:00Z",
        )

        search_rows = list_job_postings(connection, search="berlin")
        range_rows = list_job_postings(
            connection,
            from_ts="2026-05-19T00:00:00Z",
            to_ts="2026-05-20T23:59:59Z",
        )

    assert len(search_rows) == 1
    assert search_rows[0].company == "Example Berlin GmbH"
    assert len(range_rows) == 1
    assert range_rows[0].location == "Berlin, Germany"


def test_list_job_postings_time_preset_uses_detected_at(tmp_path: Path):
    db_path = tmp_path / "gethired.sqlite3"
    init_db(db_path)

    with connect_db(db_path) as connection:
        connection.execute(
            """
            INSERT INTO job_postings(
              id, canonical_key, title, company, location, source, source_type, url,
              apply_url, posted_at, detected_at, description, raw_text, score,
              score_reason, status, created_at, updated_at
            ) VALUES(
              'id-old', 'key-old', 'Old Role', 'Old Co', 'Remote', 'gmail', 'google_alert',
              'https://example.com/old', '', NULL, datetime('now', '-9 day'),
              '', '', NULL, '', 'new', datetime('now'), datetime('now')
            )
            """
        )
        connection.execute(
            """
            INSERT INTO job_postings(
              id, canonical_key, title, company, location, source, source_type, url,
              apply_url, posted_at, detected_at, description, raw_text, score,
              score_reason, status, created_at, updated_at
            ) VALUES(
              'id-new', 'key-new', 'New Role', 'New Co', 'Berlin', 'gmail', 'google_alert',
              'https://example.com/new', '', NULL, datetime('now', '-1 day'),
              '', '', NULL, '', 'new', datetime('now'), datetime('now')
            )
            """
        )
        rows = list_job_postings(connection, time_preset="1w")

    assert len(rows) == 1
    assert rows[0].canonical_key == "key-new"
