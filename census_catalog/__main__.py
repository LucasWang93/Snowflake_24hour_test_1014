"""Offline build/search/geography commands; never call Snowflake or Cortex."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from census_catalog.build import build_catalog, write_catalog
from census_catalog.catalog import Catalog
from census_catalog.geography import Geography


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path("data/semantic_catalog.json"))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build")
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--year", type=int)
    search.add_argument("--product")
    search.add_argument("--top-k", type=int, default=5)
    search.add_argument("--include-moe", action="store_true")
    geo = sub.add_parser("geography")
    geo.add_argument("cbg")
    geo.add_argument("--year", type=int, required=True)
    args = parser.parse_args()
    if args.command == "build":
        catalog = build_catalog(
            Path("docs/phase1_metadata.json"),
            Path("docs/snowflake_evidence.json"),
            Path("docs/phase1_state_reference.json"),
        )
        write_catalog(catalog, args.catalog)
        result = {
            k: v
            for k, v in catalog["coverage"].items()
            if k not in {"by_table", "quarantined_fields"}
        }
    else:
        catalog = Catalog.load(args.catalog)
        if args.command == "search":
            result = catalog.search(
                args.query,
                year=args.year,
                source_product=args.product,
                top_k=args.top_k,
                include_moe=args.include_moe,
            )
        else:
            result = Geography(catalog.data).lookup_cbg(args.cbg, args.year)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
