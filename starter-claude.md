# CLAUDE.md -- Starter Configuration

# Copy this file to your project root as CLAUDE.md.
# Claude Code reads it automatically. Each section below is independently useful --
# keep what helps, remove what doesn't, add your own.

## Iteration Philosophy

When fixing or improving code, follow this approach:

1. **Understand before changing** -- read error messages, trace the logic, identify root cause
2. **Make precise changes** -- fix the identified problem, nothing more
3. **Validate no regressions** -- check that existing functionality still works

Red flags you're over-engineering:
- Adding new sections when a phrase change would work
- Making changes before understanding the root cause
- Creating nested logic when one clear instruction suffices

## File Creation Policy

All temporary and session-ephemeral files go in `.scratch/` at the project root.

Before creating ANY file, ask: "Will this outlive the current session?"
- **No** --> `.scratch/` (use dated subdirs if needed: `.scratch/2026-02-15/`)
- **Yes** --> proper project directory

`.scratch/` should be in your `.gitignore`. It is safe to wipe anytime.

### What goes in .scratch/
- One-off scripts, debugging, quick analysis
- Intermediate outputs (temp JSON, CSV, text dumps)
- Test files and scratch notes

### What stays in the project tree
- Pipeline scripts that run repeatedly
- Config files and versioned content
- Deliverables and outputs meant to persist

## Writing Standards

- **Know your reader.** Every document is written for its specific audience.
- **Why before what.** Context first, then details.
- **No jargon before explanation.** If a term hasn't been introduced, don't use it.
- **Use dates, not relative time.** "Tomorrow" is meaningless when someone reads it later.

## Adding Skills

Skills live in `.claude/skills/`. Each skill is a folder with a `SKILL.md` file.

To add a skill:
1. Create `.claude/skills/<skill-name>/`
2. Copy the `SKILL.md` (and any reference files) into that folder
3. Claude Code picks it up automatically -- no restart needed

To invoke a skill, use its name as a slash command: `/<skill-name>`

Browse skills at: https://github.com/TomasB2BC/claude-code-toolkit
