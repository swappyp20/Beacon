import sqlite3
import time
from typing import Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS mentee (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  handle TEXT NOT NULL,           -- pseudonymous; NO real PII
  mentor TEXT NOT NULL,           -- Slack user id
  channel TEXT NOT NULL,          -- Slack channel id
  canvas_id TEXT,
  status TEXT NOT NULL DEFAULT 'active'
);
CREATE TABLE IF NOT EXISTS followup (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mentee_id INTEGER NOT NULL,
  raised_by TEXT NOT NULL,
  summary TEXT NOT NULL,
  severity TEXT NOT NULL,
  due_at TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_event (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  target TEXT NOT NULL,
  severity_before TEXT,
  severity_after TEXT,
  payload TEXT,
  ts REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS scorecard (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mentee_id INTEGER NOT NULL,
  generated_at REAL NOT NULL,
  generated_by TEXT NOT NULL,
  approved_by TEXT,
  canvas_version INTEGER NOT NULL DEFAULT 1
);
"""

class Store:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    @classmethod
    def open(cls, path: str) -> "Store":
        return cls(sqlite3.connect(path))

    def add_mentee(self, handle: str, mentor: str, channel: str, canvas_id: Optional[str] = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO mentee(handle, mentor, channel, canvas_id) VALUES (?,?,?,?)",
            (handle, mentor, channel, canvas_id),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_mentee(self, mentee_id: int) -> Optional[dict]:
        row = self.conn.execute("SELECT * FROM mentee WHERE id=?", (mentee_id,)).fetchone()
        return dict(row) if row else None

    def find_mentee_by_handle(self, handle: str) -> Optional[dict]:
        row = self.conn.execute("SELECT * FROM mentee WHERE handle=?", (handle,)).fetchone()
        return dict(row) if row else None

    def add_followup(self, mentee_id: int, raised_by: str, summary: str, severity: str, due_at: Optional[str]) -> int:
        cur = self.conn.execute(
            "INSERT INTO followup(mentee_id, raised_by, summary, severity, due_at, created_at) VALUES (?,?,?,?,?,?)",
            (mentee_id, raised_by, summary, severity, due_at, time.time()),
        )
        self.conn.commit()
        return cur.lastrowid

    def open_followups(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM followup WHERE status='open' ORDER BY created_at").fetchall()
        return [dict(r) for r in rows]

    def log_audit(self, actor: str, action: str, target: str, severity_before=None, severity_after=None, payload="{}") -> int:
        cur = self.conn.execute(
            "INSERT INTO audit_event(actor, action, target, severity_before, severity_after, payload, ts) VALUES (?,?,?,?,?,?,?)",
            (actor, action, target, severity_before, severity_after, payload, time.time()),
        )
        self.conn.commit()
        return cur.lastrowid

    def audit_for_target(self, target: str) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM audit_event WHERE target=? ORDER BY ts", (target,)).fetchall()
        return [dict(r) for r in rows]
