# Reusable project-delivery lessons

Created2026-10-15 at the user's request. No application/deployment change.

New skill: `.agents/skills/business-first-delivery/SKILL.md`. A byte-identical personal
copy is installed at `~/.codex/skills/business-first-delivery/` in this environment
(or the configured CODEX_HOME skills root). It supports normal automatic discovery;
explicit invocation is `$business-first-delivery`. New Codex sessions can discover it.
The repository copy is versioned; subsequent edits should deliberately synchronize
and validate the personal copy rather than silently overwrite an existing skill.

The skill prioritizes representative user workflows, data/operation feasibility,
compositional vertical slices and evidence-backed business acceptance. It separates
business cases from assertion counts, tests normal-language false refusals, preserves
independent first-run failures, and distinguishes UI history from result memory.
Security remains essential; no project scope, deployment or paid-call authorization
is granted by this skill. The Census case is an optional reference, not a universal
technology choice, test count or workflow requirement.

Supporting references:
- `references/acceptance-worksheet.md`: scalable user-task matrix and readiness checks.
- `references/census-retrospective.md`: factual case study with limitations.

The six existing repository skills now link to this skill at their relevant decision
points; AGENTS.md names it for multi-workflow projects. Existing instructions remain.
Previously uncommitted diagnostic/proposal files are preserved separately and are
not included in this skill-only checkpoint.

Verification:
- Bundled `quick_validate.py`: all seven repository skills and the personal copy valid.
- All four package files identical between repository/personal copies.
- Eight skill-relative Markdown references resolve.
- Full existing verification:203 passed /25 opt-in live skips, Ruff/Bash checks pass.
- Git whitespace checks pass; application/source/config/evaluation artifacts unchanged.

Validator ran with system Python's existing PyYAML. An initial attempt using the
project .venv could not import yaml; no project dependency was added. Validation is
structural/manual review, not evidence that future agent behavior is guaranteed.
No new unit tests mirroring instruction wording, service changes or live model calls.
