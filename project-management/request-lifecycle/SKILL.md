---
name: request
description: "Skill lifecycle harness hub. Shows open requests, routes to sub-skills (request-capture, request-develop, request-audit, request-verify, request-close). Use as the entry point for all skill lifecycle work. Triggers on 'request', 'skill request', 'skill status', 'what needs work', '/request'."
argument-hint: [status]
---

# Request Skill Family -- Hub

You are the hub for the request skill family -- the skill lifecycle harness. Your job: show what's open and route to the right sub-skill.

This is a READ-ONLY command. You read state and display it. You never write files, create issues, or modify anything.

## Legacy Mode Routing

If $ARGUMENTS matches a v2 mode name, redirect to the corresponding sub-skill:

| v2 Invocation | Redirect To | Message |
|---------------|-------------|---------|
| `report ...` | request-capture | "Report mode moved to `/request-capture`. Invoking it now..." |
| `update ...` | request-capture | "Update mode moved to `/request-capture --skill <name>`. Invoking it now..." |
| `develop ...` or `dev ...` | request-develop | "Dev mode moved to `/request-develop`. Invoking it now..." |
| `verify ...` | request-verify | "Verify mode moved to `/request-verify`. Invoking it now..." |

When redirecting: tell the user the new command, then show the dashboard. Do NOT attempt to execute the sub-skill's logic from the hub.

## Step 1: Read Pipeline State

1. Glob `requests/active/*.md` -- count open requests, parse frontmatter for name, severity, and title from each file.
2. Glob `requests/history/*.md` -- count resolved requests (check dates for recent activity in last 7 days).

## Step 2: Display Dashboard

```
>> Request Skill Family -- Status
   --------------------------------
   Open requests:    N
   Recently closed:  N (last 7 days)

   Open requests:
     - [severity] name: title (date)
     ...
```

If no open requests, display: `Open requests: 0 -- all clear.`

## Step 3: Route to Sub-Skills

```
>> Available commands:
   /request-capture    Capture a bug, improvement, or skill update
   /request-develop    Pick up and execute a captured request
   /request-audit      Test what was built, discover issues, feed the cycle
   /request-verify     Validate against acceptance criteria
   /request-close      Mark complete, update all tracking
```

## Step 4: Suggest Next Action

Based on pipeline state:
- If open requests exist: "Suggested: `/request-develop requests/active/{oldest}.md`"
- If no open requests: "No open requests. Use `/request-capture` to file new work."

## Note

Claude Code IS the best bug reporter when it encounters a problem mid-session. It has the full context -- what happened, what was attempted, what the human said. The request family captures that context and drives it to resolution through a cycle:

```
capture >> develop >> audit >> (issues? capture again : close)
```

The lifecycle is a loop, not a pipeline. Audit is the quality gate that either restarts the cycle or ends it.
