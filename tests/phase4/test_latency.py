"""Offline index equivalence and warehouse cleanup invalidation; no provider calls."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from census_agent.backend import SnowflakeBackend
from census_catalog.catalog import Catalog

SOURCE = Path(__file__).resolve().parents[2] / "data/semantic_catalog.json"


@pytest.fixture(scope="module")
def prepared_index(tmp_path_factory):
    path = tmp_path_factory.mktemp("search-index") / "index.jsonl"
    Catalog.prepare_index(SOURCE, path)
    return path


def test_prepared_index_preserves_all_postings_and_ranked_mappings(
    prepared_index, catalog, monkeypatch
):
    with monkeypatch.context() as m:
        m.setattr("census_catalog.catalog.tokens", lambda _: pytest.fail("Index rebuilt"))
        cached = Catalog.load(SOURCE, index_path=prepared_index)
    assert cached.documents == catalog.documents
    assert cached.index == catalog.index
    assert cached.average_length == catalog.average_length
    for query in ("population", "median age", "household income", "education", "employment"):
        assert cached.search(query, top_k=10) == catalog.search(query, top_k=10)


@pytest.mark.parametrize("defect", ["missing", "catalog", "implementation", "corrupt", "truncated"])
def test_invalid_index_falls_back_to_verified_metadata(prepared_index, tmp_path, catalog, defect):
    target = tmp_path / "index.json"
    header, payload = prepared_index.read_bytes().split(b"\n", 1)
    data = json.loads(header)
    if defect == "catalog":
        data["catalog_sha256"] = "stale"
    elif defect == "implementation":
        data["implementation_sha256"] = "stale"
    elif defect == "corrupt":
        payload += b" "  # Still valid JSON; checksum must detect altered bytes.
    if defect != "missing":
        target.write_bytes(
            b"{" if defect == "truncated" else json.dumps(data).encode() + b"\n" + payload
        )
    restored = Catalog.load(SOURCE, index_path=target)
    assert restored.search("population") == catalog.search("population")


def test_index_does_not_bypass_physical_schema_validation(prepared_index, catalog):
    import copy

    data = copy.deepcopy(catalog.data)
    data["entries"][0]["schema_verified"] = False
    with pytest.raises(ValueError, match="schema is unverified"):
        Catalog(data, search_index=json.loads(prepared_index.read_bytes().split(b"\n", 1)[1]))


def test_index_builder_cannot_overwrite_source(tmp_path):
    source = tmp_path / "source.json"
    source.write_text('{"preserve": true}')
    with pytest.raises(ValueError, match="must not overwrite"):
        Catalog.prepare_index(source, source)
    assert source.read_text() == '{"preserve": true}'


def test_close_does_not_suspend_twice_after_confirmed_cleanup(monkeypatch):
    backend = SnowflakeBackend(None)
    backend._connection = MagicMock()
    backend._connection.is_closed.return_value = False
    backend._config = {"SNOWFLAKE_WAREHOUSE": "OFFLINE_WH"}

    def run(sql, *args):
        if sql.startswith("SHOW"):
            return {
                "query_id": "offline",
                "columns": ["name", "state"],
                "rows": [["OFFLINE_WH", "SUSPENDED"]],
            }
        return {"query_id": "offline"}

    monkeypatch.setattr(backend, "_run", run)
    assert backend.suspend()["confirmed_suspended"]
    spy = MagicMock(wraps=backend.suspend)
    monkeypatch.setattr(backend, "suspend", spy)
    backend.close()
    spy.assert_not_called()
    backend._connection.close.assert_called_once()


@pytest.mark.parametrize("fails", [False, True])
def test_any_sql_attempt_invalidates_cleanup_and_close_retries(monkeypatch, fails):
    backend = SnowflakeBackend(None)
    backend._connection = MagicMock()
    backend._cleanup_confirmed = True
    cursor = backend._connection.cursor.return_value.__enter__.return_value
    cursor.description = [("VALUE",)]
    cursor.fetchmany.return_value = [[1]]
    if fails:
        cursor.execute.side_effect = RuntimeError("offline failure")
        with pytest.raises(RuntimeError):
            backend._run("SELECT 1", None, 1, 1)
    else:
        backend._run("SELECT 1", None, 1, 1)
    assert not backend._cleanup_confirmed
    suspend = MagicMock()
    monkeypatch.setattr(backend, "suspend", suspend)
    backend.close()
    suspend.assert_called_once()
