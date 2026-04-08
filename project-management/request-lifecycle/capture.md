---
name: request-capture
description: "Capture work context for cross-session handoff -- bugs, improvements, skill updates -- as structured handoff docs. Use when a bug surfaces mid-session, when a skill needs improvement, when work needs to transfer between sessions. Triggers on 'file a request', 'capture this', 'request capture', 'track this bug', 'handoff', 'this needs fixing but not now'."
argument-hint: [--skill <name>] [--severity <low|medium|high>] [--project]
---

# /request-capture -- Cross-Session Work Handoff

You are capturing context from the current session so that another session can pick up the work with full understanding. The handoff document is the atomic unit of work transfer between sessions.

The insight: Claude Code IS the best bug reporter when it encounters a problem mid-session. You have the full context -- what happened, what was attempted, what the human said. But acting on the fix NOW would context-switch away from the current task. Instead, dump the context into a structured doc and return to the original work.

## Mode Detection

Parse `$ARGUMENTS` to determine mode:

| Signal | Mode |
|--------|------|
| `--project` flag | **project** |
| `--skill <name>` flag | **update** |
| Bug/issue context | **report** (default) |

If ambiguous, ask ONE question: "Are you reporting a bug/issue (report) or proposing a skill improvement (update)?"

---

## Report Mode

Use when a bug, unexpected behavior, or improvement need surfaces mid-session. Goal: capture context in under 2 minutes and return to the original work.

### Step 1: Gather context from the session

You were THERE when this happened. Pull from conversation history -- do NOT interrogate the user with a questionnaire. Extract:

1. **What we were doing** -- task, goal
2. **What happened** -- the specific failure or unexpected behavior
3. **What was attempted** -- workarounds, partial fixes, things tried
4. **The interaction** -- what the human said/did that triggered or revealed it
5. **Evidence** -- logs, outputs, error messages. Raw data.
6. **Root cause hypothesis** -- your best understanding of WHY
7. **Affected systems** -- file paths, modules, tools
8. **Acceptance criteria** -- how to verify a fix works

If the affected system is a skill, add a **Developer Brief** section: what should change in the skill, test cases, expected behavior, edge cases. This section feeds the developer who picks up the request.

### Step 1.5: Multi-System Detection

Check the Affected Systems from Step 1. If they span 2+ independent directories, create SEPARATE requests for each system instead of one combined request.

**Split signals:**
- Systems include both a "producer" (engine, generator, builder) and a "consumer" (validator, auditor, checker)
- Issue mentions two independent modules that happen to share a symptom
- User explicitly says "for both", "dual issue", or names two skills

**When splitting:**
- Each request gets its own slug, own `system:` field, own Acceptance Criteria scoped to that system
- Each request references the other via `## Related Requests` section
- Both share the same Context and Evidence sections (copy, don't summarize)
- Report all created docs in the confirmation output

**When NOT splitting:** If all systems are within one skill directory (e.g., SKILL.md + its implementation), keep as single request.

### Step 2: Write the handoff document

Read the template from `references/handoff-template.md` (included in this skill family) and write the document to:

```
requests/active/YYYY-MM-DD-{slug}.md
```

Generate the slug from the issue description (kebab-case, max 60 chars). Fill every section from session context. Set `status: open` in frontmatter.

### Step 3: Confirm and return

```
Request captured:
  Doc: requests/active/{filename}
  Severity: {level}

Returning to original work.
```

Do NOT start fixing the issue. Context capture, not context switch.

---

## Update Mode

Use when a skill or module needs intentional improvement -- not a bug, but a feature addition, refactor, or enhancement.

### Step 1: Write handoff document

Same as Report Mode Step 2, but framed as an improvement. The **Developer Brief** section is mandatory in update mode (since it always involves a skill).

### Step 2: Confirm

Report what was created: the handoff doc path.

```
Skill update captured:
  Doc: requests/active/{filename}

Returning to original work.
```

---

## Project Mode

Use when the scope exceeds a single request -- a new project is needed. This mode captures the vision and writes a handoff doc for project bootstrapping.

### Step 1: Capture the vision

Extract from the conversation:
- Why a new project is needed (not just a single fix)
- What it would contain (scope)
- What problems it solves
- Connection to other open requests

### Step 2: Write project handoff

Write to `requests/active/YYYY-MM-DD-{slug}.md` with `type: project` in frontmatter.

### Step 3: Confirm

```
Project request captured:
  Doc: requests/active/{filename}
  Next step: Open a fresh session and bootstrap the project with this doc.

No issues created.
```

---

## Rules

- **Never fix the issue.** Capture context, create tracking, return to work.
- **Never interrogate with questionnaires.** You have the session context -- use it.
- **Write to `requests/active/`.** This is the ONE canonical location for active requests. Resolved requests go to `requests/history/`. No other locations.
- **Keep report mode under 2 minutes.** Dump context quickly, don't over-analyze.
