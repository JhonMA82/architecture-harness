# OpenCode v2 Project Guidance

Use current v2 conventions for harnesses and agent tooling.

## Agents

Project agents live under `.opencode/agents/*.md`. Markdown frontmatter defines fields such as description, mode, permissions, and steps; the body is the system prompt. Prefer v2 permission/action names.

## Commands

Project slash commands live under `.opencode/commands/`. Nested paths create names such as `.opencode/commands/architect/analyze.md` -> `/architect/analyze`. `$ARGUMENTS` carries the full command arguments.

## Skills

Directory skills live under `.opencode/skills/<skill-id>/SKILL.md`. Keep the entry skill concise and load supporting references only when needed.

## Instructions

Use `AGENTS.md` for persistent project instructions and verification requirements. Keep it concise enough to be useful on every session.

## Permissions

OpenCode v2 uses ordered permission rules with actions such as `read`, `edit`, `shell`, `subagent`, `skill`, `webfetch`, `websearch`, and `external_directory`. Prefer narrow shell/edit permissions. Access outside the active workspace requires external-directory approval unless explicitly allowed.

## References

OpenCode v2 can expose external local directories or Git repositories as references, but references do not bypass permissions. This harness accepts paths/URLs directly and uses deterministic inspection; references remain useful for manually attached supporting material.
