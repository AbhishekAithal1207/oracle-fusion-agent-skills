# Review Rubric

Use this file to rank improvement suggestions and control the approval flow.

## Improvement Ranks

| Rank | Meaning | Typical examples |
| --- | --- | --- |
| R1 Critical | Likely correctness, security, runaway runtime, or severe row explosion issue. | Missing join predicate, accidental cross join, null-unsafe `NOT IN`, missing HCM effective-date filter, unbounded BI Publisher extract. |
| R2 High | Likely material performance gain with low or manageable behavior risk. | Add selective bind predicate, align predicate with active composite index, remove non-sargable function from indexed column, eliminate duplicate-driving join. |
| R3 Medium | Useful performance, maintainability, or BI Publisher memory improvement. | Select only required columns, shorten XML aliases, combine nested data sets, move middle-tier filter into SQL. |
| R4 Low | Cleanup or readability improvement with limited runtime effect. | Normalize alias style, convert simple comma joins to ANSI joins after preserving semantics, remove redundant `DUAL`. |
| R5 Investigate | Plausible improvement but needs plan, DDL, row counts, bind values, or business confirmation. | Hint suggestion, subquery rewrite, replacing view with base table, changing date truncation logic. |

## Behavior Change Risk

| Risk | Use when |
| --- | --- |
| None | Formatting or comment-only change. |
| Low | Same rows expected, but SQL shape changes. Validate with row count and sample output. |
| Medium | Predicate placement, join form, date handling, or null handling could change edge rows. Requires explicit approval and comparison checks. |
| High | Output grain, security scope, effective dating, outer-join preservation, or mandatory parameters may change. Ask before rewriting. |

## Mandatory Review Checks

- Confirm the result grain: one row per invoice, invoice line, distribution, purchase order, PO line, PO distribution, requisition, requisition line, receipt transaction, item, item organization, inventory transaction, sales order, fulfillment line, shipment, person, assignment, payroll result, or other grain.
- Identify duplicate risk from one-to-many joins and missing aggregation.
- Identify outer joins and preserve null-producing behavior.
- Review filter selectivity and whether filters use active index leading columns.
- Check date predicates for sargability and time-of-day behavior.
- Check HCM date-effective joins on `EFFECTIVE_START_DATE` and `EFFECTIVE_END_DATE`.
- Check HCM tenant and security filters, especially `BUSINESS_GROUP_ID`.
- Check Financials tenant/scope filters such as `ORG_ID`, ledger, legal entity, business unit, supplier, invoice date, and status.
- Check Procurement tenant/scope filters such as `PRC_BU_ID`, `REQ_BU_ID`, `ORG_ID`, supplier, requester, buyer/procurement agent, document status, approval status, creation date, and receiving status.
- Check SCM tenant/scope filters such as `ORGANIZATION_ID`, `INVENTORY_ORGANIZATION_ID`, `INVENTORY_ITEM_ID`, business unit, transaction date, subinventory, locator, lot, serial, fulfillment status, shipment status, and language.
- Check many-side joins from PO/requisition lines, schedules, distributions, receipts, inventory transactions, fulfillment lines, shipping details, costing rows, and translation rows before projecting header-level amounts.
- Check whether any function is applied to a column in `WHERE` or `JOIN`.
- Check `NOT IN` with nullable subquery columns; prefer null-safe anti-join or `NOT EXISTS` when equivalent.
- Check `SELECT *`, unused columns, excessive flexfield columns, and verbose aliases in BI Publisher reports.
- Check nested BI Publisher data sets; prefer one SQL query with joins or `WITH` clauses when it preserves behavior.
- Check PL/SQL package calls in row-level SQL; ask whether the function can be replaced with joins or a once-per-report global value.
- Check bind parameters and multi-value parameter cardinality.
- Check if delivered secure views or language translation views are being used intentionally.

## Required Change Table

Use this exact table shape before rewriting:

| ID | Rank | Area | Evidence | Suggestion | Expected Improvement | Behavior Change Risk | Validation Needed | Apply? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | R2 High | Predicate/index | `TRUNC(invoice_date)` prevents use of `AP_INVOICES_N5` on `INVOICE_DATE, ORG_ID`. | Rewrite to a half-open bind date range and keep `ORG_ID` predicate. | Better index range scan potential. | Medium | Compare row counts for dates with time portions. | Awaiting approval |

## Approval Prompt

End the review with:

`Please approve the suggestion IDs you want in V2, for example: "Apply C01, C03, and C05". I will then create a separate _v2.sql query and leave the original unchanged.`

## V2 Validation Checklist

After creating V2, include:

- Applied IDs.
- Any skipped approved IDs and why.
- New bind variables.
- Row-count comparison query or instructions.
- Duplicate check query for the expected grain.
- Edge-case checks for nulls, outer joins, HCM effective dates, and date boundaries.
- Recommended BI Publisher explain plan or SQL monitoring step when available.
