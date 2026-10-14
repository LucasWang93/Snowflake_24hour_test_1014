#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$ROOT"
if [[ -n "${PYTHON_BIN:-}" ]]; then
  PY="$PYTHON_BIN"
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  PY="$ROOT/.venv/bin/python"
else
  PY=python3
fi
printf 'Doctor: read-only inspection (no environment files sourced)\n'
bash --version | head -n 1
if ! command -v "$PY" >/dev/null 2>&1; then
  printf 'FAIL: Python interpreter unavailable\n'
  exit 1
fi
"$PY" --version
for tool in git shellcheck; do
  if command -v "$tool" >/dev/null 2>&1; then
    "$tool" --version | head -n 1
  else
    printf 'MISSING optional tool: %s\n' "$tool"
  fi
done
"$PY" - <<'PYCODE'
import importlib.metadata
import os
import re
from pathlib import Path

for name in ('pytest', 'ruff'):
    try:
        print(f'{name}: {importlib.metadata.version(name)}')
    except importlib.metadata.PackageNotFoundError:
        print(f'MISSING development dependency: {name}')
example = Path('.env.example')
keys = []
if example.is_file():
    # Only the safe, tracked example is read; never read .env or credentials.
    for line in example.read_text().splitlines():
        match = re.match(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=', line)
        if match:
            keys.append(match.group(1))
for key in keys:
    print(f'Environment {key}: {"SET" if key in os.environ else "MISSING in process environment"}')
if not keys:
    print('Environment: no challenge-specific variables declared yet')
print(f'Local .env: {"present (not read)" if Path(".env").exists() else "absent"}')
print('Configuration in local files is not loaded or validated.')
PYCODE
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf 'Repository status (filenames only):\n'
  git status --short --untracked-files=all
else
  printf 'INFO: no Git worktree detected\n'
fi
