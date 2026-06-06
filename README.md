# Oracle Fusion Agent Skills

Reusable Agent Skills for Oracle Fusion SQL review and optimization.

## Included Skills

### oracle-fusion-query-optimizer

Reviews and rewrites Oracle Fusion ERP/HCM SQL using:

- Oracle Fusion table documentation
- Table DDL, keys, and indexes
- BI Publisher best practices
- Optional Oracle SQL Tuning Advisor text reports
- Ranked improvement suggestions
- Approval-based V2 query creation

## Install With GitHub CLI

```bash
gh skill install AbhishekAithal1207/oracle-fusion-agent-skills skills/oracle-fusion-query-optimizer
```

For Claude Code:

```bash
gh skill install AbhishekAithal1207/oracle-fusion-agent-skills skills/oracle-fusion-query-optimizer --agent claude-code --scope user
```

## Manual Install

Copy this folder:

```text
skills/oracle-fusion-query-optimizer/
```

to one of these locations.

Claude Code:

```text
~/.claude/skills/oracle-fusion-query-optimizer/
```

VS Code Copilot project skill:

```text
.github/skills/oracle-fusion-query-optimizer/
```

or:

```text
.agents/skills/oracle-fusion-query-optimizer/
```

Cursor:

```text
.cursor/skills/oracle-fusion-query-optimizer/
```

Antigravity:

```text
.agents/skills/oracle-fusion-query-optimizer/
```

Codex:

```text
~/.codex/skills/oracle-fusion-query-optimizer/
```

## Example Prompt

```text
Use oracle-fusion-query-optimizer to review this Oracle Fusion BI Publisher SQL. Check table docs, indexes, DDL, and SQL Tuning Advisor evidence if available. Give ranked suggestions first, then create a V2 query only after I approve the change IDs.
```

## Safety

Do not commit private SQL, credentials, tuning advisor reports, schema extracts, customer data, or company-specific DDL into this public repository.
