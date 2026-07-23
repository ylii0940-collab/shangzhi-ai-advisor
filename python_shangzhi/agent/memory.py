"""SQLite 持久化：对话记忆、行动确认、Agent Trace 与评测结果。"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class MemoryStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._lock = threading.Lock()
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    merchant_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_messages_thread
                    ON messages(thread_id, created_at);

                CREATE TABLE IF NOT EXISTS actions (
                    id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    merchant_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS traces (
                    id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    event TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS eval_runs (
                    id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    passed INTEGER NOT NULL,
                    score REAL NOT NULL,
                    details TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                );
                """
            )

    def add_message(
        self,
        thread_id: str,
        merchant_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        with self._lock, self._connection() as connection:
            connection.execute(
                "INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    message_id,
                    thread_id,
                    merchant_id,
                    role,
                    content,
                    json.dumps(metadata or {}, ensure_ascii=False),
                    time.time_ns(),
                ),
            )
        return message_id

    def history(self, thread_id: str, limit: int = 20) -> list[dict[str, str]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT role, content FROM messages
                WHERE thread_id = ?
                ORDER BY created_at DESC LIMIT ?
                """,
                (thread_id, limit),
            ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def create_action(
        self,
        thread_id: str,
        merchant_id: str,
        title: str,
        action_type: str,
        risk_level: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        action_id = f"act_{uuid.uuid4().hex[:12]}"
        now = time.time_ns()
        with self._lock, self._connection() as connection:
            connection.execute(
                "INSERT INTO actions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    action_id,
                    thread_id,
                    merchant_id,
                    title,
                    action_type,
                    risk_level,
                    json.dumps(payload, ensure_ascii=False),
                    "pending",
                    now,
                    now,
                ),
            )
        return self.get_action(action_id) or {}

    def get_action(self, action_id: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM actions WHERE id = ?", (action_id,)
            ).fetchone()
        if not row:
            return None
        item = dict(row)
        item["payload"] = json.loads(item["payload"])
        return item

    def update_action(self, action_id: str, approved: bool) -> dict[str, Any] | None:
        status = "executed" if approved else "rejected"
        with self._lock, self._connection() as connection:
            connection.execute(
                "UPDATE actions SET status = ?, updated_at = ? WHERE id = ? AND status = 'pending'",
                (status, time.time_ns(), action_id),
            )
        return self.get_action(action_id)

    def add_trace(self, thread_id: str, event: str, payload: dict[str, Any]) -> None:
        with self._lock, self._connection() as connection:
            connection.execute(
                "INSERT INTO traces VALUES (?, ?, ?, ?, ?)",
                (
                    f"trace_{uuid.uuid4().hex[:12]}",
                    thread_id,
                    event,
                    json.dumps(payload, ensure_ascii=False),
                    time.time_ns(),
                ),
            )

    def traces(self, thread_id: str, limit: int = 50) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT event, payload, created_at FROM traces
                WHERE thread_id = ?
                ORDER BY created_at DESC LIMIT ?
                """,
                (thread_id, limit),
            ).fetchall()
        result = []
        for row in reversed(rows):
            result.append(
                {
                    "event": row["event"],
                    "payload": json.loads(row["payload"]),
                    "created_at": row["created_at"],
                }
            )
        return result

    def save_eval(self, case_id: str, passed: bool, score: float, details: dict) -> None:
        with self._lock, self._connection() as connection:
            connection.execute(
                "INSERT INTO eval_runs VALUES (?, ?, ?, ?, ?, ?)",
                (
                    f"eval_{uuid.uuid4().hex[:12]}",
                    case_id,
                    int(passed),
                    score,
                    json.dumps(details, ensure_ascii=False),
                    time.time_ns(),
                ),
            )

    def eval_summary(self) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total,
                       COALESCE(SUM(passed), 0) AS passed,
                       COALESCE(AVG(score), 0) AS average_score
                FROM eval_runs
                """
            ).fetchone()
        total = int(row["total"])
        passed = int(row["passed"])
        return {
            "total": total,
            "passed": passed,
            "pass_rate": round(passed / total, 4) if total else 0,
            "average_score": round(float(row["average_score"]), 2),
        }
