---
description: Finalize the current architecture into decisive instructions and a machine-readable handoff
agent: architect
subagent: false
---

Finalize the current architecture session.

Required workflow:
1. Read `.work/current.json` and `.work/inspection.json` if present.
2. If a truly material unresolved decision remains, ask exactly that question and do not fabricate a choice. Otherwise continue without asking.
3. Load the `architecture-handoff` skill.
4. Produce exactly two final contract artifacts:
   - `ARCHITECTURE.md`
   - `.architecture/handoff.json`
5. For an existing local target, write them to the target project root (external-directory approval may be required).
6. For a Git URL analyzed through the harness cache, or for a new project without a destination path, write them under `output/<project-slug>/` preserving the `.architecture/` subdirectory.
7. Validate the JSON against `schemas/handoff.schema.json` semantically and run `python scripts/check_architecture.py <output-or-target>` when the handoff declares architecture checks that are already applicable.
8. Update `.work/current.json` with `finalized=true`, output paths, and architecture revision `1` unless an explicit prior revision exists.

Finalization is decisive: no roadmap language, no unresolved recommendations, no implementation source-code changes.
