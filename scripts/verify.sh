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
failed=0
incomplete=0
run_check() {
  local label="$1"
  shift
  printf 'RUN: %s\n' "$label"
  if "$@"; then
    printf 'PASS: %s\n' "$label"
  else
    local rc=$?
    printf 'FAIL: %s (exit %s)\n' "$label" "$rc"
    failed=1
  fi
}
while IFS= read -r -d '' script; do
  run_check "Bash syntax: $script" bash -n "$script"
done < <(find scripts -type f -name '*.sh' -print0)
if command -v shellcheck >/dev/null 2>&1; then
  while IFS= read -r -d '' script; do
    run_check "ShellCheck: $script" shellcheck "$script"
  done < <(find scripts -type f -name '*.sh' -print0)
else
  printf 'SKIP: optional ShellCheck unavailable (Bash syntax checked)\n'
fi
if ! command -v "$PY" >/dev/null 2>&1; then
  printf 'FAIL: Python interpreter unavailable\n'
  exit 1
fi
# Discover code by filename only. Do not traverse local environments or credentials.
code_count="$("$PY" - <<'PYCODE'
import os
from pathlib import Path
count = 0
excluded = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.pytest_cache', '.ruff_cache', 'build', 'dist', '.tox', '.nox'}
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in excluded and not d.startswith('.')]
    count += sum(Path(f).suffix == '.py' for f in files)
print(count)
PYCODE
)"
if [[ "$code_count" -gt 0 ]]; then
  if "$PY" -c 'import importlib.util; raise SystemExit(importlib.util.find_spec("ruff") is None)'; then
    run_check 'Ruff formatting' "$PY" -m ruff format --check .
    run_check 'Ruff lint' "$PY" -m ruff check .
  else
    printf 'SKIP: Ruff unavailable for Python code\n'
    incomplete=1
  fi
else
  printf 'SKIP: Ruff checks — no Python code yet\n'
  incomplete=1
fi
if "$PY" -c 'import importlib.util; raise SystemExit(importlib.util.find_spec("pytest") is None)'; then
  printf 'RUN: pytest\n'
  # Disable third-party autoload to keep generic runs reproducible. Explicitly
  # enable required plugins in project configuration when actual tests need them.
  if PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PY" -m pytest; then
    printf 'PASS: pytest\n'
  else
    rc=$?
    if [[ "$rc" -eq 5 ]]; then
      printf 'SKIP: pytest collected no tests\n'
      incomplete=1
    else
      printf 'FAIL: pytest (exit %s)\n' "$rc"
      failed=1
    fi
  fi
else
  printf 'SKIP: pytest unavailable\n'
  incomplete=1
fi
for manifest in package.json Cargo.toml go.mod; do
  if [[ -f "$manifest" ]]; then
    printf 'SKIP: %s detected; configure its native verification before delivery\n' "$manifest"
    incomplete=1
  fi
done
if [[ "$failed" -ne 0 ]]; then
  printf 'Verification: FAIL\n'
  exit 1
elif [[ "$incomplete" -ne 0 ]]; then
  printf 'Verification: INCOMPLETE (exit 2; skips are not passes)\n'
  exit 2
fi
printf 'Verification: PASS (optional checks may be explicitly skipped above)\n'
