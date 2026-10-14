"""Operator-only reviewer credential provisioning; no token is printed or committed."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def provision(directory: Path, principal: str) -> tuple[Path, Path]:
    if not directory.is_absolute() or directory.resolve().is_relative_to(ROOT):
        raise ValueError("Use an absolute private directory outside this Git checkout")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", principal):
        raise ValueError("Use a simple reviewer principal identifier")
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    if (
        directory.is_symlink()
        or not directory.is_dir()
        or stat.S_IMODE(directory.stat().st_mode) & 0o077
    ):
        raise ValueError("Reviewer handoff directory must be owner-only")
    token_path, digest_path = (
        directory / f"{principal}.token",
        directory / f"{principal}.digest.json",
    )
    if token_path.exists() or digest_path.exists():
        raise ValueError("Reviewer files already exist; never overwrite credentials")
    token = secrets.token_urlsafe(32)
    fd = os.open(token_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as output:
        output.write(token + "\n")
    fd = os.open(digest_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as output:
        json.dump({hashlib.sha256(token.encode()).hexdigest(): principal}, output)
        output.write("\n")
    return token_path, digest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--principal", required=True)
    args = parser.parse_args()
    try:
        paths = provision(args.directory, args.principal)
    except (ValueError, OSError):
        print("Provisioning refused; use a private external directory and unused principal.")
        return 1
    print(
        "Owner-only token and digest files created; distribute token privately. No secret was printed."
    )
    print("Files:", *(str(path) for path in paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
