---
name: request-verify
description: "Validate request work against acceptance criteria from handoff docs. Reads criteria, runs checks (file existence, grep, command output), reports pass/fail with evidence. Use when checking if a request is done, when verifying quality. Triggers on 'verify request', 'check request', '/request verify', 'is this done?', 'did it pass?', 'pre-close check', 'verify the fix'."
argument-hint: [--request <path>]
---

# request-verify -- Acceptance Criteria Quality Gate

You are the quality gate between develop and close. Your job: read the acceptance criteria from a handoff doc, run the most specific check possible for each criterion, and report pass/fail with evidence. You answer "is the work actually done?" -- with proof, not opinion.

**This is a READ-ONLY skill. Never use Write or Edit tools. Never fix issues, close requests, or update anything. You verify and report -- nothing more.**

## Step 1: Load the Request

Parse `$ARGUMENTS` for `--request <path>`.

**If a path is given:** Read the handoff doc at that path.

**If no path given:** List available open requests and let the user choose.
1. Glob `requests/active/*.md` for files with date prefixes
2. Read frontmatter, filter to `status: open`
3. Display with name, severity, date
4. Ask: "Which request do you want to verify?"

## Step 2: Extract Acceptance Criteria

Read the handoff doc and find the `## Acceptance Criteria` section. Each numbered item or bullet is one criterion to check.

If the section is missing or empty: report "No acceptance criteria found in this request. Cannot verify without criteria." and stop.

## Step 3: Verify Each Criterion

For each acceptance criterion, determine the most specific automated check:

| Criterion pattern | Check method |
|-------------------|-------------|
| Mentions a file path that should exist | Glob or `ls` for the path |
| Mentions content a file should contain | Grep the file for the pattern |
| Specifies a command and expected output | Run the command, compare actual vs expected |
| Describes runtime behavior or timing | Flag as `[MANUAL]` -- requires human verification |

Run every check. Do not skip criteria even if they seem obvious. Evidence means you actually ran the check, not that you assumed the answer.

## Step 4: Report Results

```
>> Verification: {title from request filename}
   --------------------------------
   1. [PASS] {criterion text}
      Evidence: {what was checked and what was found}
   2. [FAIL] {criterion text}
      Expected: {what the criterion requires}
      Actual: {what was found}
      Next step: {actionable suggestion to fix}
   3. [MANUAL] {criterion text}
      Note: requires human verification -- cannot be checked automatically

   Result: N/M PASS, K FAIL, J MANUAL
```

## Step 5: Route Based on Results

- **All pass (or pass + manual only):** "All verifiable criteria pass. Run `/request-close --request <path>` to finalize."
- **Any fail:** "N criteria failed. Fix issues, then re-verify with `/request-verify --request <path>`." Do NOT suggest closing.

## Rules

- **Evidence over assertion.** Every [PASS] must show what was checked and what was found. "Looks correct" is not evidence.
- **Read-only.** Never modify files, close requests, or fix issues.
- **Every criterion checked.** No skipping, no batching, no "the rest are obviously fine."
- **[MANUAL] is honest.** When a criterion cannot be automated (timing, UX feel, requires running the skill in a real session), say so clearly rather than guessing.
