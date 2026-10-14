"""Fail-closed authentication and atomic single-host session/admission budgets."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator, Protocol


class ControlIssue(ValueError):
    def __init__(self, status: str, message: str):
        super().__init__(message)
        self.status = status


class Authenticator(Protocol):
    def verify(self, token: str) -> str: ...


class BearerAuthenticator:
    """Inject server-held SHA256 digests of high-entropy bearer tokens, never plaintext."""

    def __init__(self, digests: dict[str, str]):
        if not 1 <= len(digests) <= 32 or any(
            len(d) != 64
            or any(c not in "0123456789abcdef" for c in d)
            or not isinstance(p, str)
            or not 1 <= len(p) <= 80
            for d, p in digests.items()
        ):
            raise ValueError("Provide bounded token digests and principal identifiers")
        self._digests = dict(digests)

    def verify(self, token: str) -> str:
        if not isinstance(token, str) or not 32 <= len(token) <= 256:
            raise ControlIssue("unauthorized", "Authentication is required.")
        digest = hashlib.sha256(token.encode()).hexdigest()
        principal = None
        for expected, owner in self._digests.items():
            if hmac.compare_digest(digest, expected):
                principal = owner
        if principal is None:
            raise ControlIssue("unauthorized", "Authentication is required.")
        return principal


@dataclass(frozen=True)
class Limits:
    principal_requests_per_minute: int = 6
    global_requests_per_minute: int = 20
    model_calls_per_day: int = 120
    max_sessions: int = 128
    session_ttl: float = 1800
    deadline_seconds: float = 55

    def __post_init__(self):
        if (
            any(
                isinstance(x, bool) or not isinstance(x, int) or x < 1
                for x in (
                    self.principal_requests_per_minute,
                    self.global_requests_per_minute,
                    self.model_calls_per_day,
                    self.max_sessions,
                )
            )
            or not 0.1 <= self.deadline_seconds <= 55
            or not 1 <= self.session_ttl <= 86400
        ):
            raise ValueError("Invalid bounded runtime limits")


class SQLiteControl:
    """One atomic trial-warehouse lease across processes; no unsafe concurrent suspend.

    All deployment workers must use this SAME local file. Multi-host deployments
    require an implementation of the same control contract on a transactional store.
    Admission reserves two Cortex-call units, conservatively without refunds.
    """

    def __init__(self, path: Path, limits: Limits = Limits()):
        self.path, self.limits = Path(path), limits
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
        except FileExistsError:
            pass
        if self.path.is_symlink() or not self.path.is_file() or self.path.stat().st_mode & 0o077:
            raise ValueError("Control store must be a regular owner-only file")
        with self._transaction() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS policy (id INTEGER PRIMARY KEY, value TEXT NOT NULL)"
            )
            policy = json.dumps(asdict(limits), sort_keys=True)
            db.execute("INSERT OR IGNORE INTO policy VALUES (1, ?)", (policy,))
            if db.execute("SELECT value FROM policy WHERE id=1").fetchone()[0] != policy:
                raise ValueError("Shared control limits must match across all workers")
            db.execute(
                "CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, owner TEXT NOT NULL, state TEXT NOT NULL, touched REAL NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS events (owner TEXT NOT NULL, at REAL NOT NULL, calls INTEGER NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS gate (id INTEGER PRIMARY KEY CHECK(id=1), lease TEXT, session TEXT, expires REAL, quarantined INTEGER NOT NULL)"
            )
            db.execute("INSERT OR IGNORE INTO gate VALUES (1, NULL, NULL, NULL, 0)")

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path, timeout=0.2, isolation_level=None)
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def create_session(self, owner: str) -> str:
        now = time.time()
        with self._transaction() as db:
            db.execute(
                "DELETE FROM sessions WHERE touched < ? AND id != COALESCE((SELECT session FROM gate WHERE id=1), '')",
                (now - self.limits.session_ttl,),
            )
            if (
                db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
                >= self.limits.max_sessions
            ):
                raise ControlIssue("overloaded", "Session capacity reached; retry later.")
            session = uuid.uuid4().hex
            db.execute("INSERT INTO sessions VALUES (?, ?, '{}', ?)", (session, owner, now))
            return session

    def begin(self, owner: str, session: str, request: str) -> dict:
        now = time.time()
        if not isinstance(session, str) or len(session) != 32:
            raise ControlIssue("unauthorized", "Conversation is unavailable.")
        with self._transaction() as db:
            row = db.execute(
                "SELECT owner, state, touched FROM sessions WHERE id=?", (session,)
            ).fetchone()
            if not row or row[0] != owner or now - row[2] > self.limits.session_ttl:
                raise ControlIssue("unauthorized", "Conversation is unavailable.")
            lease, expires, quarantined = db.execute(
                "SELECT lease, expires, quarantined FROM gate WHERE id=1"
            ).fetchone()
            if quarantined or (lease and expires < now):
                # Never auto-admit after a lost worker: its server query may remain active.
                raise ControlIssue(
                    "unavailable", "Data service requires operator recovery; retry later."
                )
            if lease:
                raise ControlIssue("overloaded", "Data service is busy; retry shortly.")
            db.execute("DELETE FROM events WHERE at < ?", (now - 86400,))
            count = db.execute(
                "SELECT COUNT(*) FROM events WHERE owner=? AND at> ?", (owner, now - 60)
            ).fetchone()[0]
            global_count = db.execute(
                "SELECT COUNT(*) FROM events WHERE at> ?", (now - 60,)
            ).fetchone()[0]
            used = db.execute("SELECT COALESCE(SUM(calls), 0) FROM events").fetchone()[0]
            if (
                count >= self.limits.principal_requests_per_minute
                or global_count >= self.limits.global_requests_per_minute
            ):
                raise ControlIssue(
                    "rate_limited", "Request rate limit reached; retry after one minute."
                )
            if used + 2 > self.limits.model_calls_per_day:
                raise ControlIssue(
                    "budget_exhausted", "Shared model-call budget exhausted; retry later."
                )
            db.execute("INSERT INTO events VALUES (?, ?, 2)", (owner, now))
            db.execute(
                "UPDATE gate SET lease=?, session=?, expires=? WHERE id=1",
                (request, session, now + 90),
            )
            return json.loads(row[1])

    def finish(self, request: str, state: dict | None, *, healthy: bool) -> None:
        with self._transaction() as db:
            row = db.execute(
                "SELECT session FROM gate WHERE id=1 AND lease=?", (request,)
            ).fetchone()
            if row is None:
                raise ControlIssue("unavailable", "Request lease is unavailable.")
            if healthy and state is not None:
                db.execute(
                    "UPDATE sessions SET state=?, touched=? WHERE id=?",
                    (json.dumps(state), time.time(), row[0]),
                )
            db.execute(
                "UPDATE gate SET lease=NULL, session=NULL, expires=NULL, quarantined=? WHERE id=1",
                (int(not healthy),),
            )

    def reset(self, owner: str, session: str) -> None:
        with self._transaction() as db:
            if db.execute("SELECT 1 FROM gate WHERE session=?", (session,)).fetchone():
                raise ControlIssue("overloaded", "Conversation has a request in progress.")
            result = db.execute(
                "UPDATE sessions SET state='{}', touched=? WHERE id=? AND owner=? AND touched>=?",
                (time.time(), session, owner, time.time() - self.limits.session_ttl),
            )
            if not result.rowcount:
                raise ControlIssue("unauthorized", "Conversation is unavailable.")

    def recover_after_operator_check(
        self, *, warehouse_suspended: bool, no_active_server_queries: bool
    ) -> None:
        """Trusted operator only: independently confirm both facts before calling.

        No public service method exposes this. Never infer server cancellation from
        killing a client process. A current lease must finish before recovery.
        """
        if warehouse_suspended is not True or no_active_server_queries is not True:
            raise ValueError("Operator must verify suspension and no active server queries")
        with self._transaction() as db:
            lease, expires = db.execute("SELECT lease, expires FROM gate WHERE id=1").fetchone()
            if lease and expires >= time.time():
                raise ControlIssue("overloaded", "An active request must finish before recovery.")
            db.execute(
                "UPDATE gate SET lease=NULL, session=NULL, expires=NULL, quarantined=0 WHERE id=1"
            )
