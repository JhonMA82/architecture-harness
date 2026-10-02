---
description: Analyze an existing project from a local path or Git URL and establish an agent-first architecture session
agent: architect
subagent: false
---

Analyze the existing project target supplied in `$ARGUMENTS`.

Required workflow:
1. Treat `$ARGUMENTS` as either a local project path or a Git repository URL.
2. Load the `project-assessment` skill.
3. Run `python scripts/inspect_project.py "$ARGUMENTS" --json --write .work/inspection.json` (use python3 if needed).
4. Read `knowledge/tooling.md`. Use the inspection's `analysis_tools`, scale, Git churn, and project-native tooling hints to choose the cheapest sufficient evidence source; do not index by default.
5. Use the inspection as evidence, then read only the files required to validate architecture, hotspots, framework conventions, locality, and dependency boundaries.
6. Load the matching `knowledge/ecosystems/*.md` reference if one exists.
7. Classify the intervention as KEEP, ORGANIZE, or RESTRUCTURE.
8. If ORGANIZE or RESTRUCTURE, load `safe-refactoring` and define the target architecture and safe migration approach.
9. Write/update `.work/current.json` with the target, mode=`existing`, materialized path if any, evidence summary, intervention, target architecture, resolved material decisions, unresolved material questions, and `ready_to_finalize`.
10. Present a concise assessment and only ask one question if a material architectural decision truly requires human intent. Otherwise continue to a concrete proposal.

Do not modify the target project's source code. Do not finalize unless the user asks or invokes `/architect/finalize`.
