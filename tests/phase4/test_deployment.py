"""Offline packaging/credential-runner checks, not actual Docker/HTTPS deployment."""

import hashlib
import json
import socket
import tomllib
from pathlib import Path

import pytest

from scripts.create_reviewer_token import ROOT, provision
from scripts.deployment_smoke import public_url, read_token


@pytest.mark.parametrize(
    "url",
    [
        "http://example.org",
        "https://user:password@example.org",
        "https://example.org/?token=secret",
        "https://example.org/private",
    ],
)
def test_smoke_runner_rejects_unsafe_url(url):
    with pytest.raises(ValueError):
        public_url(url)


def test_smoke_runner_requires_public_dns_addresses(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(None, None, None, None, ("127.0.0.1", 443))],
    )
    with pytest.raises(ValueError):
        public_url("https://example.org")
    monkeypatch.setattr(
        socket, "getaddrinfo", lambda *args, **kwargs: [(None, None, None, None, ("8.8.8.8", 443))]
    )
    assert public_url("https://example.org/") == "https://example.org"


def test_generated_tokens_are_private_external_and_not_overwritten(tmp_path, capsys):
    token_path, digest_path = provision(tmp_path / "reviewers", "reviewer1")
    token = read_token(token_path)
    assert json.loads(digest_path.read_text()) == {
        hashlib.sha256(token.encode()).hexdigest(): "reviewer1"
    }
    assert not token_path.stat().st_mode & 0o077 and not digest_path.stat().st_mode & 0o077
    assert token not in capsys.readouterr().out
    with pytest.raises(ValueError):
        provision(tmp_path / "reviewers", "reviewer1")
    assert read_token(token_path) == token
    with pytest.raises(ValueError):
        provision(ROOT / ".secrets", "reviewer2")
    token_path.chmod(0o644)
    with pytest.raises(ValueError):
        read_token(token_path)


def test_streamlit_and_docker_boundary_configuration():
    config = tomllib.loads(Path("deploy/streamlit.toml").read_text())
    assert config["server"]["enableCORS"] and config["server"]["enableXsrfProtection"]
    assert not config["server"]["enableStaticServing"] and not config["runner"]["fastReruns"]
    assert config["client"]["showErrorDetails"] == "none"
    docker = Path("deploy/Dockerfile").read_text()
    assert "COPY . " not in docker and "COPY .env" not in docker
    assert "USER 10001:10001" in docker
