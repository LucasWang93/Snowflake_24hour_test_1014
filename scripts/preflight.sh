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
if "$ROOT/scripts/verify.sh"; then
  :
else
  rc=$?
  if [[ "$rc" -eq 2 ]]; then incomplete=1; else failed=1; fi
fi
if ! command -v "$PY" >/dev/null 2>&1; then
  printf 'FAIL: Python interpreter unavailable for preflight\n'
  exit 1
fi
if "$PY" - <<'PYCODE'
import re
import subprocess
from pathlib import Path

failed = False
pending = False
required = {
    'CHALLENGE_SPEC.md': ['Objective', 'Rules', 'Requirements', 'Acceptance criteria', 'Deliverables', 'Ambiguity', 'Traceability', 'Ordered implementation plan'],
    'ARCHITECTURE.md': ['Overview', 'Interfaces', 'Design choices', 'Failure modes', 'Alternatives'],
    'DECISIONS.md': [],
    'EVALUATION_PLAN.md': ['Dimensions', 'Datasets and cases', 'Metrics and baselines', 'Commands', 'Observed results', 'Failure analysis and limitations'],
    'PROGRESS.md': ['Completed', 'In progress', 'Blocked', 'Next three actions', 'Verification evidence'],
    'DELIVERY_CHECKLIST.md': ['Functional', 'Reliability', 'Evaluation', 'Security', 'Documentation', 'Reproducibility', 'Submission'],
}
for name, headings in required.items():
    path = Path('docs') / name
    if not path.is_file() or not path.stat().st_size:
        print(f'FAIL: missing/empty document {path}')
        failed = True
        continue
    content = path.read_text()
    for heading in headings:
        match = re.search(r'^## ' + re.escape(heading) + r'\s*\n(.*?)(?=^## |\Z)', content, re.M | re.S)
        if not match or not match.group(1).strip():
            print(f'FAIL: missing/empty section {path}: {heading}')
            failed = True
    if re.search(r'\b(PENDING|TODO|TBD)\b|^- \[ \]', content, re.M):
        print(f'INCOMPLETE: {path} contains pending work/unchecked items')
        pending = True
for name in ('AGENTS.md', '.env.example', '.gitignore', 'requirements-dev.txt'):
    if not Path(name).is_file():
        print(f'FAIL: missing harness file {name}')
        failed = True
for name in ('challenge-intake', 'solution-architecture', 'implementation-loop', 'evaluation-engineering', 'production-hardening', 'delivery-review'):
    path = Path('.agents/skills') / name / 'SKILL.md'
    if not path.is_file():
        print(f'FAIL: missing skill {name}')
        failed = True
for name in ('doctor', 'verify', 'preflight'):
    path = Path('scripts') / f'{name}.sh'
    if not path.is_file() or path.stat().st_mode & 0o111 == 0:
        print(f'FAIL: missing/non-executable script {path}')
        failed = True
try:
    result = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], capture_output=True, check=True)
except (FileNotFoundError, subprocess.CalledProcessError):
    print('INCOMPLETE: Git file-risk inspection unavailable')
    pending = True
else:
    # Filename checks only: ignored local credentials are never read.
    for raw in result.stdout.split(b'\0'):
        if not raw:
            continue
        name = raw.decode(errors='replace')
        base = Path(name).name.lower()
        if base == '.env.example':
            continue
        if (base == '.env' or base.startswith('.env.') or base.endswith(('.pem', '.key', '.p12', '.pfx'))
                or 'credential' in base or 'service-account' in base or base in {'id_rsa', 'id_ed25519', '.netrc'}):
            print(f'FAIL: possible secret file eligible for submission: {name!r}')
            failed = True
    print('File-risk inspection complete; content-level secret detection is not performed.')
print('Documentation checks inspect structure/placeholders; human semantic review remains required.')
raise SystemExit(1 if failed else 2 if pending else 0)
PYCODE
then
  :
else
  rc=$?
  if [[ "$rc" -eq 2 ]]; then incomplete=1; else failed=1; fi
fi
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf 'Uncommitted/untracked files (review before submission):\n'
  git status --short --untracked-files=all
  if [[ -n "$(git status --porcelain --untracked-files=all)" ]]; then
    printf 'INCOMPLETE: working tree changes require review/intentional inclusion\n'
    incomplete=1
  fi
  if ! git diff --check || ! git diff --cached --check; then
    printf 'FAIL: Git whitespace check\n'
    failed=1
  fi
else
  printf 'INCOMPLETE: Git status unavailable\n'
  incomplete=1
fi
if [[ "$failed" -ne 0 ]]; then
  printf 'Readiness: FAIL — resolve reported defects/risks (exit 1)\n'
  exit 1
elif [[ "$incomplete" -ne 0 ]]; then
  printf 'Readiness: INCOMPLETE — preparation only; challenge gates unverified (exit 2)\n'
  exit 2
fi
printf 'Readiness: automated checks complete; confirm semantic review and gates A-E before delivery\n'
