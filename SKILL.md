---
name: test-cases-sheet-generate
description: "Writes manual test cases (functional, non-functional, security, usability) from a user story, BRD, screenshot, Figma or link into the team's Excel upload template plus a coverage and gaps file. Use for requests like test case sheet، اكتبلي test cases، تيست كيسز، تست كيس، شيت test cases. Not for Playwright or other automation."
---

# Test Cases – Sheet Generate
Act as a senior QA engineer. The sheet is uploaded to another system, so headers, column order and fixed values must match the template exactly.

## Core rules
1. **Scope**: test only what the inputs state. Never invent features, fields, roles, messages, rules, limits or outcomes. Exceptions: the Security & Usability checklists (§4) and gaps the user confirms (§5). Practices from other systems that are policy choices (password complexity, CAPTCHA, duplicate handling…) are gaps to ask, not cases.
2. **No invented values**: every limit (length, digits, range, format, file type/size, attempts, timeout, expiry) comes from the inputs or the user. Not stated → write "not defined in the BRD" in the step, Expected = `Depend on BRD or User Story`, and log a gap. Same for environment and data: the environment URL (dev, UAT, prod…), page paths, email domain, accounts and form fields come only from the inputs or the user. This skill has no fixed system; its `<placeholders>` are never copied into cases.
3. **EP + BVA** on every stated rule/limit (§11).
4. **Gaps**: ask the user yes/no before building files; add only confirmed ones (§5).
5. **One behavior = one case**, no duplicates (§6).
6. Every case is **independent**, **testable**, with **test data inside the steps** (§9, §12).
7. **English always** (Title, Details, Expected, Coverage file), even for Arabic inputs. Only UI element names, exact system texts (messages, emails, page titles) and Arabic test data stay in the input's language: quoted, written once, never translated in brackets (Arabic UI → `Click "النماذج".`). Screenshot/link decides names; otherwise the BRD wording.
8. Output = 2 `.xlsx` files built by `scripts/build_xlsx.py` (§13).

## Workflow
1. Read inputs (§1); ask for missing project info (§2).
2. List requirements with their rules and values (§3).
3. Plan cases: requirement coverage + EP/BVA + Security + Usability; remove duplicates.
4. Ask about gaps (§5) and wait. No gaps → skip.
5. Add confirmed cases, build files (§13), run self-check (§14).

## 1. Inputs (use everything given)
- **Story / BRD / AC** (text, docx, pdf, md, xlsx): source of behavior, rules, messages, limits, roles. Use only the requested feature.
- **Screenshot / mockup / Figma**: list page title, fields (label, placeholder, `*`), buttons, links, tabs, tables/columns, dropdown options, messages, hints (max length, file types), language, and element states shown in the design (hover, disabled, error, empty). Figma link → read it with a Figma tool if available, else ask for exported frames. Visible elements are testable; behavior not stated → `Depend on BRD or User Story` + gap.
- **Link**: open it (web fetch; browser tool for pages behind login). Collect the same elements + real URLs and navigation; use the real URL in the first step. Can't open (login, VPN) → say so and ask for a screenshot/story; never guess.
- **Combined**: story decides behavior and limits; image/link decides elements, labels, URLs. Contradiction → gap.

## 2. Project info
Ask once, in one message, for what's missing (never guess IDs): Project ID (e.g. P.xx.xx.xxxxxx), Parent Project Activity ID (e.g. PA.xx.xxxxxxx), feature name, roles (if relevant), environment URL (dev / UAT / prod, if no link), email domain and test accounts (if cases need them).

## 3. Requirements
- List every requirement with the BRD's IDs (`FR-03`, `AC-2`) or `R1, R2…`, as a short English summary: functional rules, fields, messages, roles, visible elements, and non-functional requirements (performance, browsers/devices, accessibility, localization…).
- Per field, record its rules with the exact input values: min/max length, allowed chars, format, range, digits, file types/size, date range, max items, options/statuses. Missing → "not defined".
- Per requirement, cover what applies: positive; negative (invalid input, wrong credentials, empty mandatory); EP/BVA; each role's access; audit log (if mentioned); UI (element visible, enabled, clickable, `*` marker; matches the design: labels, order, placeholders, states); non-functional (one case per measurable value, e.g. loads within `<n>` seconds; not measurable → ask, §5).

## 4. Security & Usability (always, even if not in the BRD)
Write every item whose trigger exists in the feature; skip only what clearly doesn't apply. No yes/no needed. Expected = the standard secure/usable behavior; if it depends on an undefined value or text → `Depend on BRD or User Story` + business gap. If the BRD defines a conflicting behavior, follow the BRD and log a security/usability gap. Write each once per feature/page (not per requirement) unless roles/pages differ.

**Security** (Priority High)
| Trigger | Cases |
|---|---|
| Login | Lockout after consecutive wrong passwords (BVA N−1/N, dedicated account); password field masked; error doesn't reveal whether the email or the password is wrong |
| Session / protected pages | Session timeout (BVA); logout ends the session (Back button doesn't show the protected page); protected URL opened without login → redirect to login |
| Roles | Role opening a forbidden page/action by direct URL is blocked |
| Text inputs | Script `<script>alert(1)</script>` not executed (rejected or shown as plain text); SQL injection `' OR '1'='1` → no error page, no data exposed |
| File upload | Disguised/executable file (e.g. `file.pdf.exe`) rejected |
| Reset link / OTP / token | Not reusable after success; expired one rejected (expiry from BRD) |
| Forgot password / registration | Response doesn't reveal whether an email is registered |
| Any page | Served over HTTPS; passwords, OTPs, tokens, national IDs never appear in the URL |

**Usability** (Priority Medium; cosmetic Low)
| Trigger | Cases |
|---|---|
| Forms | Tab order follows the visual order (right-to-left on Arabic pages); visible focus indicator; error shown next to its field; valid values kept after a validation error |
| Submit / save | Loading or disabled state while processing; double click → one submission only |
| Links / buttons | Visible, not overlapped, pointer cursor on hover, reachable by keyboard |
| Arabic / English pages | Correct direction (RTL/LTR) and alignment; no untranslated or mixed-language text; language switch (if present) changes all page texts |
| Lists / tables | Empty-state message when no records; long values don't break the layout |
| Any page | Usable at mobile width (no horizontal scroll or overlap); clear page title; feedback after each action (text from BRD, else `Depend on BRD or User Story`) |

Team style example: Title `Verify "<link>" link is visible and clickable` · Details: `- Open the "<page>" page <environment URL><path>` / `- Locate the link "<link>" and check it is visible, readable and not overlapped.` / `- Hover the mouse over the link.` / `- Press Tab until the link is focused.` · Expected: `The link is visible and clear, the cursor changes to a pointer on hover, and a focus indicator is shown.` · Priority High.

## 5. Gaps → ask the user
Gap = something a tester needs that the inputs don't define.
| Type | Example | Handling |
|---|---|---|
| Security/usability value | Lockout attempts, timeout, link expiry, message | Case written; reported, not asked |
| Missing message/outcome | Error/success text, redirect, email, status change | Case written with `Depend on BRD or User Story`; reported |
| Missing scenario | Duplicate email, cancelled action, Back after submit | Ask |
| Missing rule/limit | No length, chars, format, range, file type/size (blocks EP/BVA) | Ask + ask for the value |
| Policy not stated | Password complexity, CAPTCHA, OTP/2FA, rate limit, confirm before delete | Ask |
| Missing role/permission | Action with no owner; role with no stated access | Ask |
| Contradiction | Story vs image/link, or conflicting requirements | Ask |
| Vague / ambiguous | "should be fast", "validate the field" | Ask for a measurable / testable definition |

- Use AskUserQuestion if available: one question per gap, or one multi-select per gap type; ≤4 questions per round, more rounds if needed. Otherwise a numbered list; the user replies like `1 نعم، 2 لأ`.
- Each question = gap + related requirement + case(s) to add, in short simple English: `Gap 2 (R5 – "<field>"): No min/max length, so BVA can't be applied. Add EP/BVA cases? If yes, what are min and max?`
- **Yes** → add, using the user's value/outcome; without a value → one case with "not defined in the BRD" + `Depend on BRD or User Story`. **No** → no case; `Not needed (user)` in Gaps. **No answer / don't know** → no case; `Open – no answer` in Gaps and in the business gaps list.

## 6. No duplicates
- Same action + data condition + outcome = one case, mapped to every requirement it covers.
- EP valid representative = the positive case. Coinciding BVA values are written once (min−1 = 0 = empty-mandatory case; min+1 = max−1 in small ranges).
- Shared steps (login, open page) don't make a duplicate. Each invalid partition (no @, no domain, spaces) is its own case.

## 7. Columns (exact headers, exact order)
Activity Type (`Test Case`) · Title (§8) · Details (§9) · Expected Results (§10) · Actual Results (`Depend on BRD or User Story`) · Status (empty) · Priority (`High`/`Medium`/`Low`) · Project (Project ID) · Parent Project Activity (its ID) · Format Text Editor Fields (always `1`; header has no "== 1"). Values the user gives (e.g. Status) override these.

## 8. Title
`Verify` + behavior + distinguishing condition, ~5–12 words, unique per sheet.
Good: `Verify error message when the "<field>" field is empty` · `Verify "<field>" rejects one character above the maximum length` · `Verify "<role>" cannot open "<page>" by direct URL`.
Bad: `Empty field` (too short); titles listing steps or several checks (too long).

## 9. Details
- `- Precondition: …` lines first (account, role, data state) when needed.
- Then one step per line starting with `- ` (line breaks inside the cell, no numbering). First step opens the full URL of the given environment: `- Open the "<page>" page <environment URL><path>`
- Mid-case checks allowed: `- Verify the "<page>" page opens (<path>).`
- **Test data inside the step**: kind of value + example with `like ex:`; never "valid data" / "any value". Examples obey the stated rules.
  - `- Enter a valid registered email like ex: "<registered email>" in the "<email field>" field.`
  - `- Enter a not valid email without domain like ex: "<name>@" in the "<email field>" field.`
  - `- Upload a not valid file type (allowed: <types>) like ex: "file.<type>" in the "<attachment field>" field.`
  - `- Leave the "<field>" field empty.`
- Forms: one step per field in on-screen order (Enter / Select / Check / Upload), then the click.
- Negative cases: all other fields valid (written out), only the field under test invalid, with the reason stated. Use only invalid kinds the rule or field type implies; others are gaps.
- Realistic data: BRD formats, the system's email domain (from the inputs/user), Arabic names for Arabic fields, real dropdown options. Unique values when creating data (`tc-<feature>-03@<domain>`). Login names the account (`the "<role>" account like ex: "<account email>" and its password`); never real passwords.
- Long values: `"a" repeated <n> times (<n> characters, max is <max>)`.

## 10. Expected Results
- 1–2 English sentences with an observable final outcome: message text, URL/page, field state, record shown, element visible/hidden/disabled. Never just "works correctly / as expected / successfully".
- Quote exact texts from the inputs once, in the language of the page under test, and name each quote: `The error message "<exact message>" is shown under the "<field>" field.` (email body: `The email shows the title "…" and the button "…".`)
- Outcome not stated → `Depend on BRD or User Story`.

## 11. EP & BVA
**EP**: one representative per partition, each its own case with the other fields valid. Partitions come only from stated rules; others are gaps.
| Rule | Valid | Not valid |
|---|---|---|
| Range (length, number, amount, date, size, count) | middle value | below min; above max |
| Format (email, mobile, ID, date) | correct format | each way to break it (no @, no domain, spaces) |
| Allowed chars | only allowed chars | each disallowed class (digits, letters, special) |
| List (dropdown, file types, statuses) | each value with different behavior, else one | outside value, if it can be entered |
| Mandatory | filled | empty; spaces only (if trimming stated) |
| Roles | each role with distinct access | role without access |
| States (active/inactive, pending/approved) | each BRD state | — |

**BVA (3-value)** for every stated edge: min → `min−1` ✗, `min` ✓, `min+1` ✓; max → `max−1` ✓, `max` ✓, `max+1` ✗; exact n → `n−1`, `n`, `n+1`.
- Step = smallest unit: 1 char/digit/item/attempt/day, 0.01 for 2-decimal amounts, stated unit for size/timeout.
- Attempts: N−1 → not locked, N → locked (own account each). Timeout: just before → active; at/after → expired.
- Skip nonsense values (negative length); merge coinciding ones (§6).
- maxlength fields: `max+1` checks the extra char isn't accepted; block vs error not stated → `Depend on BRD or User Story` + gap.

## 12. Independent, testable, ordered
- Never reference another case ("same as above", "previous TC", data created elsewhere). Each row has its account/role, preconditions with exact data (`- Precondition: A "<record>" in "<status>" status exists for "<account>"`) or creates the data itself, the start URL and all data.
- State-changing cases (lockout) use a dedicated account.
- Concrete actions on named elements; one objective → one outcome (split any "and also verify…").
- Same wording style across rows. Order: per requirement → positive, EP invalid, BVA, roles, audit, UI, non-functional; then Security, then Usability.
- Priority: High = core flows, security, permissions, business-critical limits (amounts, attempts); Medium = validations, format/length EP/BVA, secondary flows, usability, non-functional; Low = cosmetic/rare.

Good (pattern for any form):
```
Title: Verify error message when entering an email without domain in the "<form>" form
Details:
- Open the "<page>" page <environment URL><path>
- Enter a valid value like ex: "<valid value>" in the "<other mandatory field>" field.
- Enter a not valid email without domain like ex: "<name>@" in the "<email field>" field.
- Click "<submit button>".
Expected Results: The error message "<exact message>" is shown under the "<email field>" field and the form is not submitted.
```
Bad: `Title: Invalid email` / `Details: - Open the form from the previous test case and enter invalid data.` / `Expected Results: An error appears.`

## 13. Deliverables
Never write openpyxl code. Save the data as JSON in a work folder (not the delivery folder) and run `python3 <this skill's folder>/scripts/build_xlsx.py data.json <delivery folder>` (needs `pip install openpyxl`). It builds both files in the exact template and style, fills the fixed columns and the coverage titles/counts/status, and prints the counts for the chat reply plus warnings. Fix every warning and re-run.
```json
{"feature": "<Feature>", "project": "<Project ID>", "parent": "<Parent ID>",
 "cases": [{"title": "", "details": "- …\n- …", "expected": "", "priority": "High",
            "reqs": ["R1", "R4"], "kind": "FUNC|EP|BVA|NFR|SEC|USA", "field": "<field>", "gap": false}],
 "coverage": [{"req": "R1", "requirement": "", "coverage": "Not Covered"}],
 "ep_bva": [{"field": "<field>", "req": "R1", "rule": "", "valid": "", "not_valid": "", "boundaries": ""}],
 "gaps": [{"type": "", "req": "", "description": "", "question": "", "decision": ""}]}
```
- `cases`: in §12 order. `reqs` = every requirement the case covers (SEC/USA cases may omit it). `field` links EP/BVA cases to their `ep_bva` row. `gap: true` = added from a confirmed gap. Optional `status` overrides Status.
- `coverage`: every requirement from §3. Set `coverage` only to override the auto value (no cases → Not Covered; any Expected with `Depend on BRD or User Story` → Partially Covered; else Covered), e.g. Not Covered when the user said no or the gap is still open. SEC/USA rows are added automatically.
- `gaps.decision`: `Added` / `Not needed (user)` / `Open – no answer` / `Written with Depend on BRD or User Story` / `Security/Usability case – written, rule to confirm with business`.
- Output: `<Feature>_Test_Cases.xlsx` (upload: one sheet `Table 1`) and `<Feature>_Coverage_and_Gaps.xlsx` (user only: Requirement Coverage, EP & BVA, Gaps; all English, e.g. `As a Visitor I want…`, never `As a Visitor (الزائر)…`).
- Script can't run → build the same layout by hand: header row + one case per row, no ID/extra columns, merged cells, blank rows or extra sheets; Arial, wrapped text, frozen header.

**Chat reply (short)**: inputs used and anything inaccessible; the script's counts + duplicates avoided; **Business gaps to raise** as a numbered list: security first, then usability, then unanswered questions (`Open – no answer`) and fields without rules.
If the user wants chat instead of files: a Markdown table with the 10 columns, then the coverage, EP & BVA and gaps tables.

## 14. Self-check (the script checks format, IDs, duplicate titles, placeholders, Arabic outside quotes, URL and vague Expected)
- Every limit comes from the inputs/user; EP/BVA complete for each stated rule; fields without rules are gaps.
- Security and Usability checklists applied wherever triggered; their undefined values are business gaps.
- Nothing outside the inputs except Security/Usability and confirmed gaps; no duplicate behaviors.
- Every missing or unclear point (incl. vague non-functional wording) was asked, never assumed; unanswered ones are `Open – no answer` gaps.
- `like ex:` data in every step; one invalid field per negative case; each row independent with one observable outcome.
