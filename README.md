# Architecture Harness for OpenCode v2

A focused architecture harness for software that will be developed **100% by AI agents**.

It analyzes existing repositories or designs new projects, selects the minimum sufficient architecture for the actual stack/framework, resolves material architecture decisions with the user only when necessary, and produces a final contract that OpenCode, AndMar, and Work Ledger can execute without re-deciding the architecture.

## What it is

The harness is intentionally separate from AndMar.

```text
Architecture Harness
        │
        ├─ existing project: inspect -> assess -> KEEP / ORGANIZE / RESTRUCTURE
        │
        └─ new project: idea -> archetype/framework -> final architecture
        │
        ▼
ARCHITECTURE.md + .architecture/handoff.json
        │
        ▼
AndMar / OpenCode
        │
        ▼
Work Ledger -> Work Units -> verification -> completion
```

**Architecture Harness decides the destination. Work Ledger decomposes the destination into work. Work Ledger must not reinterpret the architecture.**

## Design rules

- Agent-first is an invariant, never an option.
- Framework-native first.
- Deterministic inspection before LLM judgment.
- Minimum sufficient architecture.
- Locality, explicit ownership, bounded cognitive scope.
- Mechanical verification where practical.
- Incremental refactor instead of rewrite.
- KEEP / no architectural change is a valid result.
- One architect agent; no reviewer/explorer hierarchy.
- The harness never implements target-project source code.

## OpenCode v2 structure

```text
.opencode/
├── agents/
│   └── architect.md
├── commands/
│   └── architect/
│       ├── analyze.md
│       ├── new.md
│       ├── status.md
│       └── finalize.md
└── skills/
    ├── project-assessment/
    ├── architecture-design/
    ├── safe-refactoring/
    └── architecture-handoff/
```

The configuration uses current OpenCode v2 concepts: project agents, nested Markdown commands, directory skills, ordered permissions, and `AGENTS.md` instructions.

Official references:

- https://opencode.ai/v2/docs/agents
- https://opencode.ai/v2/docs/commands
- https://opencode.ai/v2/docs/skills
- https://opencode.ai/v2/docs/permissions
- https://opencode.ai/v2/docs/instructions

## Run

From this repository:

```bash
opencode
```

`architect` is configured as the default primary agent.

### Existing local project

```text
/architect/analyze /home/user/dev/project
```

External-directory reads are allowed because analyzing arbitrary local project paths is a core harness function. Unknown shell commands still require approval; the harness scripts and read-only `rg` searches are pre-authorized.

### Existing Git repository

```text
/architect/analyze https://github.com/org/project
```

The deterministic inspector creates a fresh shallow clone under `.architecture-cache/`. This cache is ignored by Git and exists only so the architect can inspect relevant files. Final artifacts for URL-only analysis are written under `output/<project>/` unless a real local destination is supplied later.

### New project

```text
/architect/new Desktop CAD application in Python/PySide6 for parametric speaker-box design
```

The architect iterates conversationally. There is deliberately no `/iterate` command.

### Current state

```text
/architect/status
```

This reads `.work/current.json`; it does not re-run repository inspection.

### Finalize

```text
/architect/finalize
```

Finalization produces exactly two contract artifacts:

```text
ARCHITECTURE.md
.architecture/handoff.json
```

For local existing projects they are written into the target root. For URL-only/new-project sessions without a destination they are written under `output/<slug>/`.

## Why the final document is different from a roadmap

`ARCHITECTURE.md` is an instruction contract. When it is finalized it must not contain open architectural choices such as "consider X later" or "first evaluate Y".

It defines:

- final target architecture;
- final useful repository structure;
- ownership and module responsibilities;
- allowed and forbidden dependency directions;
- framework conventions that must be preserved;
- exact migration/refactor strategy for existing projects;
- verification commands and architecture checks;
- non-goals / forbidden overengineering;
- completion criteria.

The machine handoff carries the same decisions in a compact form.

## Intervention model for existing projects

Only three classifications exist:

### KEEP

The architecture is already suitable. Do not restructure it. Add only targeted improvements that materially improve agent work.

### ORGANIZE

Keep the fundamental architecture and improve ownership, locality, composition, or boundaries. A God Object extraction is typically ORGANIZE when the surrounding architecture remains valid.

### RESTRUCTURE

The underlying architectural organization itself must change because evidence shows it is incompatible with requirements or creates pervasive friction.

## Framework-native first

The harness does not force one layout onto every stack.

A Laravel application should remain recognizably Laravel. Feature locality may be logical rather than physical when canonical framework directories are important.

A large PySide6 desktop application may use a hybrid Modular Monolith + selective Feature Slices when a shared CAD/domain core is cohesive and user-facing capabilities benefit from local ownership.

A compiler may be pipeline-oriented. A reusable geometry library may be domain/package-oriented. A small CLI may need only a few modules.

**Agent-first is the criterion. Modular Monolith is not the default answer.**

## Knowledge packs

`knowledge/ecosystems/` stores framework-specific conventions. Adding support for a new ecosystem does not change the harness architecture; add a knowledge file.

Included initially:

- PySide6 / Qt
- Laravel
- OpenCode v2

General architecture/refactor principles live in the top-level `knowledge/` documents.

## Deterministic inspector

```bash
python scripts/inspect_project.py /path/to/project --json
```

It reports cheap observable facts including:

- languages, framework hints, package managers/manifests and entry points;
- test/CI presence and top-level structure;
- repository scale and largest text files;
- Python structural hotspots and simple top-module dependency edges;
- local Git history/churn hotspots when history is available;
- generated-code candidates;
- installed/configured analysis-tool hints (`rg`, tgrep, ast-grep, CodeGraph/CBM where detectable);
- project-native tooling/configuration hints.

It does **not** build embeddings, a persistent semantic index, architecture scores, or a universal code graph. `knowledge/tooling.md` defines escalation: use project-native tools and cheap local search first; use tgrep/ast-grep/CodeGraph/codebase-memory-mcp only when the architectural question justifies them. Optional-tool absence never blocks analysis.

## Architecture checker

The final handoff can declare supported mechanical checks:

- `require_path`
- `forbid_path`
- `forbid_python_import`

Run current-phase checks:

```bash
python scripts/check_architecture.py /path/to/project
```

Run both current and completion-phase checks:

```bash
python scripts/check_architecture.py /path/to/project --completion
```

Completion-phase checks are useful for AndMar/Work Ledger: they may describe the required final state without failing before implementation begins.

## Work Ledger contract

The handoff always declares:

```json
{
  "work_ledger": {
    "policy": "decompose_do_not_reinterpret",
    "checkpoint_after_each_work_unit": true
  }
}
```

Work Ledger may create work units, dependencies, checkpoints, evidence requirements, resume state, and ordering. If implementation reveals evidence that invalidates the architecture contract, the work unit is blocked and the Architecture Harness must issue a revised architecture revision. Work Ledger must not silently redesign the project.

## Tool routing

The harness does not require a specific search/index stack. It uses the cheapest sufficient evidence source and reuses tooling already present in the target repository. `rg` or OpenCode grep is the normal textual-search default; tgrep is useful only when repeated indexed search amortizes its indexing cost; ast-grep is preferred for structural syntax questions; CodeGraph or codebase-memory-mcp are optional escalation tools for graph-level navigation or impact analysis in complex repositories. The harness should not run both graph tools by habit and should never index merely because a tool is installed.

## Self-test

The deterministic components use only Python's standard library.

```bash
python -m unittest discover -s tests -v
```

No Python package installation is required for the harness scripts.
