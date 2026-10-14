"""Frozen evaluation via production service and independent developer-written SQL.

Opt-in: RUN_PHASE3_LIVE=1 python -m evaluation.phase3 --output RUN/results.json
Never changes frozen cases; saves every outcome before checking acceptance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import secrets
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from census_agent.backend import SnowflakeBackend
from census_agent.control import BearerAuthenticator, Limits, SQLiteControl
from census_agent.service import AgentService
from census_agent.types import Deadline
from census_catalog.catalog import Catalog
from scripts.snowflake_probe import ROOT, quote_identifier


def run(output: Path) -> int:
    if os.environ.get("RUN_PHASE3_LIVE") != "1":
        raise SystemExit("Phase 3 real evaluation disabled; explicitly set RUN_PHASE3_LIVE=1")
    if output.exists():
        raise SystemExit("Use a new output path; existing evidence must be preserved")
    specification = ROOT / "evaluation/phase3_cases.json"
    cases = json.loads(specification.read_text())
    catalog = Catalog.load(ROOT / "data/semantic_catalog.json")
    evidence = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "case_sha256": hashlib.sha256(specification.read_bytes()).hexdigest(),
        "references": {},
        "outcomes": [],
        "permission_audits": [],
    }
    reference = SnowflakeBackend(catalog)

    def save():
        output.write_text(json.dumps(evidence, indent=2, default=str) + "\n")

    def expected(case):
        key = case["golden_id"] + ":" + case["scope"]
        if key not in evidence["references"]:
            field = catalog.mapping(case["golden_id"])
            qualified = ".".join(
                quote_identifier(x)
                for x in (catalog.data["database"], catalog.data["schema"], field["table"])
            )
            column = quote_identifier(field["column"])
            scope = case["scope"]
            if len(scope) == 12:
                sql = f'SELECT {column} FROM {qualified} WHERE "CENSUS_BLOCK_GROUP"=%s LIMIT 2'
                params = (scope,)
            else:
                sql = f'SELECT SUM({column}) FROM {qualified} WHERE "CENSUS_BLOCK_GROUP" LIKE %s'
                params = (scope + "%",)
            reference.connect(Deadline(budget=30))
            result = reference._run(sql, params, 15, 2)
            assert len(result["rows"]) == 1 and result["rows"][0][0] is not None
            evidence["references"][key] = {"sql": sql, "params": params, **result}
            reference.suspend()
            save()
        return float(evidence["references"][key]["rows"][0][0])

    token_a, token_b = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    auth = BearerAuthenticator(
        {
            hashlib.sha256(token_a.encode()).hexdigest(): "evaluator-a",
            hashlib.sha256(token_b.encode()).hexdigest(): "evaluator-b",
        }
    )
    with tempfile.TemporaryDirectory(prefix="phase3-eval-") as work:
        control = SQLiteControl(
            Path(work) / "control.sqlite",
            Limits(
                principal_requests_per_minute=60,
                global_requests_per_minute=60,
                model_calls_per_day=100,
            ),
        )
        service = AgentService(auth, control)

        def ask(case, session=None):
            truth = expected(case) if case["expected_status"] == "answered" else None
            session = session or service.create_session(token_a)
            result = service.ask(token_a, session, case["question"])
            public = result.public
            errors = []
            if truth is not None:
                if public["status"] != "answered":
                    errors.append("not_answered")
                else:
                    metric = public["metric"]
                    numbers = public["results"]
                    if metric["id"] not in case["allowed_ids"]:
                        errors.append("wrong_metric")
                    if (
                        metric["year"] != case["year"]
                        or metric["source_product"] != case["product"]
                    ):
                        errors.append("wrong_release_product")
                    if len(numbers) != 1 or numbers[0]["geography"]["key"] != case["scope"]:
                        errors.append("wrong_geography")
                    if not numbers or not math.isclose(
                        numbers[0]["value"], truth, rel_tol=1e-12, abs_tol=1e-9
                    ):
                        errors.append("wrong_value")
                    if f"{truth:,.15g}" not in public["answer"]:
                        errors.append("answer_number_mismatch")
            elif public["status"] not in case["expected_status"] or public["results"]:
                errors.append("unsafe_or_wrong_degradation")
            if public["latency_seconds"] >= 60:
                errors.append("latency")
            diag = result.diagnostics
            if diag:
                response = diag["response"]
                if truth is None and any(s.get("query_id") for s in response["sql"]):
                    errors.append("negative_executed_data")
                if not diag["closed"] or not (
                    not diag["connected"] or public["warehouse_suspended"]
                ):
                    errors.append("cleanup")
                evidence["permission_audits"].append(
                    {"case": case["id"], "permissions": diag["permissions"]}
                )
            evidence["outcomes"].append(
                {
                    "id": case["id"],
                    "question": case["question"],
                    "expected": truth,
                    "public": public,
                    "diagnostics": diag,
                    "failures": errors,
                }
            )
            save()
            print(
                f"CASE {case['id']}: {public['status']} {public['latency_seconds']}s; failures={errors}",
                flush=True,
            )
            return result

        try:
            for case in cases["factual"]:
                ask(case)
            for conversation in cases["conversations"]:
                session = service.create_session(token_a)
                for case in conversation:
                    ask(case, session)
            for case in cases["negative"]:
                ask(case)
            # Real concurrent sessions: lease prevents overlap; accepted worker owns
            # a fresh Snowflake connection. Another principal cannot read that state.
            a, b = service.create_session(token_a), service.create_session(token_b)
            initial = cases["factual"][7]
            with ThreadPoolExecutor(1) as executor:
                running = executor.submit(service.ask, token_a, a, initial["question"])
                for _ in range(200):
                    with control._transaction() as db:
                        active = db.execute("SELECT lease FROM gate WHERE id=1").fetchone()[0]
                    if active:
                        break
                    time.sleep(0.01)
                other = service.ask(token_b, b, "And in 2019?")
                first = running.result(timeout=60)
            isolated = service.ask(token_b, b, "And in 2019?")
            denied = service.ask(token_b, a, "What is population there?")
            evidence["concurrent_sessions"] = {
                "first": first.public,
                "overlap": other.public,
                "fresh_session_followup": isolated.public,
                "cross_owner": denied.public,
                "passed": first.public["status"] == "answered"
                and other.public["status"] == "overloaded"
                and isolated.public["status"] == "clarification"
                and denied.public["status"] == "unauthorized",
            }
            save()
        finally:
            evidence["reference_permissions"] = reference.audit
            evidence["cleanup"] = reference.suspend()
            reference.close()
            evidence["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
            evidence["summary"] = {
                "cases": len(evidence["outcomes"]),
                "passed": sum(not c["failures"] for c in evidence["outcomes"]),
                "failed": sum(bool(c["failures"]) for c in evidence["outcomes"]),
            }
            save()
    successful = (
        evidence["summary"]["failed"] == 0
        and evidence.get("concurrent_sessions", {}).get("passed")
        and evidence["cleanup"]["confirmed_suspended"]
    )
    print(json.dumps(evidence["summary"]), flush=True)
    return 0 if successful else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    return run(args.output)


if __name__ == "__main__":
    raise SystemExit(main())
