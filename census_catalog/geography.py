"""Year-specific FIPS resolution with explicit ambiguity and membership limits."""

from __future__ import annotations

import re
from typing import Any


class GeographyError(ValueError):
    pass


def parse_cbg(cbg: str) -> dict[str, str]:
    if not isinstance(cbg, str) or not re.fullmatch(r"[0-9]{12}", cbg):
        raise GeographyError("CBG must be an exact 12-digit string, including leading zeros")
    return {
        "cbg": cbg,
        "state_fips": cbg[:2],
        "county_fips": cbg[2:5],
        "county_geoid": cbg[:5],
        "tract": cbg[5:11],
        "block_group": cbg[11],
    }


class Geography:
    def __init__(self, catalog_data: dict[str, Any]):
        self.data = catalog_data
        self.states = catalog_data["sources"]["state_reference"]["rows"]
        self.counties = {}
        for year, dataset in catalog_data["geography"].items():
            index = {}
            for row in dataset["rows"]:
                key = (row["STATE_FIPS"], row["COUNTY_FIPS"])
                if (
                    not re.fullmatch(r"[0-9]{2}", key[0])
                    or not re.fullmatch(r"[0-9]{3}", key[1])
                    or key in index
                ):
                    raise GeographyError("Invalid/duplicate year-specific FIPS metadata")
                reference = [s for s in self.states if s["STATE"] == key[0]]
                if len(reference) != 1 or (row["STATE"] and row["STATE"] != reference[0]["STUSAB"]):
                    raise GeographyError("State metadata disagrees with Census reference")
                index[key] = row
            self.counties[int(year)] = index

    def resolve_state(self, query: str, year: int) -> dict[str, Any]:
        if year not in self.counties:
            raise GeographyError("No verified FIPS metadata for requested year")
        if not isinstance(query, str) or not query.strip():
            raise GeographyError("State query must be nonempty")
        key = query.strip().casefold()
        matches = [
            row
            for row in self.states
            if key
            in {row["STATE"].casefold(), row["STUSAB"].casefold(), row["STATE_NAME"].casefold()}
            and any(state == row["STATE"] for state, _ in self.counties[year])
        ]
        if len(matches) != 1:
            raise GeographyError("No unique state match in year-specific metadata")
        return {"year": year, **matches[0]}

    def resolve_county(self, query: str, year: int, state: str | None = None) -> dict[str, Any]:
        if year not in self.counties:
            raise GeographyError("No verified FIPS metadata for requested year")
        state_code = self.resolve_state(state, year)["STATE"] if state is not None else None
        if not isinstance(query, str) or not query.strip():
            raise GeographyError("County query must be nonempty")
        query = query.strip().casefold()
        matches = [
            row
            for (s, c), row in self.counties[year].items()
            if (state_code is None or state_code == s)
            and query in {str(row["COUNTY"]).casefold(), s + c}
        ]
        if len(matches) != 1:
            raise GeographyError(
                "County is unknown or ambiguous; supply state and exact county name"
            )
        return {
            "year": year,
            "fips_table": self.data["geography"][str(year)]["table"],
            **matches[0],
        }

    def lookup_cbg(self, cbg: str, year: int) -> dict[str, Any]:
        parts = parse_cbg(cbg)
        if year not in self.counties:
            raise GeographyError("No verified FIPS metadata for requested year")
        county = self.counties[year].get((parts["state_fips"], parts["county_fips"]))
        if county is None:
            raise GeographyError("CBG prefix has no year-specific county mapping")
        state = self.resolve_state(parts["state_fips"], year)
        return {
            **parts,
            "year": year,
            "state_name": state["STATE_NAME"],
            "state_abbreviation": state["STUSAB"],
            "provider_state_abbreviation": county["STATE"],
            "county_name": county["COUNTY"],
            "fips_table": self.data["geography"][str(year)]["table"],
            "cbg_membership_verified": False,
        }
