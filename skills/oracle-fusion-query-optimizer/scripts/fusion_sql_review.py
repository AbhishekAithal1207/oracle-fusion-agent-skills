#!/usr/bin/env python3
"""Create a starter review skeleton for Oracle Fusion SQL."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SQL_KEYWORDS = {
    "select",
    "from",
    "where",
    "join",
    "left",
    "right",
    "full",
    "inner",
    "outer",
    "cross",
    "on",
    "and",
    "or",
    "group",
    "order",
    "having",
    "union",
    "connect",
    "start",
    "with",
}


def strip_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    return re.sub(r"--.*?$", " ", sql, flags=re.M)


def find_cte_names(sql: str) -> set[str]:
    cleaned = strip_comments(sql)
    if not re.match(r"^\s*with\b", cleaned, flags=re.I):
        return set()
    names = set()
    for match in re.finditer(r"(?:with|,)\s+([a-zA-Z][\w$#]*)\s+as\s*\(", cleaned, flags=re.I):
        names.add(match.group(1).upper())
    return names


def extract_tables(sql: str) -> list[str]:
    cleaned = strip_comments(sql)
    ctes = find_cte_names(cleaned)
    tables: list[str] = []
    seen: set[str] = set()

    patterns = [
        r"\bfrom\s+([a-zA-Z][\w$#.]*)",
        r"\bjoin\s+([a-zA-Z][\w$#.]*)",
        r",\s*([a-zA-Z][\w$#.]*)\s+(?:[a-zA-Z][\w$#]*)(?=\s*(?:,|where|join|left|right|full|inner|outer|cross|on|$))",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, cleaned, flags=re.I):
            table = match.group(1).strip().upper()
            bare = table.split(".")[-1]
            if bare.lower() in SQL_KEYWORDS or bare in ctes:
                continue
            if table not in seen:
                seen.add(table)
                tables.append(table)
    return tables


def detect_flags(sql: str) -> list[tuple[str, str, str]]:
    cleaned = strip_comments(sql)
    flags: list[tuple[str, str, str]] = []

    checks = [
        (r"select\s+\*", "R3 Medium", "SELECT * can increase BI Publisher XML size and memory."),
        (r"\(\+\)", "R5 Investigate", "Legacy outer join detected; preserve null-producing side if converting."),
        (r"\bfrom\b[^;]*,\s*[a-zA-Z][\w$#.]*", "R5 Investigate", "Comma joins detected; check for missing join predicates before rewriting."),
        (r"\bnot\s+in\s*\(", "R2 High", "NOT IN can be null-sensitive; verify nullable subquery columns."),
        (r"\bfrom\s+dual\b", "R4 Low", "DUAL may be unnecessary for constants such as SYSDATE."),
        (r"\b(trunc|to_char|to_date|nvl|coalesce|upper|lower)\s*\(\s*[a-zA-Z][\w$#.]*\.", "R2 High", "Function appears to be applied to a column; check index/sargability impact."),
        (r"\bhaving\b", "R5 Investigate", "HAVING can be expensive; verify whether predicate can move before aggregation."),
        (r"\bin\s*\(\s*select\b", "R5 Investigate", "Subquery IN detected; compare with EXISTS or join only if behavior is equivalent."),
        (r"\bselect\b[\s\S]*\b(attribute[0-9]|global_attribute[0-9])\b", "R3 Medium", "Flexfield columns detected; confirm only required segments are selected."),
    ]
    for pattern, rank, message in checks:
        if re.search(pattern, cleaned, flags=re.I):
            flags.append((rank, message, pattern))
    return flags


def parse_advisor_report(report: str) -> dict[str, object]:
    cleaned = report.replace("\r\n", "\n")
    upper = cleaned.upper()
    section_names = [
        "GENERAL INFORMATION SECTION",
        "SUMMARY SECTION",
        "TUNING FINDINGS SECTION",
        "EXPLAIN PLANS SECTION",
        "ERRORS SECTION",
        "INFORMATION SECTION",
    ]
    sections = [
        name
        for name in section_names
        if re.search(rf"(^|\n)\s*{re.escape(name)}\s*(\n|$)", upper)
    ]
    sql_ids = sorted(set(re.findall(r"\bSQL\s*ID\s*[:=]?\s*([a-z0-9]{10,14})\b", cleaned, flags=re.I)))
    plan_hashes = sorted(set(re.findall(r"plan hash value\s*[:=]\s*(\d+)", cleaned, flags=re.I)))
    benefits = re.findall(r"(?:estimated\s+benefit|benefit)\D{0,40}(\d+(?:\.\d+)?)\s*%", cleaned, flags=re.I)

    finding_types: list[str] = []
    type_patterns = [
        ("SQL Profile", r"\bSQL\s+Profile\s+Finding\b|\bSQL\s+profile\s+recommendation\b"),
        ("Index", r"\bIndex\s+Finding\b|\bindex\s+recommendation\b"),
        ("Statistics", r"\bStatistics\s+Finding\b|\bstats?\s+recommendation\b"),
        ("Restructure SQL", r"\bRestructure\s+SQL\s+Finding\b|\brestructur(?:e|ing)\s+SQL\b"),
        ("Alternative Plan", r"\bAlternative\s+Plan\s+Finding\b|\balternative\s+plan\b"),
        ("SQL Plan Baseline", r"\bSQL\s+Plan\s+Baseline\s+Finding\b|\bplan\s+baseline\b"),
        ("Information", r"\bInformation\s+Finding\b"),
        ("Error", r"\bError\s+Finding\b|\bERRORS SECTION\b|\bORA-\d{5}\b"),
        ("No findings", r"\bNo\s+findings\b"),
    ]
    for finding_type, pattern in type_patterns:
        if re.search(pattern, cleaned, flags=re.I):
            finding_types.append(finding_type)

    full_scans = sorted(set(re.findall(r"TABLE ACCESS\s+FULL\s+([A-Z0-9_$#]+)", upper)))
    index_scans = sorted(
        set(
            re.findall(
                r"INDEX\s+(?:RANGE SCAN|UNIQUE SCAN|FULL SCAN|FAST FULL SCAN|SKIP SCAN)\s+([A-Z0-9_$#]+)",
                upper,
            )
        )
    )
    errors = bool(re.search(r"\b(ERRORS SECTION|ORA-\d{5}|ERROR:)", upper))

    return {
        "sections": sections,
        "sql_ids": sql_ids,
        "plan_hashes": plan_hashes,
        "benefits": benefits,
        "finding_types": finding_types,
        "full_scans": full_scans,
        "index_scans": index_scans,
        "errors": errors,
    }


def markdown_report(sql: str, source: str, advisor_report: str | None = None, advisor_source: str | None = None) -> str:
    tables = extract_tables(sql)
    flags = detect_flags(sql)
    advisor = parse_advisor_report(advisor_report) if advisor_report else None
    lines: list[str] = []

    lines.append("# Oracle Fusion SQL Review Starter")
    lines.append("")
    lines.append(f"Source: `{source}`")
    lines.append("")
    lines.append("## Extracted Tables")
    if tables:
        for table in tables:
            lines.append(f"- `{table}`")
    else:
        lines.append("- No table names detected. Check SQL parsing manually.")
    lines.append("")
    lines.append("## Initial Flags")
    if flags:
        lines.append("| Rank | Flag | Evidence Pattern |")
        lines.append("| --- | --- | --- |")
        for rank, message, pattern in flags:
            lines.append(f"| {rank} | {message} | `{pattern}` |")
    else:
        lines.append("- No simple static flags found. Continue with DDL, index, and explain-plan review.")
    lines.append("")
    lines.append("## SQL Tuning Advisor Evidence")
    if advisor:
        lines.append(f"Advisor source: `{advisor_source or 'provided report'}`")
        for label, key in [
            ("Sections detected", "sections"),
            ("SQL IDs", "sql_ids"),
            ("Plan hash values", "plan_hashes"),
            ("Estimated benefits", "benefits"),
            ("Finding types", "finding_types"),
            ("Full table scans", "full_scans"),
            ("Index scans", "index_scans"),
        ]:
            values = advisor.get(key, [])
            if values:
                formatted = ", ".join(f"`{value}`" for value in values)
                suffix = "%" if key == "benefits" else ""
                if key == "benefits":
                    formatted = ", ".join(f"`{value}%`" for value in values)
                lines.append(f"- {label}: {formatted}{suffix if False else ''}")
        if advisor.get("errors"):
            lines.append("- Errors or error section detected; inspect the report before ranking changes.")
    else:
        lines.append("- No SQL Tuning Advisor report supplied. Ask for the optional `.txt` report if available.")
    lines.append("")
    lines.append("## Metadata To Gather")
    for table in tables:
        bare = table.split(".")[-1]
        lines.append(f"- Official Oracle docs, PK/FK, columns, and indexes for `{bare}`.")
    if not advisor:
        lines.append("- Optional Oracle SQL Tuning Advisor `.txt` report for the same SQL and bind values.")
    lines.append("- Explain plan or BI Publisher diagnostic log.")
    lines.append("- Sample bind values and expected result grain.")
    lines.append("")
    lines.append("## Ranked Change Suggestions")
    lines.append("| ID | Rank | Area | Evidence | Suggestion | Expected Improvement | Behavior Change Risk | Validation Needed | Apply? |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    if flags:
        for idx, (rank, message, _) in enumerate(flags, start=1):
            lines.append(
                f"| C{idx:02d} | {rank} | Static SQL check | {message} | Confirm with docs/DDL and rewrite if behavior-preserving. | TBD | TBD | Compare original vs V2. | Awaiting approval |"
            )
        next_id = len(flags) + 1
    else:
        next_id = 1
    if advisor:
        finding_types = advisor.get("finding_types", [])
        benefits = advisor.get("benefits", [])
        evidence_parts = []
        if finding_types:
            evidence_parts.append("STA findings: " + ", ".join(str(x) for x in finding_types))
        if benefits:
            evidence_parts.append("Estimated benefit(s): " + ", ".join(f"{x}%" for x in benefits))
        if advisor.get("plan_hashes"):
            evidence_parts.append("Plan hash values: " + ", ".join(str(x) for x in advisor["plan_hashes"]))
        evidence = "; ".join(evidence_parts) if evidence_parts else "SQL Tuning Advisor report supplied."
        lines.append(
            f"| C{next_id:02d} | R5 Investigate | SQL Tuning Advisor | {evidence} | Cross-check advisor recommendations against Fusion docs and identify which are SQL-text changes vs DBA/Oracle support actions. | Higher-confidence ranking. | TBD | Confirm report SQL/binds match and compare original vs V2. | Awaiting approval |"
        )
    elif not flags:
        lines.append("| C01 | R5 Investigate | Evidence | Need DDL/index/plan review. | Gather metadata before rewrite. | TBD | TBD | TBD | Awaiting approval |")
    lines.append("")
    lines.append("Please approve the suggestion IDs to apply before creating a separate V2 query.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a starter Oracle Fusion SQL review skeleton.")
    parser.add_argument("--sql-file", help="Path to a SQL file. Reads stdin when omitted.")
    parser.add_argument("--advisor-file", help="Optional Oracle SQL Tuning Advisor text report for the same SQL.")
    args = parser.parse_args()

    if args.sql_file:
        path = Path(args.sql_file)
        sql = path.read_text(encoding="utf-8")
        source = str(path)
    else:
        sql = sys.stdin.read()
        source = "stdin"

    if not sql.strip():
        print("No SQL supplied.", file=sys.stderr)
        return 2

    advisor_report = None
    advisor_source = None
    if args.advisor_file:
        advisor_path = Path(args.advisor_file)
        advisor_report = advisor_path.read_text(encoding="utf-8")
        advisor_source = str(advisor_path)

    print(markdown_report(sql, source, advisor_report, advisor_source))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
