# Refactoring Patterns for Agent-First Migration

## Strangler Fig

Replace or extract a legacy responsibility incrementally while the system keeps operating. Keep stable entry points delegating to the new component until migration is complete.

Good for God Objects, large UI coordinators, legacy subsystems, and gradual module extraction.

## Seam

A place where behavior can be redirected, isolated, or tested without invasive change. A seam may be an existing signal/slot, service call, interface, command handler, route, adapter, or function boundary.

Use seams before introducing broad architecture machinery.

## Characterization Test

Capture current externally observable behavior before structural refactoring when existing tests are insufficient. The goal is safe preservation, not endorsement of accidental behavior.

## Branch by Abstraction

Introduce a stable abstraction around a dependency with many callers, migrate callers behind it, then replace the implementation. Useful when direct replacement would create a large blast radius.

Avoid for one or two callers where direct extraction is simpler.

## Parallel Change / Expand-Contract

1. Add a backward-compatible new shape.
2. Migrate consumers.
3. Remove the old shape.

Useful for APIs, data schemas, event contracts, configuration formats, and public interfaces.

## Composition Root Extraction

Move assembly/wiring out of feature implementations into one clear application composition location. Particularly useful when a MainWindow, bootstrap file, or controller currently both wires and implements product behavior.

## Dependency Direction Repair

When a lower-level/core module imports UI or feature implementation, move the contract toward the stable side or relocate the responsibility. Do not introduce an interface unless it resolves an actual reversed dependency.

## Stop condition

A refactor stops when the final architecture contract and its completion criteria are satisfied. "While we are here" cleanup is outside scope unless separately justified.
