"""Repository for Gmail sync cursor state."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class SyncState:
    source_key: str
    gmail_user_id: str
    gmail_label_name: str
    gmail_label_id: str | None
    last_history_id: str
    last_synced_at: str
    created_at: str
    updated_at: str


def get_sync_state(connection: sqlite3.Connection, source_key: str) -> SyncState | None:
    row = connection.execute(
        "SELECT * FROM sync_state WHERE source_key = ?",
        (source_key,),
    ).fetchone()
    if row is None:
        return None
    return SyncState(
        source_key=row["source_key"],
        gmail_user_id=row["gmail_user_id"],
        gmail_label_name=row["gmail_label_name"],
        gmail_label_id=row["gmail_label_id"],
        last_history_id=row["last_history_id"],
        last_synced_at=row["last_synced_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def upsert_sync_state(
    connection: sqlite3.Connection,
    *,
    source_key: str,
    gmail_label_name: str,
    last_history_id: str,
    gmail_user_id: str = "me",
    gmail_label_id: str | None = None,
) -> None:
    connection.execute(
        """
        INSERT INTO sync_state(
          source_key,
          gmail_user_id,
          gmail_label_name,
          gmail_label_id,
          last_history_id,
          last_synced_at,
          created_at,
          updated_at
        ) VALUES(
          :source_key,
          :gmail_user_id,
          :gmail_label_name,
          :gmail_label_id,
          :last_history_id,
          datetime('now'),
          datetime('now'),
          datetime('now')
        )
        ON CONFLICT(source_key) DO UPDATE SET
          gmail_user_id = excluded.gmail_user_id,
          gmail_label_name = excluded.gmail_label_name,
          gmail_label_id = excluded.gmail_label_id,
          last_history_id = excluded.last_history_id,
          last_synced_at = datetime('now'),
          updated_at = datetime('now')
        """,
        {
            "source_key": source_key,
            "gmail_user_id": gmail_user_id,
            "gmail_label_name": gmail_label_name,
            "gmail_label_id": gmail_label_id,
            "last_history_id": last_history_id,
        },
    )
