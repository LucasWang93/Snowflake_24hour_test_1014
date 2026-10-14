"""Strict, bounded agent contracts and explicit conversation state."""

from __future__ import annotations

import threading
import time
from dataclasses import asdict, dataclass, field
from typing import Any


class AgentIssue(ValueError):
    def __init__(self, message: str, status: str = "clarification"):
        super().__init__(message)
        self.status = status


class ServiceIssue(RuntimeError):
    def __init__(self, stage: str, detail: dict[str, Any] | None = None):
        super().__init__(
            f"The {stage} service could not complete this request. Please retry later."
        )
        self.stage = stage
        self.detail = detail or {}


@dataclass(frozen=True)
class Deadline:
    started: float = field(default_factory=time.monotonic)
    budget: float = 55.0

    def check(self) -> None:
        if time.monotonic() >= self.started + self.budget:
            raise ServiceIssue("request timeout")

    def timeout(self, cap: int = 15) -> int:
        self.check()
        remaining = self.budget - (time.monotonic() - self.started)
        if remaining < 1:
            raise ServiceIssue("request timeout")
        return max(1, min(cap, int(remaining)))


@dataclass(frozen=True)
class GeoRequest:
    type: str
    name: str
    state: str | None = None


@dataclass(frozen=True)
class Intent:
    metric: str | None = None
    kind: str | None = None
    year: int | None = None
    product: str | None = None
    geographies: tuple[GeoRequest, ...] = ()
    compare: bool | None = None
    aggregation: str | None = None
    filters: tuple[tuple[str, str], ...] = ()
    domain: str = "census"

    @classmethod
    def parse(cls, value: Any) -> Intent:
        required = {
            "metric",
            "kind",
            "year",
            "product",
            "geographies",
            "compare",
            "aggregation",
            "filters",
            "domain",
        }
        if not isinstance(value, dict) or set(value) != required:
            raise AgentIssue(
                "I could not safely interpret the request. Please specify the metric, year and geography."
            )
        if value["domain"] not in {"census", "off_topic", "inappropriate"}:
            raise AgentIssue("Invalid request classification.")
        if value["kind"] not in {None, "count", "median", "mean", "ratio", "moe", "unknown"}:
            raise AgentIssue("Unsupported statistical definition. Please clarify the statistic.")
        if value["product"] not in {None, "acs", "decennial"}:
            raise AgentIssue("Please choose ACS estimates or 2020 decennial redistricting counts.")
        if value["aggregation"] not in {None, "auto", "sum", "value"}:
            raise AgentIssue("This aggregation is unsupported.", "unsupported")
        if value["compare"] is not None and not isinstance(value["compare"], bool):
            raise AgentIssue("Invalid comparison request.")
        year = value["year"]
        if year is not None and (isinstance(year, bool) or not isinstance(year, int)):
            raise AgentIssue("Please specify an integer release year.")
        metric = value["metric"]
        if metric is not None and (not isinstance(metric, str) or not 1 <= len(metric) <= 200):
            raise AgentIssue("Please specify a short Census metric.")
        geos = value["geographies"]
        if not isinstance(geos, list) or len(geos) > 2:
            raise AgentIssue("At most two explicitly identified geographies are supported.")
        parsed = []
        for geo in geos:
            if not isinstance(geo, dict) or set(geo) != {"type", "name", "state"}:
                raise AgentIssue("Please identify the geography explicitly.")
            if geo["type"] not in {"cbg", "county", "state"}:
                raise AgentIssue(
                    "Only Census block groups, counties and states are supported; not cities/places.",
                    "unsupported",
                )
            if not isinstance(geo["name"], str) or not 1 <= len(geo["name"]) <= 120:
                raise AgentIssue("Invalid geography name.")
            if geo["state"] is not None and (
                not isinstance(geo["state"], str) or len(geo["state"]) > 80
            ):
                raise AgentIssue("Invalid state name.")
            parsed.append(GeoRequest(**geo))
        filters = value["filters"]
        if filters == []:
            filters = {}  # Empty-array model output has exactly the same empty meaning.
        if not isinstance(filters, dict) or len(filters) > 5:
            raise AgentIssue("Too many or invalid statistical filters.")
        filters = dict(filters)
        if "ownership" in filters:
            if "tenure" in filters and filters["tenure"] != filters["ownership"]:
                raise AgentIssue("Conflicting tenure filters.")
            filters["tenure"] = filters.pop("ownership")
        allowed = {"sex", "age", "race", "education", "employment", "income_band", "tenure"}
        if any(
            k not in allowed or not isinstance(v, str) or not 1 <= len(v) <= 100
            for k, v in filters.items()
        ):
            raise AgentIssue("These filters are not supported.", "unsupported")
        return cls(
            metric,
            value["kind"],
            year,
            value["product"],
            tuple(parsed),
            value["compare"],
            value["aggregation"],
            tuple(sorted(filters.items())),
            value["domain"],
        )


@dataclass
class ConversationState:
    resolved: Intent | None = None
    pending: Intent | None = None
    entry_id: str | None = None
    _lock: Any = field(default_factory=threading.Lock, repr=False, compare=False)

    def reset(self) -> None:
        if not self._lock.acquire(blocking=False):
            raise AgentIssue("Conversation has a request in progress.", "overloaded")
        try:
            self.resolved = self.pending = None
            self.entry_id = None
        finally:
            self._lock.release()

    def context(self) -> dict[str, Any]:
        def serialize(intent: Intent | None) -> dict[str, Any] | None:
            if intent is None:
                return None
            value = asdict(intent)
            value["filters"] = dict(intent.filters)  # Match the model's object contract.
            return value

        return {
            "resolved": serialize(self.resolved),
            "pending": serialize(self.pending),
            "entry_id": self.entry_id,
        }


@dataclass
class Response:
    status: str
    answer: str
    latency_seconds: float
    intent: dict[str, Any] | None = None
    metric: dict[str, Any] | None = None
    results: list[dict[str, Any]] = field(default_factory=list)
    sql: list[dict[str, Any]] = field(default_factory=list)
    model_calls: list[dict[str, Any]] = field(default_factory=list)
    stages: dict[str, float] = field(default_factory=dict)
    cleanup: dict[str, Any] | None = None
    error: dict[str, Any] | None = None

    def public_dict(self) -> dict[str, Any]:
        """Browser-safe surface: no raw errors, prompts, SQL or permission snapshots."""
        return {
            "status": self.status,
            "answer": self.answer,
            "latency_seconds": self.latency_seconds,
            "metric": self.metric,
            "results": self.results,
            "warehouse_suspended": bool(self.cleanup and self.cleanup.get("confirmed_suspended")),
        }

    def as_dict(self) -> dict[str, Any]:
        """Trusted local diagnostics; never use this as a public endpoint response."""
        return asdict(self)
