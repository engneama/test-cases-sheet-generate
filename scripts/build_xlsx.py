#!/usr/bin/env python3
"""Build <Feature>_Test_Cases.xlsx and <Feature>_Coverage_and_Gaps.xlsx from one JSON file.
Usage: python3 build_xlsx.py data.json [out_dir]   (JSON schema: SKILL.md section 13)
Prints the counts for the chat reply and warnings to fix; exits 1 when warnings exist."""
import json, math, re, sys
from collections import Counter
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    sys.exit("openpyxl is missing: run  pip install openpyxl")

DEP = "Depend on BRD or User Story"
EXTRA = {"SEC": "Security (not in BRD)", "USA": "Usability (not in BRD)"}
TC = (["Activity Type", "Title", "Details", "Expected Results", "Actual Results", "Status", "Priority",
       "Project", "Parent Project Activity", "Format Text Editor Fields"], [14, 42, 95, 55, 26, 10, 10, 18, 24, 14])
COV = (["Req ID", "Requirement", "Test Case Titles", "No. of Test Cases", "Coverage"], [12, 60, 70, 12, 18])
EPB = (["Field / Rule", "Req ID", "Rule from BRD", "Valid Partitions", "Not Valid Partitions",
        "Boundary Values Tested", "Test Case Titles"], [22, 16, 40, 34, 44, 34, 60])
GAP = (["#", "Gap Type", "Related Req ID", "Description", "Question to Business", "User Decision"], [5, 24, 20, 70, 50, 36])

HFONT, BFONT = Font(name="Arial", bold=True, color="FFFFFF"), Font(name="Arial", size=10)
HFILL = PatternFill("solid", fgColor="1F3864")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

ARABIC = re.compile(r"[؀-ۿ]")
QUOTED = re.compile(r'"[^"]*"|“[^”]*”')
PLACEHOLDER = re.compile(r"<([^<>\n]{1,40})>")
HTML_TAG = re.compile(r"^/?(script|img|svg|iframe|a|b|i|u|p|h[1-6]|body|div|span|input|style|link|object|embed)\b", re.I)
VAGUE = re.compile(r"\b(works? (correctly|properly|fine)|as expected|properly)\b", re.I)


def add_sheet(wb, title, spec, rows):
    headers, widths = spec
    ws = wb.create_sheet(title)
    ws.append(headers)
    for row in rows:
        ws.append(row)
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for r, row in enumerate(ws.iter_rows(), 1):
        lines = 1
        for c in row:
            head = r == 1
            c.font, c.border = (HFONT if head else BFONT), BORDER
            c.alignment = Alignment(wrap_text=True, vertical="center" if head else "top",
                                    horizontal="center" if head else None)
            if head:
                c.fill = HFILL
            elif isinstance(c.value, str):
                w = widths[c.column - 1] * 1.15
                lines = max(lines, sum(max(1, math.ceil(len(l) / w)) for l in c.value.split("\n")))
        ws.row_dimensions[r].height = 30 if r == 1 else max(15, 13 * lines + 4)
    ws.freeze_panes = "A2"


def text_checks(tag, value, warn):
    if ARABIC.search(QUOTED.sub("", value)):
        warn.append(f"{tag}: Arabic outside quotes (English sentences only, no bracket translations)")
    for p in PLACEHOLDER.findall(value):
        if not HTML_TAG.match(p):
            warn.append(f"{tag}: placeholder <{p}> left")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    data = json.loads(src.read_text(encoding="utf-8"))
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.parent
    out.mkdir(parents=True, exist_ok=True)
    feature = re.sub(r"[^\w\-]+", "_", data["feature"]).strip("_")
    cases, warn = data["cases"], []

    for key in ("project", "parent"):
        if not str(data.get(key) or "").strip():
            warn.append(f"'{key}' ID is empty")
    warn += [f"duplicate title: {t}" for t, n in Counter(c["title"] for c in cases).items() if n > 1]

    for i, c in enumerate(cases, 1):
        c["kind"] = str(c.get("kind") or "FUNC").upper()
        c["reqs"] = c.get("reqs") or ([c["kind"]] if c["kind"] in EXTRA else [])
        tag = f"case {i} '{c.get('title', '')[:60]}'"
        if c.get("priority") not in ("High", "Medium", "Low"):
            warn.append(f"{tag}: priority must be High/Medium/Low")
        if not c["reqs"]:
            warn.append(f"{tag}: no reqs")
        for f in ("title", "details", "expected"):
            if not str(c.get(f) or "").strip():
                warn.append(f"{tag}: empty {f}")
            text_checks(f"{tag} {f}", str(c.get(f) or ""), warn)
        steps = [l for l in str(c.get("details") or "").split("\n") if l.strip()]
        if any(not l.startswith("- ") for l in steps):
            warn.append(f"{tag}: every Details line must start with '- '")
        first = next((l for l in steps if not l.startswith("- Precondition")), "")
        if "http" not in first:
            warn.append(f"{tag}: first step doesn't open a full URL")
        if VAGUE.search(str(c.get("expected") or "")):
            warn.append(f"{tag}: vague Expected Results")

    tc_rows = [["Test Case", c["title"], c["details"], c["expected"], c.get("actual") or DEP, c.get("status"),
                c["priority"], data.get("project"), data.get("parent"), 1] for c in cases]

    by_req = {}
    for c in cases:
        for r in c["reqs"]:
            by_req.setdefault(r, []).append(c)
    coverage = list(data.get("coverage", []))
    listed = {x["req"] for x in coverage}
    coverage += [{"req": k, "requirement": v} for k, v in EXTRA.items() if k in by_req and k not in listed]
    warn += [f"req {r} is used by cases but missing from coverage" for r in by_req if r not in listed and r not in EXTRA]

    cov_rows, status = [], Counter()
    for x in coverage:
        cs = by_req.get(x["req"], [])
        st = x.get("coverage") or ("Not Covered" if not cs else
                                   "Partially Covered" if any(DEP in c["expected"] for c in cs) else "Covered")
        status[st] += 1
        cov_rows.append([x["req"], x["requirement"], "\n".join(c["title"] for c in cs), len(cs), st])

    ep_rows = []
    for x in data.get("ep_bva", []):
        titles = x.get("titles") or [c["title"] for c in cases if c.get("field") == x["field"]]
        if not titles:
            warn.append(f"EP & BVA '{x['field']}': no cases linked (set case.field)")
        ep_rows.append([x["field"], x.get("req", ""), x.get("rule", ""), x.get("valid", ""),
                        x.get("not_valid", ""), x.get("boundaries", ""), "\n".join(titles)])

    gaps = data.get("gaps", [])
    gap_rows = [[i, g["type"], g.get("req", ""), g["description"], g.get("question", ""), g.get("decision", "")]
                for i, g in enumerate(gaps, 1)]
    for name, rows, cols in (("Coverage", cov_rows, (1,)), ("EP & BVA", ep_rows, (0, 2, 3, 4, 5)),
                             ("Gaps", gap_rows, (1, 3, 4))):
        for row in rows:
            for i in cols:
                text_checks(f"{name} row '{str(row[0])[:20]}'", str(row[i] or ""), warn)

    f1, f2 = out / f"{feature}_Test_Cases.xlsx", out / f"{feature}_Coverage_and_Gaps.xlsx"
    wb = Workbook(); wb.remove(wb.active)
    add_sheet(wb, "Table 1", TC, tc_rows); wb.save(f1)
    wb = Workbook(); wb.remove(wb.active)
    add_sheet(wb, "Requirement Coverage", COV, cov_rows)
    add_sheet(wb, "EP & BVA", EPB, ep_rows)
    add_sheet(wb, "Gaps", GAP, gap_rows); wb.save(f2)

    kinds = Counter(c["kind"] for c in cases)
    open_gaps = sum(1 for g in gaps if g.get("decision") not in ("Added", "Not needed (user)"))
    print(f"Saved: {f1}\nSaved: {f2}")
    print(f"Requirements: {sum(1 for x in coverage if x['req'] not in EXTRA)} | Test cases: {len(cases)} ("
          + ", ".join(f"{k} {n}" for k, n in sorted(kinds.items()))
          + f", from confirmed gaps {sum(1 for c in cases if c.get('gap'))})")
    print("Coverage: " + ", ".join(f"{k} {status[k]}" for k in ("Covered", "Partially Covered", "Not Covered")))
    print(f"Gaps: {len(gaps)} ({open_gaps} still need a business answer)")
    if warn:
        print("\nWARNINGS - fix and re-run before delivering:\n- " + "\n- ".join(warn))
        sys.exit(1)


if __name__ == "__main__":
    main()
