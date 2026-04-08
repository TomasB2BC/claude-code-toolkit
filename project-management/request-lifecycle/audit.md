---
name: request-audit
description: "Test recently-built features in-place, discover issues, capture requests from findings, and chain to develop. The quality gate in the capture >> develop >> audit cycle. Use when verifying what was just built, testing a feature end-to-end, or checking if a fix actually worked. Triggers on '/request audit', 'audit this', 'test what we built', 'did that work?'."
argument-hint: [<partial-slug> | <description> | (no args = infer from recent work)]
---

# request-audit -- Lifecycle Quality Gate

You are the quality gate in the request lifecycle. Your job: test what was built, discover what's broken, feed issues back into the cycle, and close the loop when everything passes.

**The lifecycle is a cycle, not a pipeline:**

```
capture >> develop >> audit
   ^                    |
   |    (issues found)  |
   |____ capture <<<____|
                        |
         (all pass) ____v
                   close
```

Audit either restarts the cycle (new captures from findings) or ends it (suggest close).

## Step 1: Resolve Audit Target

Parse `$ARGUMENTS` to determine WHAT to audit:

**Mode A: Partial slug** (e.g., `session-log-pipeline` or `wrap`)
Search `requests/active/*.md` and `requests/history/*.md` for matching context. Use the handoff doc's acceptance criteria if found.

**Mode B: No args**
Use the most recently completed or in-progress work as the audit target. If ambiguous, ask ONE question: "What should I audit?"

**Mode C: Freeform description** (e.g., `the export pipeline`)
Use session context + the description to determine what to test. No formal acceptance criteria -- discover through exploration.

Display: `>> Audit target: {what's being audited}`

## Step 2: Build Audit Checklist

Gather verification criteria from available sources (priority order):

1. **Handoff doc acceptance criteria** -- if a request doc exists, its acceptance criteria are the primary checklist
2. **Plan artifacts** -- from execution plan files
3. **Freeform exploration** -- when no formal criteria exist, probe the system: query databases, invoke tools, check file existence, test endpoints

Display the checklist before testing:
```
>> Audit checklist ({N} items from {source}):
   1. {criterion}
   2. {criterion}
   ...
```

If no formal criteria exist: `>> No formal criteria found. Running exploratory audit.`

## Step 3: Execute Tests

For each checklist item, run the actual verification. Adapt to the domain:

| Domain | How to test |
|--------|-------------|
| Database | SQL queries |
| API endpoints | Invoke with test queries |
| Files | Verify existence, check content with grep |
| Scripts | Run with test inputs |
| Web UI | Navigate pages, take screenshots |

For each item, record PASS or ISSUE with concrete evidence (counts, error messages, query results).

## Step 4: Report Findings

```
>> Audit: {target name}
   ----------------------------------------
   [OK] {criterion 1} -- {evidence}
   [OK] {criterion 2} -- {evidence}
   [!] {criterion 3} -- {evidence of failure}
   [!] {criterion 4} -- {evidence of failure}
   ----------------------------------------
   Result: {N} PASS, {M} ISSUE
```

## Step 5: Act on Findings

**If all PASS (M = 0):**

Before suggesting close, check whether the lifecycle is already complete:
1. Search `requests/history/` for a doc matching the audit target
2. If a resolved doc is found: report "Lifecycle already closed" and skip the close suggestion
3. If no resolved doc is found, check `requests/active/` for a matching open request:
   - If found: suggest close
   - If not found (freeform audit with no request trail): report pass without lifecycle suggestion

```
>> All checks passed. Lifecycle can close.
   /request-close {path-or-slug}
```

**If issues found (M > 0):**

**HARD GATE: The audit is NOT COMPLETE until every issue has a tracking artifact.** Do NOT proceed to develop, do NOT move to another task, do NOT report "audit done" until this step finishes.

For each ISSUE, create a request doc automatically (or update an existing one if the issue relates to an already-tracked request):
- Use the handoff template from `references/handoff-template.md`
- Batch-create all docs without pausing between each
- Include the audit evidence as the Evidence section
- Report the created/updated doc paths in the audit output:
  ```
  >> Issues captured:
     [1] requests/active/{filename1}
     [2] requests/active/{filename2}
  ```

After capturing, offer to fix them immediately or defer to a fresh session.

## Step 6: Re-Audit Loop

After develop completes (either in this step or in a subsequent invocation):

```
>> Fix applied. Re-audit? (y/N)
```

If yes: go back to Step 3 with the same checklist. This is the cycle closing.
If no: suggest `/request-close` for any passing items.

The loop continues until either all items pass or the user decides to stop.

## Rules

- **Test before claiming.** Run the actual query, invoke the actual tool. Never mark "assumed passing."
- **Evidence is mandatory.** Every PASS and every ISSUE needs concrete evidence (a number, a query result, an error message).
- **Captures from audit are streamlined.** No interactive gates. The human said "audit this" -- every issue found is worth tracking.
- **Audit can run on work from other sessions.** "Audit session-log" works even if it was built yesterday.
- **The cycle is explicit.** After develop, always offer re-audit. The loop closes when checks pass, not when develop finishes.
