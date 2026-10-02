# Evidence Tool Routing

Architecture Harness uses tools to gather evidence, not to outsource architecture decisions.

## Permanent rule

Use the **cheapest sufficient source of evidence**. Prefer existing project-native tooling and deterministic local queries before heavyweight indexing or broad agent exploration.

A tool being installed is not a reason to use it. A repository being large is not, by itself, a reason to index it. Escalate only when the current architectural question cannot be answered cheaply and reliably.

## Default routing order

1. **Project-native tooling** — existing scripts, linters, test commands, architecture rules, Make/Just/Task targets, framework CLIs, CI commands.
2. **Filesystem + Git** — manifests, tree, file sizes, ownership clues, history/churn, changed-together evidence.
3. **ripgrep (`rg`) / OpenCode grep** — exact names, strings, import sites, config references, call-site candidates.
4. **tgrep** — repeated regex/text search in a large repository when an index will amortize its cost. Do not build an index for a few one-off searches.
5. **ast-grep** — structural syntax queries or existing structural rules when text matching is too imprecise.
6. **CodeGraph or codebase-memory-mcp** — graph-level questions such as cross-module relationships, call/dependency paths, impact analysis, or repeated structural navigation in a large/complex repository.
7. **Direct broad agent exploration** — only for questions the available deterministic/search/graph tools cannot establish.

This is a routing policy, not a mandatory pipeline. Skip levels when the question clearly requires a later capability.

## Tool-specific guidance

### ripgrep

Default textual search when the target is local and no project-native search is better. Scope searches by directory/file type when possible. Prefer several precise searches over reading broad directories.

### tgrep

Use when all are true:
- repository/search corpus is large enough that repeated scans are costly;
- multiple regex/text searches are expected;
- index build/refresh cost is justified by the session.

Do not require tgrep. If it is unavailable, use `rg`. Do not trust a stale index for a freshness-sensitive query without confirming current files.

### ast-grep

Use for syntax-aware questions such as:
- forbidden import/call forms;
- framework API usage patterns;
- structural searches that would be noisy with regex;
- existing project architecture rules already expressed as ast-grep rules.

Prefer existing project rules before creating new ones.

### CodeGraph

Use an available CodeGraph integration when graph navigation materially reduces exploration: symbol relationships, dependency/call paths, ownership boundaries, or impact questions. Do not make CodeGraph a required dependency and do not build a duplicate graph in the harness when the installed tool already answers the question.

### codebase-memory-mcp (CBM)

Use CBM when persistent/repeated graph queries or impact analysis justify indexing. Before indexing, check whether the project is already indexed. When indexing is required, surface progress and avoid launching duplicate indexes. Do not index a small repository merely because CBM is available.

CodeGraph and CBM are alternatives/complements, not a mandatory pair. Use one sufficient graph source by default; use both only when they provide materially different evidence for the current question.

## Failure and fallback behavior

Tool absence must never block architecture work.

- no `rg` -> use OpenCode grep or available equivalent;
- no `tgrep` -> use `rg`;
- no ast-grep -> use targeted text/AST inspection where adequate;
- no CodeGraph/CBM -> inspect targeted source and project-native dependency tools;
- graph indexing fails or stalls -> fall back rather than repeatedly retrying.

## What the deterministic inspector owns

`scripts/inspect_project.py` should remain small. It owns cheap facts:
- repository scale and structure;
- language/framework/manifests;
- tests/CI/tooling hints;
- file/AST hotspots where cheaply available;
- local Git churn/history signals;
- availability/configuration hints for analysis tools.

It does **not** implement a universal semantic index, embeddings, a persistent code graph, or architecture scoring.

## Decision boundary

Tools may establish facts such as:
- file A changes frequently;
- package X imports package Y;
- symbol P has these callers;
- a feature touches these directories;
- a rule is already enforced by ast-grep.

Tools must not decide that the project "should use feature slices" or "should migrate to hexagonal architecture". The `architect` makes that decision from product constraints, ecosystem conventions, and evidence.
