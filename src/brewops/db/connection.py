"""SQLite connection handling (stdlib sqlite3, no ORM)."""

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_FILENAME = "brewops.db"


def db_path() -> Path:
    """Database file location: $BREWOPS_DB if set, else ./brewops.db."""
    return Path(os.environ.get("BREWOPS_DB", DEFAULT_DB_FILENAME))


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(path if path is not None else db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
