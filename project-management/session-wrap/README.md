# /wrap -- Session Wrap-Up

Generate a rich session summary with accomplishments, decisions, learnings, and automatic git commits at the end of each work session.

## What It Does

When you're done working, `/wrap` closes the session cleanly:

1. **Summarizes** what was accomplished (narrative, not just file lists)
2. **Captures** decisions made and why, plus learnings discovered
3. **Commits** outstanding work with a descriptive message
4. **Logs** everything to a daily digest file for future reference

The key difference from just committing and walking away: `/wrap` captures the *reasoning* behind the work, not just the artifacts. When you come back tomorrow, the daily log tells you what you did and why -- not just which files changed.

## When to Use It

- End of a work session (natural stopping point)
- Before context gets long and you want to start fresh
- When switching between projects or tasks
- Any time you want a clean handoff to your future self

## Example Usage

```
/wrap
>> Generates summary, commits work, writes daily log

# Or natural language
wrap up
let's close
end session
```

## Output

```
>> Session wrapped
   Duration: 2h 15m
   Accomplishments:
     - Built the export pipeline with CSV and JSON support
     - Fixed the auth flow that was dropping sessions after 30 minutes
   Decisions: 2
   Learnings: 1
   Commits: 3 (this session)
   Files changed: 8
   Log: docs/daily-logs/sessions/2026-04-04.md
```

## Daily Log Format

Each wrap appends to the day's log file. Two formats supported:

**JSONL** (machine-readable, at `docs/daily-logs/sessions/YYYY-MM-DD-digests.jsonl`):
```json
{
  "date": "2026-04-04",
  "duration_minutes": 135,
  "accomplishments": ["Built export pipeline", "Fixed auth session drops"],
  "decisions": ["Chose CSV over Parquet for compatibility"],
  "learnings": ["Session timeout was caused by missing keep-alive header"],
  "commits": [{"hash": "abc1234", "message": "feat: add export pipeline"}]
}
```

**Markdown** (human-readable, at `docs/daily-logs/sessions/YYYY-MM-DD.md`):
```markdown
_Session wrapped: 2026-04-04 18:30 (duration: 2h 15m)_
**Accomplishments:**
  - Built export pipeline with CSV and JSON support
  - Fixed auth session drops (missing keep-alive header)
**Decisions:**
  - Chose CSV over Parquet -- broader tool compatibility outweighs compression
```

## Features

- **Continuation support** -- If you `/wrap` twice in one session, the second wrap appends new work instead of duplicating
- **Smart git hygiene** -- Auto-commits outstanding changes, but pauses for confirmation if it detects potential secrets (.env, credentials files)
- **Memory extraction** -- Suggests observations worth persisting across sessions (you approve before anything is saved)
- **Client/project allocation** -- Optional multi-project time tracking with auto-detection

## Install

**Option A: Script**
```bash
python install.py session-wrap
```

**Option B: Manual**
Copy `project-management/session-wrap/` to `.claude/skills/session-wrap/`

Then create `docs/daily-logs/sessions/` in your project for the daily log files.

## Requirements

- Claude Code (any version with skill support)
- Git (for commit history and auto-commit)
- No external dependencies
