# Architecture Anti-Patterns and Agent Friction

## God Object / God Module

One class/module owns unrelated composition, workflows, persistence, UI, integration, and domain responsibilities. Large size is often present but responsibility mix is the actual problem.

## Layer scattering

A single feature requires navigation through controllers/services/models/validators/repositories/views with little independent value in each layer. Strong framework conventions may justify this; otherwise prefer better locality.

## Shared-utils dumping ground

`utils`, `helpers`, or `common` accumulates unrelated behavior with unclear ownership. Move behavior to its real owner; keep shared utilities truly generic and stable.

## Workflow/service dumping ground

`workflows.py`, `services.py`, `handlers.py`, `managers.py`, or equivalent accumulates unrelated product capabilities extracted from a former God Object. This reduces the original file size but preserves poor ownership and cognitive scope. Use an explicit capability/feature owner when workflows have independent product identity; keep a generic module only for truly cohesive shared orchestration.

## Architecture by directory name

Creating `domain/`, `services/`, `features/`, or `modules/` without real dependency boundaries or ownership rules. Structure must match behavior.

## Abstraction before consumer

Interfaces, repositories, factories, adapters, event buses, or plugin points created for hypothetical futures. Add when a real second implementation/consumer or isolation need exists.

## Framework inversion

Reorganizing a strong-convention framework until normal framework tooling and ecosystem knowledge no longer apply. Prefer native extension points.

## UI contains product/domain behavior

Event handlers or widgets implement substantial domain calculations, persistence, import/export, or workflows. Keep UI as interaction/composition where practical.

## Hidden global state

Behavior depends on mutable singletons or implicit module state that is difficult to identify or test. Prefer explicit ownership/lifecycle where the current stack permits.

## Giant instruction file

Every agent task loads all project knowledge. Use short top-level instructions with references and local docs for progressive disclosure.

## Non-deterministic completion

A task is "done" when the model feels it is done. Replace with explicit checks, tests, build commands, smoke tests, and architecture invariants where practical.

## Rewrite reflex

Replacing a working subsystem because the target pattern looks cleaner. Prefer incremental extraction unless the current foundation is genuinely incompatible with requirements.

## Tooling escalation by habit

Running every available indexer, graph tool, MCP, or search engine on every repository. This adds latency, state, and failure modes without improving the decision. Use the cheapest sufficient evidence source; index only when repeated or graph-level questions justify it.

## Duplicate code intelligence

Building a custom semantic graph/index inside the harness when project-native tools, CodeGraph, codebase-memory-mcp, language tooling, or structural search already answer the question. Keep the harness inspector cheap and observational.
