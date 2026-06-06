# SQL Tuning Advisor Reports

Use this file when the user provides an Oracle SQL Tuning Advisor text report, SQL Monitor report, BI Publisher diagnostic report, or a `.txt` file generated from `DBMS_SQLTUNE.REPORT_TUNING_TASK` / `DBMS_SQLTUNE.REPORT_AUTO_TUNING_TASK`.

## Ask for the Optional Report

When starting a review, ask for the SQL Tuning Advisor report as optional evidence:

`If you have the Oracle SQL Tuning Advisor .txt report for this SQL, please attach it. It can include findings, estimated benefit, explain-plan sections, SQL IDs, and recommended actions that make the review more accurate.`

Tell the user it is acceptable to redact host names, usernames, schema names, literals, or business-sensitive values, but ask them to keep:

- SQL ID or statement identifier.
- General information section.
- Summary section.
- Tuning findings and recommendations.
- Explain plans.
- Errors section.
- Bind values or representative bind description when available.

## Official Report Shape

Oracle documents `DBMS_SQLTUNE.REPORT_TUNING_TASK` as returning a CLOB, text by default. The report can include individual sections such as:

- `SUMMARY` - summary information.
- `FINDINGS` - tuning findings.
- `PLAN` - explain plans.
- `INFORMATION` - general information.
- `ERROR` - statements with errors.
- `ALL` - all sections.

Automatic SQL Tuning reports may include:

- General information: task metadata and execution details.
- Summary: SQL identifiers and estimated benefit or tested execution statistics.
- Tuning findings: findings, profile status, implementation notes, and execution statistics.
- Explain plans: old and new plans.
- Errors: tuning task errors.

SQL Tuning Advisor recommendations can include:

- Optimizer statistics collection.
- Index/access structure creation.
- SQL statement restructuring.
- SQL profile creation.
- SQL plan baseline creation.

## How to Use the Report in This Skill

1. Confirm the report matches the SQL being reviewed:
   - Compare SQL ID, SQL text excerpts, schema, module, and bind values.
   - If the report is for a different literalized version, ask whether forced matching or bind variation matters.
2. Extract task context:
   - Task name, owner, execution name, completion status, scope, time limit, start/end time.
   - Whether scope was `LIMITED` or `COMPREHENSIVE`. Comprehensive includes SQL profiling; limited does not.
3. Extract findings:
   - Finding type: `Statistics`, `Index`, `Restructure SQL`, `SQL Profile`, `Alternative Plan`, `Information`, `Error`, or `No findings`.
   - Estimated benefit percentage.
   - Rationale and exact recommendation/action text.
   - Objects named in the finding.
4. Extract plan evidence:
   - Plan hash values.
   - Full table scans on large Fusion transaction tables.
   - Index range/full/unique scans and index names.
   - Join method changes.
   - Cardinality estimate mismatches if shown.
   - Original vs recommended plan cost/elapsed/buffer gets when available.
5. Cross-check each advisor recommendation with Fusion table docs, user DDL/indexes, BI Publisher constraints, and business semantics.
6. Promote evidence-backed items in the ranked change table:
   - Advisor recommendation with high estimated benefit and clear SQL rewrite path: usually `R1` or `R2`.
   - Advisor recommendation that requires DBA action in SaaS, such as profile/index/stats: usually `R5 Investigate` unless user has an implementation path.
   - Advisor error or stale/missing report: `R5 Investigate`.

## Fusion SaaS Interpretation Rules

- In Oracle Fusion SaaS, users normally tune report SQL, predicates, joins, and parameters; they often cannot create indexes, gather stats, accept SQL profiles, or create plan baselines directly.
- If SQL Tuning Advisor recommends a SQL profile, explain that it is a database-side remedy for optimizer estimates, not a SQL text rewrite. Suggest DBA/Oracle support action separately from V2 SQL changes.
- If it recommends an index, map the recommendation to existing active Oracle Fusion indexes first. If a similar delivered index exists, rewrite predicates to use it. If no delivered index exists, mark as DBA/Oracle SR action rather than editing the SQL to pretend the index exists.
- If it recommends statistics, ask whether stats can be refreshed by DBA/Oracle support. Also look for SQL rewrites that reduce dependence on bad estimates, such as more selective predicates or pre-aggregation.
- If it recommends restructuring SQL, treat that as a strong candidate for V2 but still preserve row counts, outer joins, null semantics, HCM effective dating, and security views.
- If it recommends an alternative plan or baseline, do not add hints unless the user approves and the plan evidence supports it. Prefer clear SQL rewrites first.

## Additions to the Review Table

When advisor evidence is available, include these extra details in the `Evidence` or `Validation Needed` cells:

- `STA finding: <type>`
- `Estimated benefit: <n>%`
- `Plan hash: <old> -> <new>`
- `Objects: <table/index names>`
- `Advisor action requires DBA/Oracle support: Yes/No`

Example:

| ID | Rank | Area | Evidence | Suggestion | Expected Improvement | Behavior Change Risk | Validation Needed | Apply? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C02 | R2 High | Date predicate / access path | STA Restructure SQL finding, estimated benefit 71%; current plan shows full scan of `AP_INVOICES_ALL`; docs show active index on `INVOICE_DATE, ORG_ID`. | Replace `TRUNC(ai.invoice_date)` with half-open bind range and keep `ORG_ID` predicate. | Better index range scan potential and lower buffer gets. | Medium | Compare date-boundary row counts and BI Publisher output for same binds. | Awaiting approval |

## Report Generation SQL to Request From User

If the user asks how to generate the text report and has privileges, suggest one of these patterns:

```sql
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(:task_name, 'TEXT', 'TYPICAL', 'ALL')
FROM dual;
```

For a specific findings section:

```sql
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(:task_name, 'TEXT', 'TYPICAL', 'FINDINGS')
FROM dual;
```

For automatic SQL tuning task reports:

```sql
VARIABLE my_rept CLOB;
BEGIN
  :my_rept := DBMS_SQLTUNE.REPORT_AUTO_TUNING_TASK(
    begin_exec   => NULL,
    end_exec     => NULL,
    type         => 'TEXT',
    level        => 'TYPICAL',
    section      => 'ALL',
    object_id    => NULL,
    result_limit => NULL
  );
END;
/
PRINT :my_rept
```

Do not ask the user to run these if they do not have database advisor privileges. In Fusion SaaS, they may only have a generated `.txt` report from diagnostics or Oracle support.
