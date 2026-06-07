---
name: oracle-fusion-query-optimizer
description: Review and rewrite Oracle Fusion SaaS SQL for BI Publisher, OTBI extracts, ERP Financials, HCM, Procurement, and SCM tables. Use when asked to tune, optimize, refactor, validate, or create a V2 version of Oracle Fusion SQL using table DDL, Oracle documentation, indexes, explain plans, bind parameters, or BI Publisher performance best practices.
---

# Oracle Fusion Query Optimizer

Use this skill to review Oracle Fusion SQL with source-backed caution: inspect table metadata, DDL, indexes, bind parameters, BI Publisher constraints, and module-specific behavior for Financials, HCM, Procurement, and SCM before suggesting or writing changes.

## Required Workflow

1. Preserve the original query.
2. Gather context:
   - SQL text or SQL file.
   - Target module: Financials/ERP, HCM, SCM, Projects, Procurement, or unknown.
   - Execution surface: BI Publisher data model, OTBI/analysis SQL, extract, ad hoc SQL, or unknown.
   - User-provided DDL, table descriptions, indexes, row counts, explain plan, SQL Monitor, sample bind values, and expected result rules.
   - Optional but strongly preferred: Oracle SQL Tuning Advisor text report, SQL Monitor report, or BI Publisher diagnostic tuning output for the same SQL and bind values.
3. When the user has not supplied a tuning report, ask once for it as optional evidence: `If you have the Oracle SQL Tuning Advisor .txt report for this SQL, share it too; I can use its findings, estimated benefits, and explain-plan sections to rank recommendations more accurately.`
4. Extract table names and aliases. For long SQL, run `scripts/fusion_sql_review.py --sql-file <file>` to produce a starter review skeleton. If a SQL Tuning Advisor report is available, run `scripts/fusion_sql_review.py --sql-file <file> --advisor-file <txt-file>`.
5. Read the relevant references only as needed:
   - [Review rubric](references/review-rubric.md) for ranking, required output tables, approval gates, and V2 behavior.
   - [Oracle Fusion source discovery](references/source-discovery.md) for official table documentation lookup across Financials, HCM, Procurement, and SCM.
   - [Fusion SQL performance patterns](references/fusion-sql-performance.md) for BI Publisher and Oracle SQL tuning checks.
   - [SQL Tuning Advisor reports](references/sql-tuning-advisor.md) when the user provides a tuning advisor `.txt`, SQL ID, SQL Monitor/Tuning Advisor finding, or advisor recommendation.
   - [Platform compatibility](references/platform-compatibility.md) when the user asks how to install or reuse this skill across Codex, Claude, VS Code, Cursor, or Antigravity.
6. Prefer official Oracle docs for table metadata and SQL Tuning Advisor interpretation. Use web/browser search when table documentation, current release pages, report format, or best-practice details are not already provided. If web is unavailable, ask the user for the needed DDL/index/report excerpts.
7. Compare the SQL against table primary keys, foreign keys, active indexes, obsolete indexes, composite index leading columns, date-effective keys, module-specific filters, and any SQL Tuning Advisor evidence such as findings, recommended actions, estimated benefit, original/new plan, cardinality mismatch, stale statistics, access-path issues, or SQL profile advice.
8. Ask concise clarification questions before recommending changes when semantics are ambiguous, such as:
   - Required output grain and duplicate handling.
   - Whether outer joins must preserve unmatched rows.
   - Whether inactive, historical, future-dated, or terminated HCM records are expected.
   - Whether parameters can be mandatory.
   - Whether the query runs in BI Publisher and must obey data model limitations.
   - Whether SQL Tuning Advisor recommendations can be implemented by a DBA, or whether only SQL text changes are allowed in the report/data model.
9. Produce a review first. Do not rewrite the SQL yet.
10. Present a ranked change table and ask the user to approve the rows to apply.
11. After approval, create a new V2 query only. Never overwrite the original unless explicitly requested.

## Review Output Contract

Return these sections in order:

1. `Context Checked` - list SQL source, docs/DDL/indexes reviewed, missing evidence, and assumptions.
2. `Questions Before Rewrite` - only include blockers or high-value clarifications.
3. `Ranked Change Suggestions` - a Markdown table with:
   - `ID`
   - `Rank`
   - `Area`
   - `Evidence`
   - `Suggestion`
   - `Expected Improvement`
   - `Behavior Change Risk`
   - `Validation Needed`
   - `Apply?`
4. `Important Risks` - call out any likely row-count, null-handling, security, effective-date, or outer-join behavior change.
5. `Approval Gate` - ask which suggestion IDs to apply before writing V2.

Use rank labels from [Review rubric](references/review-rubric.md). Mark behavior risk as `None`, `Low`, `Medium`, or `High`.

## V2 Rewrite Rules

When the user approves changes:

1. Create or update a separate file using the original name plus `_v2.sql`; if the SQL was pasted, return a fenced `sql` block titled `V2 Query`.
2. Apply only approved change IDs unless a new blocker is found.
3. Add comments only where they explain non-obvious behavior-preserving choices.
4. Keep bind variable names stable unless the approved change requires a new bind. Document any new bind and default expectation.
5. Preserve result columns and aliases unless the user approved alias changes.
6. Provide a `V2 Change Log` mapping each applied ID to the exact query change.
7. Provide `Validation SQL/Checks`, such as row count comparison, duplicate checks, null-sensitive anti-join checks, and sample bind testing.

## Hard Safety Rules

- Do not invent Oracle Fusion table relationships. Verify relationships in official docs, DDL, or user-provided metadata.
- Do not recommend adding or dropping indexes, accepting SQL profiles, gathering optimizer statistics, or creating plan baselines in Fusion SaaS as the primary fix unless the user controls the database or can route the action to a DBA/Oracle SR. Usually suggest query/index-aligned rewrites instead.
- Do not blindly apply SQL Tuning Advisor output. Treat advisor findings as strong evidence, but still verify behavior, Fusion SaaS supportability, security views, bind values, and report grain.
- Do not replace secured views with base tables without warning that row-level security or delivered semantics can change.
- Do not remove `ORG_ID`, `BUSINESS_GROUP_ID`, `PRC_BU_ID`, `REQ_BU_ID`, `ORGANIZATION_ID`, `INVENTORY_ORGANIZATION_ID`, ledger, effective-date, status, language, or security filters unless the user approves the exact behavior change.
- Do not blindly convert legacy `(+)` outer joins to ANSI joins; preserve null-preserving sides and test row counts.
- Do not treat every full table scan as bad. Large selective tables, missing predicates, and bad cardinality need investigation; small lookup table full scans may be acceptable.
- Avoid unsupported certainty. When no explain plan, row counts, or bind values are available, state the confidence and ask for evidence.
