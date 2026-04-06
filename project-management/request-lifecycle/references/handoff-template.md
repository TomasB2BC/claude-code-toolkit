# Handoff Document Template

> Canonical handoff document template. Used by request-capture (write) and request-develop (read).
> Update HERE, not in individual sub-skills.

Save to `requests/active/YYYY-MM-DD-{slug}.md` using this template:

```markdown
---
type: request
status: open
created: {YYYY-MM-DD}
system: "{primary file or module affected}"
severity: {low|medium|high}
title: "{descriptive title}"
---

## Context
{What we were doing when this came up. Task, goal.}

## What Happened
{The specific problem. Concrete steps and observations, not abstractions.}

## What Was Attempted
{Workarounds, partial fixes, things tried. Include what DID work partially.}

## Interaction That Triggered It
{What the human said or did that revealed the issue.}

## Evidence
{Logs, outputs, error messages. Raw data.}

## Root Cause Hypothesis
{Best understanding of WHY. Code flaw vs config issue vs missing capability vs edge case.}

## Affected Systems
- File paths
- Modules / tools
- Dependencies

## Acceptance Criteria
{How to verify the fix works. Reproducible commands and expected results.}

## Skill-Creator Brief
{Only if affected system is a skill. What the skill should do, test cases,
expected behavior, edge cases. This section feeds the developer who picks
up this request.}

## Post-Completion Checklist
- [ ] Work completed and verified against acceptance criteria
- [ ] Request status updated to resolved
- [ ] Moved to requests/history/

## Resolution
{Populated by request-develop -- what was changed, why, commit hash, verification result.}
```

## Template Notes

- The `system:` field identifies the primary file or module affected. Used by batch mode for conflict detection.
- Resolution section is filled by request-develop, not by the user.
- Post-Completion Checklist items are handled automatically by request-close.
