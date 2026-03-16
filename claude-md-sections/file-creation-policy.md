# File Creation Policy

Drop this section into your CLAUDE.md to prevent Claude Code from scattering temporary files across your project.

---

## File Creation Policy

**All temporary and session-ephemeral files go in `.scratch/` at the project root.**

`.scratch/` is gitignored, lives at project root, and is safe to wipe anytime (`rm -rf .scratch/*`). Use dated subdirectories when working on multiple things: `.scratch/2026-02-15/`.

Before creating ANY file, ask: "Will this outlive the current session?"
- **No** --> `.scratch/` (one-off scripts, debugging, temp data, scratch notes)
- **Yes** --> proper project directory (pipeline scripts, configs, deliverables)

### Rules
1. Never create files in the project root -- root is for repo config only
2. One-time-purpose scripts (analyze this CSV, debug this API, test this query) --> `.scratch/`
3. Pipeline scripts (run_pipeline.py, build.py) --> proper project directory
4. Never leave orphan files -- if you created a temp file outside `.scratch/`, delete it before finishing

### .gitignore Entry
```
.scratch/
```
