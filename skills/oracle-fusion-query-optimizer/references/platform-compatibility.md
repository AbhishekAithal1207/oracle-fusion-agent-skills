# Platform Compatibility

This skill follows the Agent Skills `SKILL.md` structure: a folder containing `SKILL.md` plus optional `scripts/`, `references/`, and `assets/`. The same folder can be reused across compatible tools.

## Recommended Install Locations

| Platform | Project skill location | Personal/global location | Notes |
| --- | --- | --- | --- |
| Codex | `.codex/skills/oracle-fusion-query-optimizer/` or a configured shared skill location | `~/.codex/skills/oracle-fusion-query-optimizer/` | The current folder is already a Codex skill package. |
| Claude Code | `.claude/skills/oracle-fusion-query-optimizer/` | `~/.claude/skills/oracle-fusion-query-optimizer/` | Claude Code uses `SKILL.md` with YAML frontmatter. |
| VS Code Copilot | `.github/skills/oracle-fusion-query-optimizer/`, `.claude/skills/`, or `.agents/skills/` | `~/.copilot/skills/`, `~/.claude/skills/`, or `~/.agents/skills/` | VS Code supports Agent Skills and shared skill locations. |
| Cursor | `.cursor/skills/oracle-fusion-query-optimizer/` or shared `.agents/skills/oracle-fusion-query-optimizer/` | `~/.cursor/skills/oracle-fusion-query-optimizer/` or `~/.agents/skills/` | Cursor also supports project rules, but skills are better for on-demand workflows. |
| Antigravity | `.agents/skills/oracle-fusion-query-optimizer/` | `~/.gemini/antigravity-cli/skills/oracle-fusion-query-optimizer/` | Antigravity supports workspace skills under `.agents/skills/`; plugins can also contain `skills/`. |

For maximum portability in a repo, place this entire folder at:

```text
.agents/skills/oracle-fusion-query-optimizer/
```

## Cross-Platform Constraints

- Keep the folder name and `name` frontmatter identical.
- Use only lowercase letters, numbers, and hyphens in the skill name.
- Keep `description` specific because agents use it for activation.
- Reference supporting files from `SKILL.md` with relative paths.
- Keep scripts self-contained and avoid platform-specific shell syntax when possible.
- Do not depend on a single agent's proprietary frontmatter fields unless there is a fallback.

## Optional Always-On Companion Rules

If a tool does not auto-load skills reliably, add a short rule/custom instruction:

```md
When reviewing Oracle Fusion, BI Publisher, ERP Financials, or HCM SQL, use the oracle-fusion-query-optimizer Agent Skill. Follow its approval gate: produce ranked suggestions first, then create a separate V2 SQL only after approval.
```

Use this as:

- VS Code: `.github/copilot-instructions.md` or an `.instructions.md` file.
- Cursor: `.cursor/rules/oracle-fusion-query-optimizer.mdc`.
- Antigravity: `.agents/rules/oracle-fusion-query-optimizer.md`.
- Claude: `CLAUDE.md` when a project-level always-on reminder is needed.
