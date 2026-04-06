---
name: request-close
description: "Atomic one-command close for the request lifecycle. Handles all bookkeeping steps -- status update, Resolution fill, doc move to history. Use when closing a request, finishing work, wrapping up a request. Triggers on 'close request', 'request close', 'finish request', 'mark as done', '/request close', 'finalize request'."
argument-hint: [<path> | <partial-slug> | (no args = picker)] [--maturity <level>]
---

# request-close -- Atomic Lifecycle Close

You are the enforcement mechanism for trail-over-fix. One command, all steps, zero manual follow-up. The user invokes you once; you handle everything.

The insight: trail-over-fix creates multiple artifacts per lifecycle event. If the user remembers them all manually, compliance erodes. You make the right thing the easy thing.

## Arguments

Parse `$ARGUMENTS` and resolve to a handoff doc path. Three input modes:

**Mode A: Full path** (e.g., `--request requests/active/2026-04-04-foo.md`)
Read the handoff doc at that path directly.

**Mode B: Partial slug** (e.g., `session-log` or `wrap`)
Glob `requests/active/*{arg}*.md`. If exactly one match, use it. If multiple, show picker. If none: "No closeable request matching '{arg}'."

**Mode C: No args**
Show a picker of closeable requests (those with filled Resolution sections):
1. Glob `requests/active/*.md`
2. For each: check if Resolution section has substance (not empty/placeholder)
3. Display closeable requests: `"{title} [{severity}] ({date})"`
4. If zero closeable: "No closeable requests. Use /request-develop first to fill a Resolution."

**Additional flag:** `--maturity <level>` -- maturity assessment: draft, tested, production, or shareable (prompted if not given)

## The Close Steps

Execute all steps in sequence. Steps that don't apply skip silently.

### Step 1: Update Handoff Doc Status

1. Read the handoff doc
2. Edit frontmatter: change `status: open` to `status: resolved`
3. Add `resolved: {today's date YYYY-MM-DD}` to frontmatter

### Step 2: Fill/Validate Resolution Section

The Resolution section is the heart of the trail. It must contain specifics, not placeholders.

**If Resolution is empty or placeholder text:**
- Auto-fill from git:
  - `git log --oneline -5` for recent relevant commits
  - `git log -1 --format=%H` for the commit hash
  - Today's date
  - Affected files from the handoff doc's Affected Systems section
- Write a concrete Resolution: what changed, why, commit hash, verification results

**If Resolution is already filled (by request-develop):**
- Validate: does it have a commit hash? Does it describe what changed specifically?
- If it says just "fixed", "done", or "updated" -- flag as insufficient and enrich from git

**Minimum valid Resolution:** what changed + commit hash + date. Anything less gets rejected and auto-filled.

### Step 3: Move Doc to History

1. Move the handoff doc to `requests/history/`:
   ```bash
   mv <active-path> requests/history/
   ```
2. Verify the file no longer exists in the source location.

## Maturity Assessment

If `--maturity` is not provided in arguments, you must ask before proceeding:

```
Maturity assessment required for {name}:
  - draft:      Created, not battle-tested
  - tested:     Evals pass, used in at least one real session
  - production: Battle-tested, stable, relied upon
  - shareable:  Production + portable + documented for external use

What maturity level?
```

This is the ONE thing the user must provide. Everything else is auto-filled.

## Output Format

After all steps complete, report what was done:

```
>> Request Closed: {title}
   --------------------------
   [1] Status: open >> resolved (YYYY-MM-DD)
   [2] Resolution: filled (commit {short hash})
   [3] Moved to: requests/history/{filename}

   Request lifecycle complete.
```

## Rules

- **One command = done.** If the user has to do anything after invoking close, the skill failed.
- **Maturity is mandatory.** Cannot close without an assessment.
- **Resolution must have substance.** Bare "fixed" or empty is rejected.
- **Auto-fill aggressively.** Commit hash, date, affected files -- derive from git and the doc.
- **Request docs canonical location:** `requests/active/` (active) and `requests/history/` (resolved). One location, no fallbacks.
