"""Clean-browser HTTPS deployment smoke tests; no local/mock deployment success claim."""

from __future__ import annotations

import argparse
import ipaddress
import json
import socket
import stat
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


def public_url(url: str) -> str:
    parts = urlsplit(url)
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.query
        or parts.fragment
        or parts.path not in ("", "/")
    ):
        raise ValueError("Provide a public HTTPS origin without credentials or query parameters")
    addresses = socket.getaddrinfo(parts.hostname, parts.port or 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(row[4][0]).is_global for row in addresses):
        raise ValueError(
            "Deployed checks require public addresses; localhost/private URLs are rejected"
        )
    return url.rstrip("/")


def read_token(path: Path) -> str:
    if (
        path.is_symlink()
        or not path.is_file()
        or stat.S_IMODE(path.stat().st_mode) & 0o077
        or path.stat().st_size > 300
    ):
        raise ValueError("Reviewer token file must be small, owner-only and regular")
    token = path.read_text().strip()
    if not 32 <= len(token) <= 256:
        raise ValueError("Invalid reviewer token length")
    return token


def run_checks(url: str, token_a: str, token_b: str, report: dict) -> None:
    from playwright.sync_api import expect, sync_playwright

    def record(case: str, check):
        started = time.monotonic()
        row = {"id": case}
        try:
            detail = check()
            row.update(passed=True, detail=detail)
        except Exception as exc:
            row.update(passed=False, failure_type=type(exc).__name__)
            raise
        finally:
            row["seconds"] = round(time.monotonic() - started, 4)
            report["checks"].append(row)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        first, second = browser.new_context(), browser.new_context()
        a, b = first.new_page(), second.new_page()
        for page in (a, b):
            page.set_default_timeout(60_000)

        def load():
            response = a.goto(url, wait_until="domcontentloaded")
            assert response and response.status == 200
            expect(a.get_by_role("heading", name="Census Chat", exact=True)).to_be_visible()
            expect(a.get_by_label("Reviewer access token")).to_be_visible()
            assert a.get_by_placeholder("Ask about Census data…").count() == 0
            return {"http_status": response.status, "clean_context": True}

        record("page_public_auth_required", load)

        def login(page, token):
            page.get_by_label("Reviewer access token").fill(token)
            page.get_by_role("button", name="Sign in", exact=True).click()

        def invalid():
            login(a, "intentionally-invalid-token-at-least-32-chars")
            expect(a.get_by_text("Authentication is required.", exact=True)).to_be_visible()
            assert not a.get_by_placeholder("Ask about Census data…").count()

        record("invalid_authentication", invalid)

        def valid():
            login(a, token_a)
            expect(a.get_by_placeholder("Ask about Census data…")).to_be_visible()
            assert a.get_by_label("Reviewer access token").count() == 0

        record("reviewer_authentication", valid)

        def ask(page, question, expected_status, number=None):
            started = time.monotonic()
            prior = page.get_by_test_id("stChatMessage").count()
            box = page.get_by_placeholder("Ask about Census data…")
            box.fill(question)
            box.press("Enter")
            expect(page.get_by_test_id("stChatMessage")).to_have_count(prior + 2)
            answer = page.get_by_test_id("stChatMessage").last
            expect(answer.get_by_text("Status: " + expected_status, exact=True)).to_be_visible()
            text = answer.inner_text()
            if number is not None:
                assert number in text
            assert time.monotonic() - started < 60
            assert not any(
                x in text
                for x in (
                    "model_calls",
                    "primary_role_grants",
                    "private_key_file",
                    "SNOWFLAKE_PASSWORD",
                    "SELECT ",
                    "Traceback (",
                )
            )
            return {
                "question": question,
                "answer": text,
                "seconds": round(time.monotonic() - started, 4),
            }

        record(
            "grounded_census_answer",
            lambda: ask(
                a,
                "Using ACS release 2020, what is the total population of Autauga County, Alabama?",
                "answered",
                "55,639",
            ),
        )
        record(
            "multi_turn_follow_up",
            lambda: ask(a, "And in 2019?", "answered", "55,380"),
        )
        record(
            "unsupported_question",
            lambda: ask(
                a, "What is the population of Autauga County, Alabama in 1850?", "clarification"
            ),
        )

        def isolation():
            b.goto(url, wait_until="domcontentloaded")
            login(b, token_b)
            expect(b.get_by_placeholder("Ask about Census data…")).to_be_visible()
            assert b.get_by_test_id("stChatMessage").count() == 0
            return ask(b, "What about Autauga County?", "clarification")

        record("independent_owner_context", isolation)

        def rate_limit():
            # Fast off-topic rejections exercise the real unchanged shared limits.
            for _ in range(9):
                prior = a.get_by_test_id("stChatMessage").count()
                box = a.get_by_placeholder("Ask about Census data…")
                box.fill("Tell me a joke.")
                box.press("Enter")
                expect(a.get_by_test_id("stChatMessage")).to_have_count(prior + 2)
                last = a.get_by_test_id("stChatMessage").last
                expect(last.get_by_text("Request completed in", exact=False)).to_be_visible()
                if "Status: rate_limited" in last.inner_text():
                    return {"rate_limited": True}
            raise AssertionError("Shared rate limit not observed; preserve this failure")

        record("shared_rate_limits", rate_limit)

        def privacy():
            body = a.locator("body").inner_text() + b.locator("body").inner_text()
            assert token_a not in body and token_b not in body
            assert not any(
                s in body
                for s in (
                    "SNOWFLAKE_PASSWORD",
                    "SNOWFLAKE_PRIVATE_KEY",
                    "model_calls",
                    "primary_role_grants",
                    "Traceback (",
                )
            )
            return {
                "visible_surface_only": True,
                "note": "Does not prove absence of all secret values; inspect deployment secret handling separately.",
            }

        record("public_surface_privacy", privacy)
        browser.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--token-file", required=True, type=Path)
    parser.add_argument("--second-token-file", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Evidence path exists; use a new path")
    report = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": [],
        "availability_after_ssh_disconnect": "pending independent second probe; not inferred from browser success",
    }
    try:
        url = public_url(args.url)
        report["url"] = url
        a, b = read_token(args.token_file), read_token(args.second_token_file)
        if a == b:
            raise ValueError("Use two distinct reviewer principals/tokens")
        run_checks(url, a, b, report)
        report["passed"] = True
    except Exception as exc:
        report.update(passed=False, failure_type=type(exc).__name__)
    finally:
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        with args.output.open("x") as output:
            json.dump(report, output, indent=2)
            output.write("\n")
    print(
        "Deployment browser checks:",
        "PASS (SSH persistence still pending)"
        if report["passed"]
        else "FAIL; see safe evidence artifact",
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
