---
name: safe-refactoring
description: Design behavior-preserving, incremental architecture refactors for existing projects
---

# Safe Refactoring

Use only after assessment proves ORGANIZE or RESTRUCTURE is justified.

## Primary rule

For structural refactors, preserve observable behavior unless the architecture contract explicitly includes a behavior change.

## Refactoring workflow

1. Establish the baseline: existing tests/checks plus characterization or smoke tests for risky behavior that is not covered.
2. Identify a **seam**: a boundary where responsibility can be extracted without rewriting the system. Use project-native search/graph tooling for impact evidence when useful; follow `knowledge/tooling.md` and do not index by default.
3. Define the final target ownership and dependency direction before moving code.
4. Extract one coherent responsibility at a time.
5. Verify after each extraction.
6. Keep old entry points delegating to the new implementation when necessary until callers are migrated.
7. Remove obsolete paths only after no callers remain. Confirm callers with the cheapest sufficient evidence source (`rg`/tgrep/ast-grep/CodeGraph/CBM as appropriate) rather than relying on memory.
8. Stop when the final architecture contract is satisfied; do not continue “cleaning” unrelated code.

## Patterns

### Strangler Fig

Gradually replace or extract responsibilities while the application remains operational. Appropriate for God Objects, legacy subsystems, and large modules that can delegate to new components.

### Seams

Introduce or use an existing boundary where behavior can be redirected or tested without invasive changes. Examples: a service call, action object, interface, event, command handler, or UI signal/slot boundary.

### Characterization tests

Tests that capture current behavior before structural change. Use when behavior matters but existing tests are insufficient. They protect behavior; they are not an excuse to freeze known bugs when bug fixing is part of the request.

### Branch by Abstraction

Introduce a stable interface around a dependency or subsystem, migrate callers, then replace the implementation behind it. Use only when many callers make direct replacement risky.

### Parallel Change / Expand-Contract

Add the new compatible shape, migrate consumers, then remove the old shape. Useful for APIs, schemas, event contracts, or public interfaces.

## What not to do

- Do not rewrite a working core to make directory structure prettier.
- Do not combine packaging migration, framework migration, UI redesign, and architectural extraction unless the final contract explicitly requires all of them and their risks are independently verifiable.
- Do not create large “refactor everything” work units.
- Do not use file size as the sole extraction criterion.
- Do not silently change architecture while implementing. New evidence that invalidates the contract must return to the Architecture Harness for a revised contract.

## Handoff to Work Ledger

The final architecture contract defines the destination. Work Ledger may decompose that contract into Work Units with dependencies, checkpoints, evidence, and resume state. It must not reinterpret or change architectural decisions.
