---
description: Show the current architecture session status without re-analyzing the project
agent: architect
subagent: false
---

Read `.work/current.json` and report the current architecture session succinctly.

Include:
- mode and target/project;
- current intervention classification if existing project;
- selected target architecture;
- decisive evidence/findings;
- resolved material decisions;
- unresolved material decisions, if any;
- whether it is ready to finalize;
- final output destination if known.

Do not rerun inspection or reopen resolved decisions unless `.work/current.json` is missing or explicitly stale.
