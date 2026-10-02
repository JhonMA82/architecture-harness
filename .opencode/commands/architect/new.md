---
description: Design the final agent-first architecture for a new project from an idea or specification
agent: architect
subagent: false
---

Design a new project from `$ARGUMENTS`.

Required workflow:
1. Load the `architecture-design` skill.
2. Extract product archetype, stack/framework (if stated), deployment/runtime shape, persistence/data needs, integration boundaries, plugin/extensibility requirements, and operational constraints.
3. Load relevant `knowledge/ecosystems/*.md` references for the selected framework/stack.
4. Apply agent-first invariants automatically; never ask whether agent-first development is desired.
5. Select the minimum sufficient architecture and concrete repository organization.
6. Ask one question at a time only when a material product decision cannot be inferred and would change architecture.
7. Write/update `.work/current.json` with mode=`new`, project summary, architecture, resolved material decisions, unresolved material questions, proposed destination if known, and `ready_to_finalize`.
8. Present the decided architecture and any remaining material decision.

Do not create application source code. Final artifacts are written only by `/architect/finalize`.
