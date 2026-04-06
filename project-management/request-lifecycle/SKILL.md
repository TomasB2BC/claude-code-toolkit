---
name: request
description: "Skill lifecycle harness -- capture bugs and improvements, develop fixes with full documentation trail, audit what was built. Three sub-commands: /request-capture (report bugs, propose improvements), /request-develop (execute work with mandatory trail), /request-audit (test and discover issues). Use when something needs fixing but not right now, when picking up work from a previous session, or when testing what was just built."
argument-hint: [capture | develop | audit | status]
---

# /request -- Skill Lifecycle Harness

A structured system for tracking and executing work across sessions. Three commands form a cycle:

```
capture >> develop >> audit
   ^                    |
   |    (issues found)  |
   |____ capture <<<____|
                        |
         (all pass) ____v
                   close
```

## Hub: /request

Shows the current state and routes to the right sub-command.

### Step 1: Read Pipeline State

1. Glob `requests/active/*.md` -- count open requests, parse frontmatter for name, severity, and title.
2. Glob `requests/history/*.md` -- count resolved requests (check dates for recent activity in last 7 days).

### Step 2: Display Dashboard

```
>> Request Lifecycle -- Status
   --------------------------------
   Open requests:    N
   Recently closed:  N (last 7 days)

   Open requests:
     - [severity] name: title (date)
     ...
```

If no open requests: `Open requests: 0 -- all clear.`

### Step 3: Route

```
>> Available commands:
   /request-capture    Capture a bug, improvement, or work handoff
   /request-develop    Pick up and execute a captured request
   /request-audit      Test what was built, discover issues
```

### Step 4: Suggest Next Action

- If open requests exist: "Suggested: `/request-develop requests/active/{oldest}.md`"
- If no open requests: "No open requests. Use `/request-capture` to file new work."

---

## /request-capture -- Cross-Session Work Handoff

Capture context from the current session so another session can pick up the work with full understanding. The handoff document is the atomic unit of work transfer.

The insight: Claude Code IS the best bug reporter when it encounters a problem mid-session. You have the full context -- what happened, what was attempted, what the human said. But acting on the fix NOW would context-switch away from the current task. Instead, dump the context into a structured doc and return to the original work.

### Mode Detection

Parse arguments to determine mode:

| Signal | Mode |
|--------|------|
| Bug/issue context | **report** (default) |
| `--update <name>` | **update** (skill improvement) |
| `--project` | **project** (new project needed) |

### Report Mode

Use when a bug, unexpected behavior, or improvement need surfaces mid-session.

**Step 1: Gather context from the session**

You were THERE when this happened. Pull from conversation history -- do NOT interrogate the user with a questionnaire. Extract:

1. **What we were doing** -- task, goal
2. **What happened** -- the specific failure or unexpected behavior
3. **What was attempted** -- workarounds, partial fixes, things tried
4. **The interaction** -- what the human said/did that triggered or revealed it
5. **Evidence** -- logs, outputs, error messages. Raw data.
6. **Root cause hypothesis** -- your best understanding of WHY
7. **Affected systems** -- file paths, modules, tools
8. **Acceptance criteria** -- how to verify a fix works

**Step 2: Write the handoff document**

Write the document to:
```
requests/active/YYYY-MM-DD-{slug}.md
```

Use this template:

```markdown
---
status: open
date: YYYY-MM-DD
severity: low | medium | high
system: "{primary file or module affected}"
title: "{descriptive title}"
---

# {Title}

## Context
{What we were doing, what happened}

## Evidence
{Logs, error messages, outputs}

## Root Cause Hypothesis
{Best understanding of why this happened}

## Affected Systems
{File paths, modules, tools}

## Acceptance Criteria
- [ ] {Criterion 1 -- how to verify the fix works}
- [ ] {Criterion 2}

## Resolution
{Filled by /request-develop after the fix}
```

Generate the slug from the issue description (kebab-case, max 60 chars). Fill every section from session context. Set `status: open` in frontmatter.

**Step 3: Confirm and return**

```
Request captured:
  Doc: requests/active/{filename}
  Severity: {level}

Returning to original work.
```

Do NOT start fixing the issue. Context capture, not context switch.

### Update Mode

Use when a skill or module needs intentional improvement -- not a bug, but a feature addition, refactor, or enhancement.

Same as Report Mode but framed as an improvement. Include a specification section describing what should change, test cases, and edge cases.

### Project Mode

Use when the scope exceeds a single request -- a new project is needed. Capture the vision and scope in a handoff doc formatted for project bootstrapping.

### Rules

- **Never fix the issue.** Capture context, create tracking, return to work.
- **Never interrogate with questionnaires.** You have the session context -- use it.
- **Write to `requests/active/`.** This is the canonical location for active requests. Resolved requests go to `requests/history/`.
- **Keep report mode under 2 minutes.** Dump context quickly, don't over-analyze.

---

## /request-develop -- Request Execution Orchestrator

Pick up a captured request and drive it to completion. Load the handoff doc, decide on approach, execute, verify against acceptance criteria, and produce a mandatory documentation trail.

### Step 1: Load the Request

Parse arguments and resolve to a handoff doc path. Four input modes:

**Mode A: Full path** (e.g., `requests/active/2026-04-04-foo.md`)
Read the handoff doc directly.

**Mode B: Partial slug** (e.g., `session-log` or `wrap`)
Glob `requests/active/*{arg}*.md`. If exactly one match, use it. If multiple, show picker. If none: "No open request matching '{arg}'."

**Mode C: No args**
Show a picker of all open requests:
1. Glob `requests/active/*.md`
2. For each: read frontmatter, extract name, severity, date
3. Filter to `status: open` only
4. Sort by severity (high first), then date (oldest first)
5. Present options formatted as: `"{title} [{severity}] ({date})"`
6. If zero open requests: "No open requests. Use /request-capture to create one."

### Step 2: Assess State

Read the handoff doc and extract:

| Field | Where | Purpose |
|-------|-------|---------|
| status | frontmatter | If `resolved`, warn: "This request is already resolved. Re-open it?" |
| system | frontmatter | Identifies the target file/module |
| Acceptance Criteria | section | Exit gate -- every criterion must pass with evidence |
| Affected Systems | section | Scope assessment for routing |

### Step 3: Route to Approach

```
Assess from Affected Systems + Context section:
  |
  Bug with symptoms but unknown root cause?
    YES --> Debug route
    |         Hypothesis-driven investigation before fixing
    |
  Single file, clear spec, no cross-system dependencies?
    YES --> Direct edit route
    |         Make the changes yourself using Edit/Write
    |
    NO  --> Multi-file? Cross-system? Needs formal planning?
              YES --> Plan and execute route
```

**Every route produces the same trail.** The size of the change determines the edit approach, never the documentation approach.

### Step 4: Verify Against Acceptance Criteria

After the work is done, go through each acceptance criterion from the handoff doc:

1. Read the Acceptance Criteria section
2. For each criterion: run the verification (command, file check, test) and record PASS/FAIL with evidence
3. If any criterion fails: fix the issue and re-verify
4. Document results in the Resolution section

Do not skip this step. Do not mark criteria as "assumed passing." Run the actual checks.

### Step 5: Produce the Trail (NON-NEGOTIABLE)

A 2-line typo fix gets the same treatment as a 200-line rewrite. The trail IS the product. The fix is a side effect.

Edit the handoff doc's `## Resolution` section:

```markdown
## Resolution
**What changed:** {concrete description of changes made}
**Why:** {reasoning -- why this approach, what alternatives were considered}
**Commit:** {hash, or "pending commit" if not yet committed}
**Verification:**
- [x] Criterion 1: {evidence} -- PASS
- [x] Criterion 2: {evidence} -- PASS
```

### Step 6: Close

After the trail is complete:

1. Update handoff doc frontmatter: `status: open` >> `status: resolved`, add `resolved: {today}`
2. Move the handoff doc: `requests/active/` >> `requests/history/`

```
>> Request closed: {title}
   Status: resolved ({date})
   Moved to: requests/history/{filename}
```

### Batch Mode

When given multiple requests (multiple slugs, `--all-open`, or `--parallel slug1,slug2`):

1. Resolve all request paths
2. Check for file conflicts (two requests modifying the same file cannot run in parallel)
3. Partition into parallel and serial groups
4. Dispatch background agents for parallel work
5. Collect results and present consolidated summary

### Rules

- **Trail is mandatory.** Even for trivial changes. No exceptions.
- **Always close after trail.** The human approved the work by invoking develop. Bookkeeping doesn't need a second approval.
- **Never skip acceptance criteria verification.** Run the checks, record evidence.

---

## /request-audit -- Lifecycle Quality Gate

Test what was built, discover what's broken, feed issues back into the cycle, and close the loop when everything passes.

### Step 1: Resolve Audit Target

Parse arguments to determine WHAT to audit:

- **Path or slug** -- look up the request doc, use its acceptance criteria
- **No args** -- use the most recently completed work as the audit target
- **Freeform description** (e.g., "the export pipeline") -- probe the system through exploration

### Step 2: Build Audit Checklist

Gather verification criteria from available sources (priority order):

1. **Handoff doc acceptance criteria** -- primary checklist if a request doc exists
2. **Plan artifacts** -- from execution plan files
3. **Freeform exploration** -- when no formal criteria exist, probe the system

Display the checklist before testing:
```
>> Audit checklist ({N} items from {source}):
   1. {criterion}
   2. {criterion}
   ...
```

### Step 3: Execute Tests

For each checklist item, run the actual verification. Adapt to the domain:

| Domain | How to test |
|--------|-------------|
| Database | SQL queries |
| API endpoints | Invoke with test queries |
| Files | Verify existence, check content with grep |
| Scripts | Run with test inputs |
| Web UI | Navigate pages, take screenshots |

For each item, record PASS or ISSUE with concrete evidence.

### Step 4: Report Findings

```
>> Audit: {target name}
   ----------------------------------------
   [OK] {criterion 1} -- {evidence}
   [OK] {criterion 2} -- {evidence}
   [!] {criterion 3} -- {evidence of failure}
   ----------------------------------------
   Result: {N} PASS, {M} ISSUE
```

### Step 5: Act on Findings

**If all PASS:** suggest closing the request.

**If issues found:** for each ISSUE, create a new request doc automatically (streamlined, no interactive gates). Then offer to fix them immediately or defer to a fresh session.

### Step 6: Re-Audit Loop

After fixes are applied:
```
>> Fix applied. Re-audit? (y/N)
```

The loop continues until either all items pass or the user decides to stop.

### Rules

- **Test before claiming.** Run the actual check. Never mark "assumed passing."
- **Evidence is mandatory.** Every PASS and every ISSUE needs concrete evidence.
- **Captures from audit are streamlined.** No interactive gates for issue filing.
- **The cycle is explicit.** After develop, always offer re-audit.

---

## Setup

To use this skill family, create these directories in your project:

```
requests/
  active/       # Open request handoff docs
  history/      # Resolved request docs (moved here after close)
```

The skill works standalone with no external dependencies. All state lives in the request documents themselves -- frontmatter tracks status, the Resolution section tracks what was done, and the file location (active vs history) indicates lifecycle state.
