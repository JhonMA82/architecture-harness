---
name: architecture-handoff
description: Convert a resolved architecture session into final instructions and a machine-readable contract for OpenCode, AndMar, and Work Ledger
---

# Architecture Handoff

Use only when the architecture is resolved enough to execute.

## Required outputs

Produce exactly two final contract artifacts:

1. `ARCHITECTURE.md`
2. `.architecture/handoff.json`

## ARCHITECTURE.md standard

This is a final instruction document, not a brainstorming note and not a roadmap of future architectural decisions.

For an existing project include:

- Context and constraints
- Current architecture
- Evidence and agent-friction findings
- Intervention: KEEP / ORGANIZE / RESTRUCTURE
- Final target architecture
- Final repository structure
- Ownership and responsibilities, including explicit owners for user-facing workflows/capabilities
- Allowed/forbidden dependencies
- Framework/ecosystem conventions to preserve
- Migration/refactor instructions
- Verification
- Non-goals / forbidden overengineering
- Completion criteria

For a new project omit current-state/refactor sections and give the final structure directly.

Use decisive language. Do not leave choices such as "consider", "maybe", or "evaluate later" when a decision belongs in the contract.

## handoff.json standard

Must validate conceptually against `schemas/handoff.schema.json`.

It contains executable facts, not prose discussion:

- schema and architecture revision;
- project archetype/framework;
- intervention for existing projects;
- architecture pattern and organization;
- preserve/change/non-goal lists;
- explicit ownership map for important capabilities/workflows;
- module boundaries and dependency rules;
- migration strategy where applicable;
- verification commands;
- optional machine-checkable architecture checks;
- completion criteria;
- Work Ledger policy: decompose but do not reinterpret.

### Ownership contract

When a capability has a meaningful product identity, emit an `ownership` entry mapping that capability to its final owner path/module. Do not map unrelated capabilities to a generic dumping-ground module. Shared infrastructure does not need fake feature ownership; only record ownership where it improves execution clarity.

Example:

```json
{
  "ownership": {
    "orders": "app/Domain/Orders",
    "reporting": "features/reporting",
    "editor": "ui/editor"
  }
}
```

### Scope of non-goals

Treat non-goals as **constraints for the current architecture contract** unless the project itself proves they are permanent invariants. Use decisive wording such as `Current contract non-goal: do not split core/history.py; current evidence does not justify it.` Do not accidentally freeze a module forever merely because it is out of scope for this refactor.

## Architecture checks

Only emit checks supported by `scripts/check_architecture.py` and only when they are useful:

- `require_path`
- `forbid_path`
- `forbid_python_import`

Do not manufacture checks just to populate the list.

## Final consistency checks

Before writing:

- every `preserve` item agrees with the migration instructions;
- dependency rules agree with the proposed tree;
- verification commands are appropriate to the actual stack;
- framework-native conventions are not contradicted;
- no rejected architecture reappears indirectly;
- no God Object has merely been replaced by a generic workflow/service/handler dumping ground;
- every significant user-facing workflow has a clear final owner (physical or logical);
- non-goals are scoped to the current contract unless explicitly permanent;
- Work Ledger can decompose the contract without making new architectural choices.
