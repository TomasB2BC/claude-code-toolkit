---
name: wrap
description: "Generate a rich session summary with accomplishments, decisions, learnings, and optional git hygiene. Triggers on '/wrap', 'wrap up', 'let's close', 'end session'."
triggers: ["wrap", "wrap up", "let's close", "end session", "close out"]
---

# Session Wrap-Up

You are generating a graceful session closure. Your job: summarize what happened, capture decisions and learnings, commit outstanding work, and leave a clean trail for the next session.

## Step 1: Read Session Context

Gather what happened this session from available sources:

1. **Git history**: Run `git log --oneline --since="<session_start>"` for commits during this session
2. **Modified files**: Run `git diff --name-only` and `git diff --cached --name-only` for uncommitted work
3. **Your conversation memory**: What tasks were worked on, what decisions were made, what was discussed

If git history is unavailable, generate the summary from your in-session memory instead.

### Continuation Detection

Before proceeding, check if this session was already wrapped:

1. Check if a wrap digest already exists for the current session in the daily log file
2. If found: print `>> Continuing wrap (prior wrap at {time}). New work will be appended.` and only summarize work done SINCE the prior wrap.
3. If not found: proceed normally.

## Step 2: Generate Summary

Using your full session context (not just file names), produce:

1. **Accomplishments** -- Narrative summaries of what was achieved (not just "Modified 5 files" but what the modifications accomplished and why they matter)
2. **Decisions** -- Key decisions made during this session and WHY they were made. Include tradeoffs considered.
3. **Learnings** -- Anything discovered, confirmed, or changed understanding. Include technical findings and process observations.
4. **Blockers** -- Any blockers encountered, whether resolved or still open.

## Step 3: Client/Project Allocation (Optional)

If you track time across clients or projects:

- Analyze the session work to build an allocation estimate
- If single client/project at 100% with no ambiguity, just print it and move on
- If multiple clients/projects or unclear split, ask for correction:
  ```
  Client allocation: [project-a: 60%, project-b: 40%]
  Correct? (Press Enter to confirm, or provide corrections)
  ```

If you don't use multi-client tracking, skip this step.

## Step 4: Memory Extraction

Review the session for memory candidates -- observations that should persist across sessions. Only extract entries that qualify under at least one criterion:

- (a) Changes behavior (how you work, communicate, or make decisions)
- (b) Documents a commitment (promises made, agreements reached)
- (c) Records decision rationale (why you chose X over Y)
- (d) Is a stable recurring fact (confirmed more than once)
- (e) Was explicitly requested by the user

For qualifying entries:
- Suggest adding to persistent memory: "From this session, I suggest noting: [entry]"
- For observations about the user: ALWAYS ask before storing. Never auto-promote.

## Step 5: Write the Digest

Write the session summary to a daily log file. Choose the format that fits your project:

### Option A: JSONL (machine-readable, recommended)

Append to `docs/daily-logs/sessions/YYYY-MM-DD-digests.jsonl`:

```json
{
  "session_id": "<unique-id>",
  "date": "YYYY-MM-DD",
  "started_at": "<ISO timestamp>",
  "ended_at": "<ISO timestamp>",
  "duration_minutes": 45,
  "end_reason": "graceful_wrap",
  "accomplishments": ["Narrative accomplishment 1", "Narrative accomplishment 2"],
  "decisions": ["Decision and rationale"],
  "learnings": ["Learning 1"],
  "blockers": [],
  "files_changed": ["path/to/file1.py", "path/to/file2.md"],
  "commits": [{"hash": "abc1234", "message": "commit message"}]
}
```

**Always use append mode** (`open('a')`) -- never read-all-write-all, as parallel sessions may write to this file concurrently.

### Option B: Markdown (human-readable)

Append to `docs/daily-logs/sessions/YYYY-MM-DD.md`:

```markdown
---
_Session wrapped: TIMESTAMP (duration: Xh Ym)_
**Accomplishments:**
  - Narrative accomplishment 1
  - Narrative accomplishment 2
**Decisions:**
  - Decision + rationale
**Learnings:**
  - Learning
**Files changed:** N files
**Commits:**
  - hash: message
```

You can use both formats (JSONL for programmatic access, markdown for human scanning).

## Step 6: Git Hygiene -- Auto-Commit Session Work

Commit this session's outstanding work automatically. This step runs AFTER digest writing so that digest files are included.

1. Gather the accomplishments list from Step 2.
2. Run `git status` to see what's uncommitted.
3. Stage and commit with a descriptive message derived from the accomplishments.
4. **Edge case handling (only these pause):**
   - If files that may contain secrets are detected (.env, credentials, tokens): ask the user "These files may contain secrets: {list}. Commit, skip, or add to .gitignore?"
   - If commits fail (pre-commit hook rejection): report the failure and continue. Do NOT retry with --no-verify.
   - If no uncommitted changes: skip this step silently.

**Auto-commit is the default.** Do not ask for confirmation unless sensitive files are detected.

## Step 7: Report

Print the final summary:

```
>> Session wrapped
   Duration: Xh Ym
   Accomplishments:
     - accomplishment 1
     - accomplishment 2
   Decisions: N
   Learnings: N
   Commits: N (this session)
   Files changed: N
   Log: docs/daily-logs/sessions/YYYY-MM-DD.md
```

## Important Constraints

- Keep the total output concise. The narrative value of /wrap is in quality, not quantity.
- Do NOT modify session tracking files that other hooks may depend on.
- If session data is unavailable, generate from in-session memory. Never block on missing data.
- No emojis in any output. Use `[OK]`, `[!]`, `>>` for indicators.
