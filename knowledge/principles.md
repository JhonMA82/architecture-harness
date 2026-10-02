# Agent-First Architecture Principles

These principles are permanent evaluation criteria. They are not an architecture by themselves.

## 1. Framework-native first

Use the framework's canonical entry points, directories, lifecycle, generators, extension points, and testing conventions. A repository that remains recognizable to its ecosystem gives agents valuable prior knowledge. Improve architecture inside those constraints before inventing a parallel framework.

## 2. Minimum sufficient architecture

Architecture exists to reduce real complexity, not to display patterns. Every layer or abstraction must solve a current problem or enforce a current boundary.

## 3. Locality of behavior

Prefer an obvious owner for behavior. Physical locality is ideal when compatible with the ecosystem. Logical locality is acceptable when a framework requires canonical directories; use consistent naming, namespaces, maps, tests, and documentation to connect the pieces.

## 4. High cohesion, low coupling

A module should contain things that change for the same reason. Changes in one capability should not require unrelated modules to know its internals.

## 5. Small cognitive scope

A normal task should require a bounded amount of context. Measure the practical path an agent follows from request -> owner -> dependencies -> tests -> verification.

## 6. Explicit boundaries

Public APIs, ownership, allowed dependencies, forbidden dependencies, generated files, and framework-owned files should be explicit. Prefer mechanically enforceable rules where practical.

## 7. Deterministic verification

The repository should expose clear build/test/lint/typecheck/architecture commands. Agents should not need subjective judgment to know whether routine work is complete.

## 8. Progressive disclosure

Top-level instructions should be short and point to deeper context only when needed. Avoid giant instruction files that force every task to carry the entire architecture.

## 9. Preserve behavior during structural refactor

Architectural cleanup and feature change are separate concerns unless explicitly combined in the contract. Use characterization/smoke tests where needed.

## 10. Change surface matters

A small product request should normally have a small blast radius. If trivial changes routinely cross many layers or unrelated modules, investigate ownership and coupling.

## 11. Generated code must be obvious

Generated files should live in recognizable locations or carry clear conventions. Agents must know whether to edit source definitions or generated outputs.

## 12. No architecture change is a valid result

If the project is already predictable, local, verifiable, and ecosystem-native, recommend KEEP. Do not create churn.

## 13. Evidence economy

Use the cheapest sufficient source of evidence. Reuse project-native tooling before adding harness-specific analysis. Prefer targeted search over broad reading, and only pay the indexing/graph cost of tgrep, CodeGraph, or codebase-memory-mcp when the current question benefits from it. Tool absence must degrade gracefully, never block architecture work.
