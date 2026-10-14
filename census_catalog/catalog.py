"""Offline inverted-index BM25 search over physically verified Census metadata."""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from scripts.snowflake_probe import quote_identifier

STOP = set("what is the in of by and to a an for on with me show please how many".split())
ALIASES = {
    "population": {"population", "people", "person", "persons"},
    "education": {"education", "educational", "attainment", "school", "schooling"},
    "employment": {"employment", "employed", "labor", "labour", "workforce", "occupation"},
    "income": {"income"},
    "household": {"household", "households"},
}


def tokens(text: str) -> list[str]:
    normalized = {"educational": "education", "households": "household"}
    return [
        normalized.get(t, t) for t in re.findall(r"[a-z0-9]+", text.casefold()) if t not in STOP
    ]


class Catalog:
    def __init__(self, data: dict[str, Any]):
        self.data = data
        self.schemas = data["schemas"]
        self.entries = {e["id"]: e for e in data["entries"]}
        if len(self.entries) != len(data["entries"]):
            raise ValueError("Duplicate catalog ID")
        self.physical = {
            (table, column["column"]): column
            for table, columns in self.schemas.items()
            for column in columns
        }
        for entry in self.entries.values():
            key = (entry["table"], entry["column"])
            if key not in self.physical or self.physical[key]["data_type"] != entry["data_type"]:
                raise ValueError("Catalog entry does not match exact physical schema")
            if not entry["schema_verified"]:
                raise ValueError("Catalog schema is unverified")
        self.documents = {}
        self.index: dict[str, dict[str, int]] = defaultdict(dict)
        for entry in self.entries.values():
            if not entry["semantic_verified"]:
                continue
            text = (
                (entry["title"] + " ") * 4
                + (entry["topic"] + " ") * 2
                + (" ".join(entry["field_path"]) + " ") * 3
                + entry["universe"]
                + " "
                + entry["column"]
            )
            counts = Counter(tokens(text))
            self.documents[entry["id"]] = sum(counts.values())
            for term, count in counts.items():
                self.index[term][entry["id"]] = count
        self.average_length = sum(self.documents.values()) / max(len(self.documents), 1)

    @classmethod
    def load(cls, path: Path = Path("data/semantic_catalog.json")) -> Catalog:
        return cls(json.loads(path.read_text()))

    def mapping(self, entry_id: str) -> dict[str, Any]:
        entry = self.entries[entry_id]
        names = ["CENSUS_BLOCK_GROUP", entry["column"]]
        counterpart = re.sub(
            r"([em])([0-9]+)$",
            lambda m: ("m" if m[1] == "e" else "e") + m[2],
            entry["column"],
        )
        paired = self.entries.get(f"{entry['table']}.{counterpart}")
        if paired and paired["semantic_verified"] and counterpart != entry["column"]:
            names.append(counterpart)
        year = entry["year"]
        geo_table = (
            f"{year}_REDISTRICTING_METADATA_CBG_GEOGRAPHIC_DATA"
            if entry["source_product"] == "decennial_redistricting_pl94_171"
            else f"{year}_METADATA_CBG_GEOGRAPHIC_DATA"
        )
        key = "CENSUS_BLOCK_GROUP"
        if (geo_table, key) not in self.physical:
            raise ValueError("Geography association lacks verified physical key")
        fips = self.data["geography"][str(year)]
        qualified = ".".join(
            quote_identifier(value)
            for value in (self.data["database"], self.data["schema"], entry["table"])
        )
        return {
            **entry,
            "database": self.data["database"],
            "schema": self.data["schema"],
            "qualified_table": qualified,
            "quoted_column": quote_identifier(entry["column"]),
            "physical_schema": [self.physical[(entry["table"], name)] for name in names],
            "geography": {
                "level": "census_block_group",
                "key": key,
                "year": year,
                "geographic_table": geo_table,
                "fips_table": fips["table"],
                "state_fips_expression": 'SUBSTR("CENSUS_BLOCK_GROUP", 1, 2)',
                "county_fips_expression": 'SUBSTR("CENSUS_BLOCK_GROUP", 3, 3)',
                "cbg_membership": "must be checked in source table; syntactic parsing is not membership",
            },
        }

    def table_schema(self, table: str) -> list[dict[str, Any]]:
        return self.schemas[table]

    def search(
        self,
        query: str,
        *,
        year: int | None = None,
        source_product: str | None = None,
        top_k: int = 5,
        include_moe: bool = False,
    ) -> list[dict[str, Any]]:
        if not isinstance(query, str) or len(query) > 2000:
            raise ValueError("Search query must be a string of at most 2000 characters")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 100:
            raise ValueError("top_k must be between 1 and 100")
        query_tokens = set(tokens(query))
        years = {int(t) for t in query_tokens if re.fullmatch(r"(?:19|20)[0-9]{2}", t)}
        if year is not None and years and year not in years:
            raise ValueError("Explicit year conflicts with the query year")
        if year is None and len(years) == 1:
            year = years.pop()
        query_tokens -= {t for t in query_tokens if re.fullmatch(r"(?:19|20)[0-9]{2}", t)}
        moe_query = bool(query_tokens & {"moe", "margin", "error"})
        if moe_query:
            query_tokens -= {"moe", "margin", "margins", "error", "errors"}
        query_tokens = {
            next((key for key, alternatives in ALIASES.items() if term in alternatives), term)
            for term in query_tokens
        }
        groups = []
        for term in sorted(query_tokens):
            group = next((v for k, v in ALIASES.items() if term == k or term in v), {term})
            groups.append(group)
        if not groups and not moe_query:
            return []
        candidates = set(self.documents)
        for group in groups:
            candidates &= set().union(*(set(self.index.get(term, {})) for term in group))
        scored = []
        total_documents = len(self.documents)
        for entry_id in candidates:
            entry = self.entries[entry_id]
            if year is not None and entry["year"] != year:
                continue
            if source_product and entry["source_product"] != source_product:
                continue
            if moe_query and entry["estimate_kind"] != "moe":
                continue
            if not moe_query and not include_moe and entry["estimate_kind"] == "moe":
                continue
            score = 0.0
            matched = []
            for group, original_term in zip(groups, sorted(query_tokens)):
                group_scores = []
                for term in sorted(group):
                    postings = self.index.get(term, {})
                    if entry_id not in postings:
                        continue
                    frequency = postings[entry_id]
                    idf = math.log(
                        1 + (total_documents - len(postings) + 0.5) / (len(postings) + 0.5)
                    )
                    denominator = frequency + 1.2 * (
                        0.25 + 0.75 * self.documents[entry_id] / self.average_length
                    )
                    weight = 1.0 if term == original_term else 0.35
                    group_scores.append(weight * idf * frequency * 2.2 / denominator)
                    matched.append(term)
                score += max(group_scores, default=0)
            intent_terms = {
                next((key for key, alternatives in ALIASES.items() if term in alternatives), term)
                for term in query_tokens
            }
            title_terms = set(tokens(entry["title"]))
            topic_terms = set(tokens(entry["topic"]))
            score += 2.0 * len(query_tokens & title_terms)
            score += 1.0 * len(intent_terms & title_terms)
            score += 1.0 * len(query_tokens & topic_terms)
            phrase_terms = [t for t in tokens(query) if t in query_tokens]
            phrase = " ".join(phrase_terms)
            if phrase and phrase in " ".join(tokens(entry["title"])):
                score += 3.0
            if "allocation" in entry["title"].casefold():
                score *= 0.25
            if entry["aggregation"]["measure"] == "ratio_or_index" and not (
                query_tokens & {"ratio", "percentage", "percent", "rate", "index", "gini", "rent"}
            ):
                score *= 0.65
            # Do not equate rank with confidence. This small tie preference avoids
            # redundant MOEs when estimates are requested and favors simpler totals.
            score += 0.05 if entry["estimate_kind"] != "moe" else 0
            if entry["field_path"] == ["Total"]:
                score += 0.05
            scored.append((score, entry_id, sorted(set(matched))))
        scored.sort(key=lambda row: (-row[0], -self.entries[row[1]]["year"], row[1]))
        # Broad searches should expose multiple indicator definitions, not fill
        # the page with demographic cells of one long cross-tabulation.
        distinct, deferred, seen_definitions = [], [], set()
        for row in scored:
            e = self.entries[row[1]]
            key = (e["year"], e["table"], e["original_table_id"])
            if key in seen_definitions:
                deferred.append(row)
            else:
                distinct.append(row)
                seen_definitions.add(key)
        selected = (distinct + deferred)[:top_k]
        return [
            {**self.mapping(entry_id), "search_score": round(score, 6), "matched_terms": terms}
            for score, entry_id, terms in selected
        ]
