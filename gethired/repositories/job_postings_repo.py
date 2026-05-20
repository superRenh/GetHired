"""Repository for canonical job postings and listing filters."""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class JobPosting:
    id: str
    canonical_key: str
    title: str
    company: str
    location: str
    source: str
    source_type: str
    url: str
    apply_url: str
    posted_at: str | None
    detected_at: str
    description: str
    raw_text: str
    score: float | None
    score_reason: str
    status: str
    created_at: str
    updated_at: str


def upsert_job_posting(
    connection: sqlite3.Connection,
    *,
    canonical_key: str,
    title: str,
    company: str,
    location: str,
    source: str,
    source_type: str,
    url: str,
    apply_url: str = "",
    posted_at: str | None = None,
    detected_at: str,
    description: str = "",
    raw_text: str = "",
    score: float | None = None,
    score_reason: str = "",
    status: str = "new",
) -> None:
    connection.execute(
        """
        INSERT INTO job_postings(
          id,
          canonical_key,
          title,
          company,
          location,
          source,
          source_type,
          url,
          apply_url,
          posted_at,
          detected_at,
          description,
          raw_text,
          score,
          score_reason,
          status,
          created_at,
          updated_at
        ) VALUES(
          :id,
          :canonical_key,
          :title,
          :company,
          :location,
          :source,
          :source_type,
          :url,
          :apply_url,
          :posted_at,
          :detected_at,
          :description,
          :raw_text,
          :score,
          :score_reason,
          :status,
          datetime('now'),
          datetime('now')
        )
        ON CONFLICT(canonical_key) DO UPDATE SET
          title = excluded.title,
          company = excluded.company,
          location = excluded.location,
          source = excluded.source,
          source_type = excluded.source_type,
          url = excluded.url,
          apply_url = excluded.apply_url,
          posted_at = excluded.posted_at,
          detected_at = excluded.detected_at,
          description = excluded.description,
          raw_text = excluded.raw_text,
          score = excluded.score,
          score_reason = excluded.score_reason,
          status = excluded.status,
          updated_at = datetime('now')
        """,
        {
            "id": str(uuid.uuid4()),
            "canonical_key": canonical_key,
            "title": title,
            "company": company,
            "location": location,
            "source": source,
            "source_type": source_type,
            "url": url,
            "apply_url": apply_url,
            "posted_at": posted_at,
            "detected_at": detected_at,
            "description": description,
            "raw_text": raw_text,
            "score": score,
            "score_reason": score_reason,
            "status": status,
        },
    )


def list_job_postings(
    connection: sqlite3.Connection,
    *,
    time_preset: str | None = None,
    from_ts: str | None = None,
    to_ts: str | None = None,
    search: str | None = None,
    limit: int = 200,
) -> list[JobPosting]:
    where_clauses = []
    params: dict[str, object] = {"limit": limit}

    cutoff = _preset_cutoff(time_preset)
    if cutoff is not None:
        where_clauses.append("detected_at >= datetime('now', :cutoff)")
        params["cutoff"] = cutoff

    if from_ts:
        where_clauses.append("detected_at >= :from_ts")
        params["from_ts"] = from_ts
    if to_ts:
        where_clauses.append("detected_at <= :to_ts")
        params["to_ts"] = to_ts

    if search and search.strip():
        where_clauses.append(
            "(lower(title) LIKE :search OR lower(company) LIKE :search OR lower(location) LIKE :search)"
        )
        params["search"] = f"%{search.strip().lower()}%"

    sql = "SELECT * FROM job_postings"
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    sql += " ORDER BY detected_at DESC LIMIT :limit"

    rows = connection.execute(sql, params).fetchall()
    return [_row_to_job_posting(row) for row in rows]


def _preset_cutoff(time_preset: str | None) -> str | None:
    if time_preset == "1d":
        return "-1 day"
    if time_preset == "3d":
        return "-3 day"
    if time_preset == "1w":
        return "-7 day"
    return None


def _row_to_job_posting(row: sqlite3.Row) -> JobPosting:
    return JobPosting(
        id=row["id"],
        canonical_key=row["canonical_key"],
        title=row["title"] or "",
        company=row["company"] or "",
        location=row["location"] or "",
        source=row["source"] or "",
        source_type=row["source_type"] or "",
        url=row["url"] or "",
        apply_url=row["apply_url"] or "",
        posted_at=row["posted_at"],
        detected_at=row["detected_at"],
        description=row["description"] or "",
        raw_text=row["raw_text"] or "",
        score=row["score"],
        score_reason=row["score_reason"] or "",
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
