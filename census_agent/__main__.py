"""Local interactive CLI. Explicit user requests consume Snowflake/Cortex credits."""

from __future__ import annotations

import argparse
import json
import sys

from census_agent.agent import CensusAgent
from census_agent.backend import SnowflakeBackend
from census_agent.types import ConversationState
from census_catalog.catalog import Catalog
from scripts.snowflake_probe import ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", help="Run one question instead of interactive conversation")
    parser.add_argument(
        "--json", action="store_true", help="Include structured result/SQL/query-ID diagnostics"
    )
    parser.add_argument(
        "--model", default="llama3.3-70b", choices=["llama3.3-70b", "llama3.1-70b", "mistral-7b"]
    )
    args = parser.parse_args()
    backend = None
    try:
        catalog = Catalog.load(ROOT / "data/semantic_catalog.json")
        backend = SnowflakeBackend(catalog, args.model)
        agent = CensusAgent(
            catalog, backend, lambda stage: print(f"[{stage}]", file=sys.stderr, flush=True)
        )
        state = ConversationState()
        if args.question:
            response = agent.ask(args.question, state)
            print(
                json.dumps(response.as_dict(), indent=2, default=str)
                if args.json
                else response.answer
            )
            return 0 if response.status == "answered" else 2
        print(
            "Census analytics: specify release/product/geography. /reset clears state; /quit exits."
        )
        while True:
            try:
                question = input("You> ").strip()
            except EOFError:
                break
            if question == "/quit":
                break
            if question == "/reset":
                state.reset()
                print("Conversation reset.")
                continue
            response = agent.ask(question, state)
            print(
                json.dumps(response.as_dict(), indent=2, default=str)
                if args.json
                else response.answer
            )
        return 0
    except KeyboardInterrupt:
        print("Stopped.", file=sys.stderr)
        return 130
    except Exception:
        print(
            "Unable to initialize the local agent. Check catalog and local configuration; credentials are not displayed.",
            file=sys.stderr,
        )
        return 1
    finally:
        if backend is not None:
            try:
                backend.close()
            except Exception:
                print("Connection cleanup could not be confirmed.", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
