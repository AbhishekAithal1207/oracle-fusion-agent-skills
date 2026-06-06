# Fusion SQL Performance Patterns

Use this as a checklist for Oracle Fusion SQL, especially BI Publisher data models.

## BI Publisher Practices

Oracle BI Publisher performance guidance emphasizes:

- Return only required columns; never use `SELECT *` for reports.
- Use `WHERE` clauses and bind parameters to restrict data early.
- Use shorter column aliases to reduce XML size when practical.
- Push group filters into SQL instead of filtering in the BI Publisher middle tier.
- Avoid PL/SQL calls in `WHERE` clauses and row-level elements because they execute repeatedly and add context switching.
- Avoid unnecessary `DUAL` subqueries for constants such as `SYSDATE`.
- Avoid broad data models with multiple unused data sets; every data set can execute even if the layout does not use it.
- Avoid nested data sets when a single query or `WITH` clause can preserve the same parent-child behavior.
- Enable scalable mode and SQL pruning when appropriate for large report data models.
- Use BI Publisher explain plan, SQL monitoring, and SQL trace/TKPROF diagnostics for Oracle Database-backed SQL.
- If the user has a SQL Tuning Advisor text report, use its findings, estimated benefit, and explain-plan sections as evidence, then cross-check against Fusion SaaS supportability and business semantics.

## Oracle SQL Rewrite Heuristics

Prefer behavior-preserving rewrites:

- Keep predicates sargable. Avoid functions on indexed columns in `WHERE` and `JOIN` unless a matching function-based index exists.
- Rewrite date filters to half-open ranges when time portions matter:

```sql
column_date >= :p_from_date
AND column_date <  :p_to_date + 1
```

- For single as-of dates, apply functions to bind values rather than indexed columns when safe:

```sql
TRUNC(:p_as_of_date) BETWEEN effective_start_date AND effective_end_date
```

- Align predicates with active composite index leading columns. If an index is `(ORG_ID, APPROVAL_STATUS, CREATION_DATE)`, a predicate only on `CREATION_DATE` may not use it efficiently.
- Use function-based index expressions exactly when docs show them, such as `UPPER("PERSON_NUMBER")`.
- Use `EXISTS` instead of `IN` when it avoids duplicate inflation or improves correlated filtering; do not rewrite blindly.
- Replace nullable `NOT IN` with `NOT EXISTS` or an anti-join only after confirming null semantics.
- Remove joins that do not filter, project, or validate required existence.
- Pre-aggregate many-side tables before joining to a one-row grain.
- Be cautious with hints. Suggest hints only when the plan evidence shows the optimizer consistently chooses the wrong path and no clearer SQL rewrite exists.

## Oracle Fusion ERP/Financials Patterns

- `AP_INVOICES_ALL` primary grain is invoice header. Join lines/distributions carefully to avoid multiplying header amounts.
- Use `INVOICE_ID` for invoice header joins when available.
- For supplier invoice lookups, consider unique or active indexes involving `VENDOR_ID`, `INVOICE_NUM`, `ORG_ID`, and `PARTY_ID` when those columns are part of the business lookup.
- Keep `ORG_ID`, ledger, legal entity, date, source, status, and supplier filters where they define security or report scope.
- Do not rely on obsolete indexes shown in docs.

## Oracle Fusion HCM Patterns

- Most core HCM tables are date-effective. Current-row filters are usually required unless the user wants history or future rows.
- Join date-effective tables on both key and overlapping effective date range, or use a common `:p_as_of_date`.
- Preserve `BUSINESS_GROUP_ID` filters when they define enterprise partitioning.
- Watch assignment grain. `PER_ALL_ASSIGNMENTS_M` can contain multiple assignment rows per person; confirm primary assignment, assignment type, status, and work terms requirements.
- Use translation views (`_VL`) or translation tables (`_TL`) only when language-specific labels are needed.
- Do not remove security-aware views or predicates without explicit approval.

## Evidence and Confidence

Use high confidence only when at least one of these is available:

- Official table docs showing matching keys/indexes.
- User-provided DDL/index metadata.
- Explain plan or SQL Monitor evidence.
- SQL Tuning Advisor report evidence for the same SQL and representative binds.
- Row counts and representative bind values.

Use `R5 Investigate` when the suggestion depends on unknown data volume, selectivity, bind values, or functional requirements.
