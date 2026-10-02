---
name: project-assessment
description: Inspect and classify an existing repository before recommending architecture changes
---

# Project Assessment

Use this skill for existing projects only.

## Goal

Determine the actual architecture, framework constraints, agent friction, and intervention level from evidence. Do not start by proposing a preferred pattern.

## Required sequence

1. Run the deterministic inspector first.
2. Read `knowledge/tooling.md` and use the inspector's `analysis_tools`, repository scale, Git churn, and project-native tooling signals to choose the cheapest sufficient evidence source. Do not index by default.
3. Identify the project archetype and framework/ecosystem.
4. Read only the files needed to validate the most relevant structural signals. Prefer project-native tools and targeted search before broad source reading.
5. Map current responsibilities, entry points, shared core, feature/application workflows, persistence, integrations, and UI composition where applicable.
6. Trace representative normal changes through the repository and record their agent-locality path: starting point, owner, directories crossed, unrelated context required, and verification path.
7. Evaluate architecture using the complete agent-first fitness set below. Dependency health is only one dimension.
8. Identify ownership failures, including generic workflow/service/handler modules that would become dumping grounds if more unrelated behavior were extracted into them.
9. Classify the intervention as KEEP, ORGANIZE, or RESTRUCTURE.
10. State what must be preserved before stating what should change.

## Agent-friction criteria

Evaluate concrete evidence for:

- **Discoverability** — can an agent find the owner of a behavior quickly?
- **Cognitive scope** — how much unrelated context is needed for a normal change?
- **Locality** — is behavior physically or logically grouped by ownership?
- **Coupling** — do unrelated modules change together or reach into internals?
- **Cohesion** — does each module have a focused reason to change?
- **Boundary clarity** — are public APIs and dependency directions obvious?
- **Change surface / blast radius** — does a small request require touching many layers/files?
- **Verification** — are build/test/check commands explicit and deterministic?
- **Generated-code clarity** — can agents distinguish generated and human-owned code?
- **Framework recognizability** — does the repository still look like its ecosystem?

### Architecture fitness rule

Do not infer that an architecture is agent-friendly merely because imports are acyclic or dependency direction is healthy. Before preserving the current organization, assess all of:

1. framework fit;
2. dependency health;
3. cohesion;
4. agent locality;
5. cognitive scope;
6. change surface;
7. discoverability;
8. deterministic verification.

A materially weak result in locality/cognitive scope/change surface may justify selective structural change even when dependency direction is already good.

## Intervention classification

### KEEP

Use when the current structure already supports predictable agent work. Targeted improvements may include AGENTS.md, explicit verification commands, one local extraction, or architecture checks without changing the architectural organization.

### ORGANIZE

Use when the fundamental architecture is valid but locality, ownership, composition, or boundaries need improvement. This may include introducing **selective feature owners** while preserving a healthy shared core and framework-native infrastructure. Examples: decomposing a God Object, extracting self-contained workflows into explicit feature ownership, creating feature slices only where normal changes benefit from locality, clarifying dependency direction.

### RESTRUCTURE

Use only when evidence shows the current architectural model itself creates recurring friction: pervasive cycles, fundamentally misplaced boundaries, framework conventions actively violated, deployment requirements incompatible with the current design, or widespread cross-cutting coupling that cannot be corrected locally.

## Evidence rules

- Large LOC is a signal, not a verdict.
- A directory name is not proof of architecture.
- Do not recommend moving files solely to match a fashionable layout.
- Do not assume `src/` is automatically superior.
- Do not replace framework-native structure for aesthetic consistency.
- Prefer concrete examples of normal changes that currently have excessive scope.
- Do not replace a God Object with a generic `workflows`, `services`, `handlers`, `helpers`, or `common` module containing unrelated product capabilities.
- Treat physical and logical locality as first-class evidence. Framework-native scattering can be valid when logical ownership is explicit; arbitrary horizontal scattering is not automatically valid.
- Shared core/infrastructure and feature slices may coexist. Do not treat layered organization and feature ownership as mutually exclusive.

## Assessment output

Return:

- project archetype;
- stack/framework;
- current architecture in plain language;
- decisive evidence;
- agent-friction hotspots;
- representative agent-locality paths for normal changes;
- ownership map: current owners, ambiguous owners, and capabilities needing explicit ownership;
- intervention: KEEP / ORGANIZE / RESTRUCTURE;
- preserve list;
- target architecture if change is justified;
- material unresolved decisions only.
