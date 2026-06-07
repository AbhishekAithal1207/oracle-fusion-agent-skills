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

## Oracle Fusion Procurement Patterns

- Confirm the expected purchasing grain before rewriting: purchase order header, line, schedule/location, distribution, requisition header, requisition line, requisition distribution, supplier, or receiving transaction.
- Join PO and requisition header-to-line-to-distribution chains using documented primary and foreign keys; avoid joining only by document number or line number when surrogate IDs are available.
- Keep procurement scope filters such as `PRC_BU_ID`, `REQ_BU_ID`, `ORG_ID`, supplier, requester, buyer/procurement agent, document status, approval status, creation date, and last update date when they define report scope.
- Treat receiving tables as transaction-grain unless the report explicitly wants shipment or receipt header grain; pre-aggregate receipts before joining to PO or requisition header output.
- Watch one-to-many joins from suppliers, sites, categories, distributions, projects, and receipts that can multiply PO or requisition amounts.
- For status and lookup meaning columns, verify whether the query should use base status codes, lookup tables, or delivered views that already apply language/security semantics.
- Do not replace delivered secured views with base procurement tables without warning about row-level security and delivered semantics.

## Oracle Fusion SCM Patterns

- Confirm the expected SCM grain before rewriting: item, item organization, on-hand quantity row, material transaction, sales order header, sales order line, fulfillment line, shipment/delivery detail, costing row, or receiving transaction.
- For item master queries, treat `INVENTORY_ITEM_ID` plus `ORGANIZATION_ID` or `INVENTORY_ORGANIZATION_ID` as the key pattern unless the official docs for the specific object say otherwise.
- Preserve inventory organization, item, business unit, status, transaction date, source type, subinventory, locator, lot, serial, and language filters when they define report scope.
- Translation tables and views such as `_TL` or `_VL` can multiply item rows by language; keep language predicates or use delivered language-aware views when appropriate.
- Pre-aggregate transaction, on-hand, costing, fulfillment, or shipment details before joining to item or order header output when the report grain is higher than the detail table grain.
- Be careful when joining `RCV_` objects from Procurement and SCM flows; confirm whether the report wants receiving transaction, shipment header/line, PO distribution, or accounting/costing grain.
- Do not assume item, order, shipping, or costing table relationships from naming alone. Verify keys, indexes, and comments in the official `oedsc` docs or live metadata.

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
