# Oracle Fusion Source Discovery

Use official Oracle documentation first, then user-provided DDL/indexes, then other sources only for examples or troubleshooting. Always cite or name the source consulted in the review.

## Official Sources

- Financials tables and views: `https://docs.oracle.com/en/cloud/saas/financials/<release>/oedmf/`
- Current Financials table search pattern: `site:docs.oracle.com/en/cloud/saas/financials/oedmf <TABLE_NAME>`
- Versioned Financials example: `https://docs.oracle.com/en/cloud/saas/financials/25d/oedmf/apinvoicesall-26582.html`
- HCM tables and views: `https://docs.oracle.com/en/cloud/saas/human-resources/<release>/oedmh/`
- Current HCM table search pattern: `site:docs.oracle.com/en/cloud/saas/human-resources/oedmh <TABLE_NAME>`
- HCM examples: `PER_ALL_PEOPLE_F`, `PER_ALL_ASSIGNMENTS_M`, `PER_USERS`, `HR_ALL_ORGANIZATION_UNITS_F`.
- BI Publisher performance best practices: `https://docs.oracle.com/middleware/1221/bip/BIPDM/best_practices.htm`
- SQL Tuning Advisor and DBMS_SQLTUNE report interpretation: Oracle Database SQL Tuning Guide and PL/SQL Packages and Types Reference for `DBMS_SQLTUNE.REPORT_TUNING_TASK`.

Use the latest relevant release unless the user specifies a release such as `25D`. State the release used because Oracle SaaS table metadata can shift between quarterly updates.

## What to Extract From Table Docs

For every base table or delivered view that drives cardinality, collect:

- Schema, owner, and object type.
- Primary key columns.
- Foreign keys and relationship table/column pairs.
- Column data types and not-null flags for join/filter columns.
- Index list, including uniqueness, column order, and active/obsolete status when shown.
- HCM effective-date columns and tenant columns.
- Comments that define business meaning, especially status flags and denormalized columns.

## Table Name Lookup Tips

1. Normalize object names to lowercase and remove underscores for Oracle doc slugs, then search with the original uppercase name.
2. If a page has a numeric suffix, do not guess the suffix; search the docs domain.
3. For synonyms or views, search both the view and likely base tables.
4. For HCM `_F`, `_M`, `_VL`, `_B`, and `_TL` objects, inspect whether the query needs effective dating, language rows, or current-row filtering.
5. For Financials `ALL` tables, inspect `ORG_ID`, ledger, legal entity, supplier, status, invoice date, and primary key joins.

## When Docs Are Not Enough

Ask the user for:

- `DBMS_METADATA.GET_DDL` output when available.
- Index metadata from `ALL_INDEXES` and `ALL_IND_COLUMNS`.
- Column metadata from `ALL_TAB_COLUMNS`.
- `EXPLAIN PLAN`, SQL Monitor, or BI Publisher diagnostic log.
- Oracle SQL Tuning Advisor `.txt` report generated for the same SQL and bind values, when available.
- Sample bind values and row counts.

Suggested metadata SQL, if the user has access:

```sql
SELECT table_name, column_name, data_type, data_length, data_precision, nullable
FROM all_tab_columns
WHERE owner = :owner
  AND table_name IN (:table_names)
ORDER BY table_name, column_id;

SELECT i.table_name, i.index_name, i.uniqueness, i.status,
       c.column_position, c.column_name, c.descend
FROM all_indexes i
JOIN all_ind_columns c
  ON c.index_owner = i.owner
 AND c.index_name = i.index_name
WHERE i.table_owner = :owner
  AND i.table_name IN (:table_names)
ORDER BY i.table_name, i.index_name, c.column_position;
```

## Source Trust Rules

- Treat official Oracle docs, user DDL, and live metadata as authoritative.
- Treat blogs, forums, and generated examples as non-authoritative hints.
- If official docs and live DDL conflict, prefer live DDL for that environment and mention the conflict.
- Do not infer custom indexes or custom synonyms in a SaaS tenant without evidence.
