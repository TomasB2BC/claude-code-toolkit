# Surgical Iteration

Drop this section into your CLAUDE.md to enforce precise, root-cause-driven changes instead of shotgun rewrites.

---

## Iteration Philosophy

When fixing or improving code, prompts, or documentation, follow this approach:

### 1. Understand Before Changing
- **Walk the trail** -- understand what the current code actually does
- **Analyze reasoning** -- if something failed, understand WHY it failed
- **Verify ground truth** -- check what's actually happening vs what you expect
- **Identify root cause** -- find the specific issue before proposing a fix

### 2. Make Precise Changes
- **Address the root cause** -- change what fixes the identified problem, nothing more
- **Avoid bloat** -- don't add new sections when a word change works
- **Use Edit over Write** -- preserve context by editing specific lines, not rewriting entire files

### 3. Validate No Regressions
- **Check what was working** -- ensure changes don't break existing functionality
- **Test incrementally** -- start small, expand gradually
- **Verify consistency** -- new changes should align with existing patterns

### Red Flags (You're Over-Engineering)
- Adding new sections when a phrase change would work
- Explaining the same concept multiple ways
- Adding emphasis markers everywhere ("CRITICAL", "IMPORTANT")
- Creating nested logic when one clear instruction suffices
- Making changes before understanding the root cause
