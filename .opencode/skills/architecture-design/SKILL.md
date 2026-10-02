---
name: architecture-design
description: Select the minimum sufficient agent-first architecture and repository structure for a new project
---

# Architecture Design

Use for new projects or when an existing-project assessment has already proven that a target architecture must be designed.

## Permanent premise

The project will be developed 100% with AI agents. Do not ask whether to optimize for agents.

## Decision order

1. **Project archetype** — desktop GUI, API, web app, library, CLI, compiler, data pipeline, plugin host, monorepo, etc.
2. **Framework constraints** — preserve framework-native structure and extension points.
3. **Runtime/deployment shape** — one process, client/server, offline, multi-user, independently deployed components, background workers, etc.
4. **Product boundaries** — capabilities that evolve independently and shared domain/core responsibilities.
5. **Data/integration constraints** — persistence, external services, files, queues, hardware, platform APIs.
6. **Agent ergonomics** — locality, cognitive scope, change surface, discoverability, explicit boundaries, deterministic verification.
7. **Ownership test** — every user-facing capability must have one obvious owner; decide whether that owner is framework-native logical locality, a cohesive shared module, or a selective feature slice.
8. **Minimum sufficient pattern** — choose only as much architecture as the evidence requires.

## Pattern selection guidance

- **Simple package/module layout**: small utilities, focused CLIs, compact applications.
- **Domain/package-oriented library**: libraries where public APIs and conceptual domains matter more than UI features.
- **Pipeline**: compilers, ETL/data processing, transformation stages.
- **Framework-native layered/modular**: strong-convention ecosystems where physical feature locality would fight tooling or conventions.
- **Modular Monolith + selective Feature Slices**: substantial single-deployment applications with multiple product capabilities and shared core/domain behavior.
- **Plugin architecture**: only when extensions genuinely need independent discovery/evolution or third-party installation.
- **Ports/adapters**: when multiple replaceable external systems or isolation from volatile infrastructure has demonstrated value.
- **Distributed/microservices**: only for concrete independent deployment, scaling, ownership, isolation, or regulatory needs.

Patterns may be combined. Do not force everything into feature slices. Shared cross-feature primitives can remain domain/core modules when that improves cohesion.


## Selective feature-ownership rule

Do not decide between "layered" and "feature-sliced" as mutually exclusive choices.

Use a hybrid when evidence supports it:
- keep cohesive shared domain/core primitives, framework infrastructure, format layers, rendering kernels, tool frameworks, and other genuinely cross-feature capabilities in shared modules;
- give independent user-facing workflows/capabilities an explicit local owner when that materially reduces agent exploration and change surface;
- keep framework-owned files in canonical framework locations and provide logical ownership when physical movement would fight the ecosystem.

A user-facing workflow deserves a selective feature owner when several are true:
- it has a recognizable product name/capability;
- it evolves independently from neighboring workflows;
- a normal change currently crosses multiple technical directories;
- it coordinates UI plus domain/integration behavior;
- its tests can be scoped locally;
- a feature owner would reduce cognitive scope without duplicating shared infrastructure.

Do **not** create a catch-all `workflows.py`, `services.py`, `handlers.py`, or similar module for unrelated capabilities. Such a module is a transitional seam at most, never the final owner of heterogeneous product behavior.

## Agent-first structure requirements

A final design should make these questions easy to answer:

- Where does a new feature or user-facing workflow belong?
- What single owner should an agent open first for that capability?
- What is the public entry point for this module?
- What may this module depend on?
- What is forbidden?
- Where are its tests?
- What command proves the change is correct?
- Which files are generated or framework-owned?

Prefer physical locality when compatible with the ecosystem. When framework conventions scatter a feature across canonical directories, create **logical locality** through naming, maps, namespaces, tests, and explicit ownership rather than fighting the framework.

## Overengineering guardrails

Do not add a layer, abstraction, service, repository, event bus, DI container, plugin system, package boundary, or deployment unit without a current consumer and concrete reason.

Do not generate empty directories for hypothetical future needs.

The final architecture must explain its non-goals explicitly so future agents do not reintroduce rejected complexity.
