"""SQLite-backed long-term memory store for student study profiles.

Implements U3-2: Long-term memory with namespace `(user_id, "profile")`,
persisted in SQLite so memories survive process restart.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "student_profiles.sqlite"


class SQLiteProfileStore:
    """Persistent key-value store partitioned by (user_id, namespace)."""

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_store (
                    user_id TEXT NOT NULL,
                    namespace TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, namespace, key)
                )
                """
            )
            conn.commit()

    def put(self, user_id: str, namespace: str, key: str, value: Any) -> None:
        """Store a JSON-serializable value under (user_id, namespace, key)."""
        value_json = json.dumps(value)
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO memory_store (user_id, namespace, key, value_json, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, namespace, key) DO UPDATE SET
                    value_json=excluded.value_json,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (user_id, namespace, key, value_json),
            )
            conn.commit()

    def get(self, user_id: str, namespace: str, key: str, default: Any = None) -> Any:
        """Retrieve a stored value for (user_id, namespace, key)."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT value_json FROM memory_store
                WHERE user_id = ? AND namespace = ? AND key = ?
                """,
                (user_id, namespace, key),
            )
            row = cursor.fetchone()
            if row is None:
                return default
            return json.loads(row["value_json"])

    def get_all(self, user_id: str, namespace: str = "profile") -> dict[str, Any]:
        """Retrieve all keys for a given user and namespace."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT key, value_json FROM memory_store
                WHERE user_id = ? AND namespace = ?
                """,
                (user_id, namespace),
            )
            rows = cursor.fetchall()
            return {row["key"]: json.loads(row["value_json"]) for row in rows}

    def delete(self, user_id: str, namespace: str, key: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                DELETE FROM memory_store
                WHERE user_id = ? AND namespace = ? AND key = ?
                """,
                (user_id, namespace, key),
            )
            conn.commit()


def get_student_profile(user_id: str, db_path: Path | str = DEFAULT_DB_PATH) -> dict[str, Any]:
    """Helper to fetch student profile dictionary from SQLite."""
    store = SQLiteProfileStore(db_path)
    profile = store.get_all(user_id, namespace="profile")
    if not profile:
        # Fallback institutional default profile
        return {
            "user_id": user_id,
            "name": "Standard Student",
            "daily_max_hours": 6.0,
            "pace_multiplier": 1.0,
            "fatigue_threshold": 5.0,
            "target_subject": "Computer Science AI Exam",
        }
    profile["user_id"] = user_id
    return profile
