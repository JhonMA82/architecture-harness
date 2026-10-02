# Architecture Pattern Catalog

This is a bounded catalog for decision support, not a menu that must be combined.

## Simple package/module layout

**Use when:** small CLI, utility, compact service, single-purpose application.

**Shape:** a few cohesive modules with direct dependencies and obvious entry points.

**Agent benefit:** minimal navigation and little ceremony.

**Avoid when:** multiple capabilities evolve independently and ownership is becoming ambiguous.

## Framework-native layered/modular

**Use when:** the framework has strong conventions that tooling and developers expect, such as Laravel, Rails, Django, or similar ecosystems.

**Shape:** preserve canonical framework directories, then improve domain/module ownership inside flexible areas.

**Agent benefit:** maximizes prior ecosystem knowledge and tooling compatibility.

**Risk:** feature behavior may be physically scattered. Counter with logical locality, naming, tests, and maps rather than fighting the framework.

## Modular Monolith

**Use when:** one deployable application has several meaningful internal capabilities/domains.

**Shape:** one runtime/deployment unit with explicit modules and dependency boundaries.

**Agent benefit:** local reasoning without distributed-system overhead.

**Risk:** becomes a directory-only label if module boundaries are not real.

## Feature Slices / Vertical Slices

**Use when:** product capabilities are the natural unit of change and physical locality helps agents understand a feature with few files.

**Shape:** feature-owned UI/application/domain/test code grouped together where the ecosystem permits.

**Agent benefit:** request -> feature owner is obvious; reduced context gathering.

**Do not:** force shared primitives, geometry kernels, compiler stages, framework-owned files, or universal infrastructure into artificial feature folders.

## Hybrid Modular Monolith + selective Feature Slices

**Use when:** a substantial application has a cohesive shared core plus product capabilities that benefit from local ownership.

**Example shape:**

```text
core/          shared domain/CAD/runtime primitives
formats/       shared file capability
plugins/       extension mechanism
features/      product/application slices
ui/            thin composition when needed
```

This is often appropriate for desktop/CAD/business applications but is not a universal default.

## Domain/package-oriented library

**Use when:** the artifact is a reusable library and public API/domain concepts matter more than end-user feature workflows.

**Shape:** packages by domain concept, stable exports, internal implementation hidden behind public modules.

## Pipeline

**Use when:** behavior naturally flows through ordered stages (compiler, ETL, media processing, data transformation).

**Shape:** explicit stages with typed/defined contracts between them.

**Agent benefit:** easy to locate where transformation responsibility belongs.

## Plugin architecture

**Use when:** extensions must be independently discovered, installed, enabled, or maintained, especially by third parties.

**Do not use:** merely to avoid adding code to the main application.

## Ports and adapters / hexagonal boundaries

**Use when:** volatile external systems, multiple implementations, testing isolation, or platform substitution create concrete value.

**Agent benefit:** stable domain contracts and limited infrastructure coupling.

**Risk:** excessive interfaces/mappers/DTOs when there is only one stable implementation.

## Distributed services / microservices

**Use only when concrete requirements demand independent deployment, scaling, failure isolation, ownership, regulatory boundaries, or technology/runtime separation.**

Do not choose this pattern for code organization alone; a modular monolith provides code boundaries without network/distribution cost.
