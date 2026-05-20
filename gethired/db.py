"""SQLite bootstrap and connection helpers for GetHired."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path("data/gethired.sqlite3")
DEFAULT_SCHEMA_PATH = Path("db/schema.sql")
SCHEMA_VERSION = 1


def connect_db(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(
    db_path: str | Path = DEFAULT_DB_PATH,
    schema_path: str | Path = DEFAULT_SCHEMA_PATH,
) -> None:
    schema = Path(schema_path).read_text(encoding="utf-8")
    with connect_db(db_path) as connection:
        connection.executescript(schema)
        connection.execute(
            "INSERT OR IGNORE INTO schema_version(version, applied_at) VALUES (?, datetime('now'))",
            (SCHEMA_VERSION,),
        )
