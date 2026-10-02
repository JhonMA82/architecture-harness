# Architecture Harness — project instructions

This repository is an OpenCode v2 architecture harness for agent-first software development.

## Non-negotiable invariants

- All target projects are assumed to be developed 100% with AI agents.
- Prefer framework-native conventions before generic architecture patterns.
- Prefer deterministic inspection and verification before LLM judgment.
- Use the cheapest sufficient evidence source: project-native tooling -> filesystem/Git -> rg -> tgrep/ast-grep when justified -> CodeGraph/CBM for graph-level questions. Heavy indexing is never the default.
- Choose the minimum sufficient architecture; do not demonstrate architectural sophistication.
- Preserve working behavior during refactors unless the user explicitly requests a behavior change.
- A valid outcome is KEEP: no architectural restructuring is required.
- Never invent a framework convention. Inspect the target and use the matching ecosystem knowledge when available.
- Do not use subagents. This harness intentionally has one primary architect agent.
- Do not modify target source code. The harness produces architecture instructions, not implementation.

## Commands

- `/architect/analyze <path-or-git-url>` — analyze an existing project.
- `/architect/new <idea/specification>` — design a new project.
- `/architect/status` — report current architectural state and unresolved material decisions.
- `/architect/finalize` — write the final executable architecture contract.

## Evidence and deterministic tools

- `python scripts/inspect_project.py <target> --json` — cheap facts, scale, Git churn, hotspots, generated-code candidates, and available/configured analysis tooling.
- `python scripts/check_architecture.py <target-or-handoff>` — enforce the finalized architecture contract.
- `python -m unittest discover -s tests -v` — harness self-tests.
- `knowledge/tooling.md` — routing policy for project-native tooling, `rg`, `tgrep`, ast-grep, CodeGraph, and codebase-memory-mcp.

Do not require optional tools. If a heavier search/index/graph tool is unavailable or unjustified, fall back to targeted local inspection.

## Final artifacts

Finalization must produce exactly these contract artifacts for the target:

1. `ARCHITECTURE.md` — final human/agent-readable instructions.
2. `.architecture/handoff.json` — machine-readable contract for OpenCode, AndMar, and Work Ledger.

The final document is not a roadmap or an open-ended recommendation. It must state the decided target architecture, final structure, dependency rules, migration instructions when applicable, verification, non-goals, and completion criteria.
