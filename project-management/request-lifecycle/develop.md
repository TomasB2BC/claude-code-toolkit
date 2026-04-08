---
name: request-develop
description: "Pick up a captured request and drive it to completion. Loads handoff docs, decides approach (direct edits for simple fixes, debugging for unknown root cause, planning for complex multi-file work), executes, verifies against acceptance criteria, and produces a mandatory documentation trail. Supports batch mode for parallel dispatch of independent requests. Use when picking up work from a previous session, when a request needs executing. Triggers on 'develop request', 'pick up request', 'work on this request', 'execute this request', '/request develop', 'pick up where we left off', 'work on the backlog', 'develop all open requests'."
argument-hint: [<path> | <partial-slug> | <slug1> <slug2> ... | --all-open | --parallel <slug1>,<slug2> | (no args = picker)]
---

# request-develop -- Request Execution Orchestrator

You are the foreman of the request lifecycle. Your job: read the blueprint (handoff doc), pick the right tool, do the work, verify it, and sign off with documentation. Every execution -- no matter how small -- produces a trail.

## Step 0: Detect Mode (Single or Batch)

Before resolving request paths, check whether this is a single-request or batch invocation.

**Batch mode triggers:**
- `$ARGUMENTS` contains `--all-open`
- `$ARGUMENTS` contains `--parallel` followed by comma-separated slugs
- `$ARGUMENTS` contains multiple space-separated slugs (2+ args that are not flags)

If any batch trigger is detected, jump to **Batch Mode** (below Step 6). Otherwise, continue to Step 1 for single-request processing.

## Step 1: Load the Request

Parse `$ARGUMENTS` and resolve to a handoff doc path. Three input modes:

**Mode A: Full path** (e.g., `requests/active/2026-04-04-foo.md`)
Read the handoff doc at that path directly.

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

## Step 2: Assess State

Read the handoff doc and extract:

| Field | Where | Purpose |
|-------|-------|---------|
| status | frontmatter | If `resolved`, warn: "This request is already resolved. Re-open it?" |
| system | frontmatter | Identifies the target file/module |
| Acceptance Criteria | section | Exit gate -- every criterion must pass with evidence |
| Skill-Creator Brief | section | Spec input -- tells you WHAT to change |
| Affected Systems | section | Scope assessment for routing |

## Step 3: Route to Approach

Routing decides HOW you make the change. It does NOT affect the trail -- Steps 4 and 5 are identical regardless of route. There is no "simple" path that skips documentation.

If a Skill-Creator Brief exists in the handoff doc, use it as your spec -- it tells you what to change, test cases, and edge cases.

```
Assess from Affected Systems + Skill-Creator Brief + Context section:
  |
  Bug with symptoms but unknown root cause? Multiple symptoms that might share a cause?
    YES --> Debug route
    |         Hypothesis-driven investigation before fixing
    |
  Single file, clear spec, no cross-system dependencies?
    YES --> Direct edit route
    |         Make the changes yourself using Edit/Write
    |
    NO  --> Multi-file? Cross-system? Needs formal planning?
              YES --> Plan and execute route
              |
              MAYBE --> Your call. Explain the routing decision in the Resolution.
```

### Debug Route -- Investigate, Then Fix

When the request is a bug with unclear root cause, use structured debugging: hypothesis formation, evidence gathering, and root cause identification.

1. **Form hypotheses** from the handoff doc context
2. **Test each hypothesis** systematically -- run checks, read code, trace the logic
3. **Eliminate** hypotheses that don't match the evidence
4. **Document** what was investigated and ruled out (preserves the debugging reasoning)
5. **Fix** the identified root cause
6. **Continue to Step 4** (verify) with the fix in place

### Plan and Execute Route

For multi-file or cross-system changes, plan before acting:

1. **Map the scope** from the handoff doc's Affected Systems
2. **Create a plan** -- what to change, in what order, what to verify
3. **Execute the plan** step by step
4. **Continue to Step 4** (verify)

**Every route produces the same trail.** The size of the change determines the edit approach, never the documentation approach.

## Step 4: Verify Against Acceptance Criteria

After the work is done, go through each acceptance criterion from the handoff doc:

1. Read the Acceptance Criteria section
2. For each criterion: run the verification (command, file check, test) and record PASS/FAIL with evidence
3. If any criterion fails: fix the issue and re-verify
4. Document results in the Resolution section

Do not skip this step. Do not mark criteria as "assumed passing." Run the actual checks.

**Behavioral test mandate (skills):** If the change modifies a skill file, grepping for the text you just wrote is NOT verification. You must test the skill behaviorally: simulate an invocation with representative input and verify the output matches expectations. "Evidence" means actual output, not quotes from the file you edited.

## Step 5: Produce the Trail (NON-NEGOTIABLE)

This is the most important step. A 2-line typo fix gets the same treatment as a 200-line rewrite. The trail IS the product. The fix is a side effect.

### 5a: Fill the Resolution section

Edit the handoff doc's `## Resolution` section with:

```markdown
## Resolution
**What changed:** {concrete description of changes made}
**Why:** {reasoning -- why this approach, what alternatives were considered}
**Commit:** {hash, or "pending commit" if not yet committed}
**Verification:**
- [x] Criterion 1: {evidence} -- PASS
- [x] Criterion 2: {evidence} -- PASS
```

### 5b: Maturity assessment

Report current maturity level:
- `draft` -- created, not battle-tested
- `tested` -- evals pass, used in at least one real session
- `production` -- battle-tested, stable, relied upon
- `shareable` -- production + portable + documented for external use

Include the assessment and reasoning in the Resolution section.

## Step 6: Auto-Close

After the trail is complete, close the request automatically. The trail is written, the work is verified, the Resolution is filled. There is no human judgment needed for bookkeeping.

1. Update handoff doc frontmatter: `status: open` >> `status: resolved`, add `resolved: {today}`
2. Move the handoff doc: `requests/active/` >> `requests/history/`

```
>> Request closed: {title}
   Status: resolved ({date})
   Moved to: requests/history/{filename}
```

---

## Batch Mode -- Parallel Agent Dispatch

When Step 0 detects a batch invocation, this section governs execution instead of Steps 1-6.

### B1: Resolve Target Requests

**If `--all-open`:**
1. Glob `requests/active/*.md`
2. Read frontmatter of each, filter to `status: open`
3. Collect list of `{slug, path, system, severity}`

**If `--parallel slug1,slug2,...` or multiple space-separated slugs:**
1. For each slug, resolve via partial match against `requests/active/`
2. If any slug matches zero files: warn and skip it
3. If any slug matches multiple files: warn and skip it
4. Collect resolved list

Print the resolved list:
```
>> Batch mode: {N} requests resolved
   1. {title} [{severity}] -- {path}
   2. {title} [{severity}] -- {path}
```

### B2: Dependency and Conflict Check

**File conflict detection:**
1. For each request, extract the `system:` field -- this is the primary file it modifies
2. Also scan the Skill-Creator Brief for additional file paths
3. If two requests share ANY target file, they CONFLICT and cannot run in parallel

**Partition into execution groups:**
- **Parallel group:** All requests with no file conflicts
- **Serial groups:** Requests that conflict, ordered alphabetically

Print the dispatch plan:
```
>> Dispatch plan:
   Parallel (wave 1): request-a, request-b, request-c
   Serial (wave 2, after wave 1): request-d (conflicts with request-a on pipeline.py)
```

### B3: Dispatch Agents

For each request in the parallel group, spawn a background agent to run the full lifecycle (load >> assess >> route >> execute >> verify >> trail >> close).

### B4: Collect Results

After all agents complete, present the consolidated summary:

```
>> Batch development complete: {resolved}/{total} requests resolved

   [OK] request-a: resolved -- 2 files changed
   [OK] request-b: resolved -- 1 file changed
   [X]  request-c: FAILED -- acceptance criterion 3 failed (see handoff doc)
```

### B5: Error Handling

- **Request doc missing or malformed:** Skip with warning, continue batch. Do not block other requests.
- **Agent failure:** Report which request failed and why. Other agents continue independently.
- **Timeout:** If an agent has not completed after 15 minutes, report it as timed out. Do not block other agents.

## Rules

- **Trail is mandatory.** Even for trivial changes. This is the behavioral distinction between request-develop and ad-hoc editing. No exceptions.
- **Always auto-close after trail.** The human approved the work by invoking develop. Bookkeeping doesn't need a second approval.
- **Never skip acceptance criteria verification.** Run the checks, record evidence.
- **Request docs live in `requests/active/` (active) and `requests/history/` (resolved).** One canonical location, no fallbacks.
- **Batch mode: each agent owns its own trail.** The orchestrator produces the consolidated summary.
- **Batch mode: never dispatch conflicting requests in parallel.** File conflict detection is a hard gate, not a suggestion.
