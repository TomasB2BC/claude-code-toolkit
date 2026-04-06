# /request -- Skill Lifecycle Harness

Track bugs, improvements, and cross-session work with a structured capture >> develop >> audit cycle.

## What It Does

Three commands form a continuous quality loop:

| Command | Role | When to Use |
|---------|------|-------------|
| `/request-capture` | Capture context | Bug surfaces mid-session, need to hand off work, want to improve a skill |
| `/request-develop` | Execute with trail | Picking up work from a previous session, executing a captured request |
| `/request-audit` | Test and discover | Verifying what was built, testing a feature end-to-end |

The key insight: Claude Code IS the best bug reporter when it encounters a problem mid-session. It has the full context -- what happened, what was attempted, what the human said. But fixing it NOW would context-switch away from the current task. The request family captures that context and drives it to resolution through the cycle.

## The Cycle

```
capture >> develop >> audit
   ^                    |
   |    (issues found)  |
   |____ capture <<<____|
                        |
         (all pass) ____v
                   close
```

- **Capture** creates a handoff doc with full context, evidence, and acceptance criteria
- **Develop** loads the handoff doc, makes the fix, verifies against acceptance criteria, writes a documentation trail, and closes the request
- **Audit** tests what was built, discovers new issues, feeds them back as new captures, or confirms everything passes

Every execution -- no matter how small -- produces a trail. A 2-line typo fix gets the same treatment as a 200-line rewrite.

## Example Usage

```
# Mid-session: something breaks but you don't want to context-switch
/request-capture
>> Captures the bug with full context, writes handoff doc, returns to original work

# New session: pick up work from the backlog
/request-develop session-log
>> Loads handoff doc, makes the fix, verifies acceptance criteria, writes trail, closes

# After building: verify everything works
/request-audit
>> Tests against acceptance criteria, discovers issues, feeds back into cycle

# Check pipeline state
/request
>> Shows open requests, recently closed, suggests next action

# Batch: develop all open requests in parallel
/request-develop --all-open
>> Dispatches background agents for independent requests, handles conflicts
```

## How It Works

### Handoff Documents

Every request produces a markdown document in `requests/active/`:

```markdown
---
status: open
date: 2026-04-04
severity: medium
system: "src/pipeline.py"
title: "Export fails on empty input"
---

# Export fails on empty input

## Context
Running the export pipeline with an empty CSV...

## Evidence
Error traceback...

## Root Cause Hypothesis
The pipeline doesn't check for empty input before...

## Acceptance Criteria
- [ ] Export handles empty CSV without error
- [ ] Output file is created (empty but valid)

## Resolution
{Filled after fix -- what changed, why, verification evidence}
```

### Documentation Trail

The Resolution section is non-negotiable. After every fix:

```markdown
## Resolution
**What changed:** Added empty-input guard in pipeline.py line 42
**Why:** Pipeline assumed non-empty input; guard is cheaper than restructuring
**Commit:** abc1234
**Verification:**
- [x] Export handles empty CSV -- ran with empty.csv, got valid empty output -- PASS
- [x] Output file created -- confirmed at output/result.csv (0 rows, headers intact) -- PASS
```

### Batch Mode

`/request-develop` supports parallel execution:
- Multiple slugs: `/request-develop fix-export fix-import fix-validate`
- All open: `/request-develop --all-open`
- Detects file conflicts and serializes conflicting requests automatically

## Directory Structure

```
requests/
  active/       # Open request handoff docs (status: open)
  history/      # Resolved docs (moved here after close)
```

## Install

**Option A: Script**
```bash
python install.py request-lifecycle
```

**Option B: Manual**
Copy `project-management/request-lifecycle/` to `.claude/skills/request-lifecycle/`

Then create the `requests/active/` and `requests/history/` directories in your project.

## Requirements

- Claude Code (any version with skill support)
- No external dependencies -- all state lives in markdown files
