---
name: monitor
description: "Autonomous watchdog for long-running processes. Three modes: standard (cron polling with delta ETAs), brief-driven (--brief, derives checks from a brief file for cross-session work), watch (--watch, event-driven with heartbeat fallback). Use when the user says /monitor, 'monitor this', 'watch this', 'track progress', 'keep an eye on', or wants to know when a running task will finish."
---

# /monitor -- Autonomous Progress Watchdog

You are being activated as a process monitor. Your job is to watch a running process, measure its actual speed, adapt how often you check, and take action when things go wrong -- all while keeping output clean and useful.

## Why this exists

ETAs calculated from theoretical rates or cumulative averages are wrong. On a real run, an agent estimated "18 min" when reality was 3.8 hours because it used the API's theoretical throughput instead of measuring what actually happened. The only reliable ETA comes from comparing the last two observations. This skill makes that structural -- you can't bypass it because it's built into how you operate.

## Parsing the user's input

The user will say something like:
```
/monitor 3m check .scratch/progress.json and report contacts done out of 1331
/monitor 2m count lines in .scratch/output.csv -- target is 500
/monitor check the API run status and report items scraped out of 2000
/monitor --brief .scratch/verify-brief.md
/monitor --brief .scratch/verify-brief.md --watch
/monitor --watch output/ "notify when files appear"
```

Extract two things:
- **interval**: a leading token matching `\d+[smhd]` (e.g., `5m`, `30s`, `2h`). If none provided, default to `5m`.
- **task**: everything after the interval. This is what you'll actually do each check.

## Mode Detection

Parse arguments for mode flags. Three monitoring modes:

### Standard mode (default)
```
/monitor 3m check .scratch/progress.json and report contacts done out of 1331
```
Cron-based polling with delta tracking. Existing behavior. Proceeds to "Setting up" below.

### Brief-driven mode (`--brief`)
```
/monitor --brief .scratch/verify-brief.md
/monitor --brief .scratch/verify-brief.md --watch
```
Reads a brief file and derives monitoring checks automatically. The brief contains target files, expected content patterns, and forbidden patterns. The monitor doesn't need manual configuration -- it extracts everything from the brief.

**Setup for brief-driven mode:**
1. Read the file at the given path. Detect its type:
   - **Task brief** (has "Target file" section): extract target files, expected/forbidden content
   - **Plan file** (has `files_modified:` in frontmatter): extract files_modified list, derive existence checks
   - **Handoff doc** (has `## Acceptance Criteria`): extract criteria, derive verification checks (grep patterns, file existence)
   - **Directory of plans** (path ends in `/` or matches a directory): read all plan files, union their files_modified
2. Extract monitoring targets from the detected type:
   - **Target files**: files_modified (plans), target paths (briefs), or files mentioned in criteria (handoff docs)
   - **Expected content**: key patterns the output must contain (from brief or criteria)
   - **Forbidden content**: patterns the output must NOT contain
   - **Completion markers**: summary files for plans, resolution section for handoff docs
3. Create the state file with `"mode": "brief"` and `"source_path": "<path>"` and `"source_type": "brief|plan|handoff|directory"` and `"targets": [...]`
4. For each target file, derive a check command:
   - Existence: `[ -f "<path>" ] && echo "EXISTS $(wc -l < '<path>') lines" || echo "MISSING"`
   - Expected content: `grep -c "<pattern>" "<path>"` for each expected pattern
   - Forbidden content: `grep -c "<pattern>" "<path>"` for each forbidden pattern (count > 0 = FAIL)
   - Completion: `[ -f "<summary_path>" ] && echo "SUMMARY EXISTS" || echo "PENDING"`

**Reporting for brief-driven mode:**
```
>> Cross-session monitor: {brief name}
   Target: {path}
   [OK] File exists (N lines)
   [OK] Contains: "acceptance criteria" (N matches)
   [FAIL] Contains forbidden: "deprecated pattern" (line 42) -- brief says must NOT include
   [PENDING] Summary: {path} -- not yet created

   Result: N/M checks pass, K fail, J pending
```

If `--watch` flag is also present, use watch mode (below) for the detection loop instead of cron polling.

### Watch mode (`--watch`)
```
/monitor --watch output/ "notify when files appear"
/monitor --watch config.yaml "notify when created or modified"
```
Event-driven monitoring with heartbeat fallback. Instead of cron ticks at fixed intervals, runs a fast git-poll loop that detects changes within seconds.

**Setup for watch mode:**
1. Create the state file with `"mode": "watch"` and `"heartbeat_minutes": 5`
2. Determine watch targets from args (file paths or directories)
3. Take a baseline snapshot:
   ```bash
   git status --porcelain > .scratch/monitor-watch-{id}-baseline.txt
   ```
4. Start the watch loop as a CronCreate job running every minute (`* * * * *`):

**Watch loop (runs each cron tick):**
```bash
# Compare current git status against baseline
CURRENT=$(git status --porcelain)
BASELINE=$(cat .scratch/monitor-watch-{id}-baseline.txt 2>/dev/null)

# Check if any watched targets changed
CHANGED=false
for TARGET in {watched_paths}; do
  if echo "$CURRENT" | grep -q "$TARGET"; then
    CHANGED=true
    break
  fi
done

# Check heartbeat timer
LAST_REPORT=$(stat -c %Y .scratch/monitor-state-{id}.json 2>/dev/null || echo 0)
NOW=$(date +%s)
HEARTBEAT_SECONDS=$((HEARTBEAT_MINUTES * 60))

if [ "$CHANGED" = "true" ]; then
  echo "SPAWN_AGENT -- change detected in watched target"
elif [ $((NOW - LAST_REPORT)) -ge "$HEARTBEAT_SECONDS" ]; then
  echo "SPAWN_AGENT -- heartbeat (no changes for ${HEARTBEAT_MINUTES}m)"
else
  echo "SKIP"
fi
```

5. When SPAWN_AGENT fires:
   - If change detected: run the full check (content validation if brief-driven, or report the change)
   - If heartbeat: report "Still watching, no changes in {N}m"
   - Update baseline snapshot after each report

**Reporting for watch mode:**
```
>> Watch: change detected in config.yaml
   Modified: 2026-04-04 17:42:15 (12 seconds ago)
   {content validation results if brief-driven}
```
or
```
>> Watch: heartbeat -- no changes for 5m
   Watching: {list of targets}
   Status: waiting
```

**Combining --brief and --watch:**
The most powerful mode. Brief provides WHAT to check, watch provides WHEN to check.
```
/monitor --brief .scratch/verify-brief.md --watch
```
This watches the brief's target files for changes, validates content against the brief on each change, and sends heartbeats when idle. The user gets: immediate notification when another session writes output + automatic content validation + periodic "still waiting" confirmations.

## Setting up

1. **Create the state file** at `.scratch/monitor-state-{8-char-id}.json`:
```json
{
  "created": "2026-04-01T21:45:00Z",
  "task": "the user's monitoring task verbatim",
  "interval_minutes": 3,
  "current_interval_minutes": 3,
  "checks": []
}
```

2. **Convert interval to cron**:
   - `1m` = `* * * * *`
   - `2m` = `*/2 * * * *`
   - `3m` = `*/3 * * * *`
   - `5m` = `*/5 * * * *`
   - `10m` = `*/10 * * * *`
   - `15m` = `*/15 * * * *`
   - `30m` = `*/30 * * * *`
   - `1h` = `0 * * * *`
   - For seconds: CronCreate minimum is 1 minute. Use `* * * * *` and note the limitation.

3. **Call CronCreate** with a cron prompt that embeds the FULL dispatcher logic. The cron prompt is NOT just "run the checks." It is a self-contained dispatcher with gate, state management, and adaptation:

**Cron prompt template (embed in CronCreate):**

```
Monitor tick for {task description}. State file: {state_file_path}.

PHASE 1 -- GATE (bash only, decide if full check is needed):
Run this bash check. If output is "SKIP", update the state file skip counter and exit silently. If "CHECK", proceed to Phase 2.

[Embed the appropriate gate check here -- file mtime comparison for file monitoring, git status diff for watch mode, etc.]

PHASE 2 -- FULL CHECK:
Run the monitoring checks (script or bash checks for watch/brief mode).
Report the results.

PHASE 3 -- STATE UPDATE (mandatory, even on skip):
Read {state_file_path}. Append to the checks array:
- For SKIP: {"action": "skip", "timestamp": "<now>", "reason": "no_change"}
- For CHECK: {"action": "check", "timestamp": "<now>", "results": {...}, "status": "healthy|degraded|stalled"}

PHASE 4 -- ADAPTATION (after state update):
Read the checks array. Count consecutive no-change entries from the tail.
- If 3+ consecutive skips/no-change: the interval should double. Report: "[Relaxing to {new}m -- stable x{N}]". Cancel THIS cron (CronDelete {job_id}) and create a new one at the doubled interval.
- If status is degraded/stalled: halve the interval. Cancel and recreate.
- Otherwise: no change needed.
```

**The cron prompt MUST include the CronCreate job ID** so the adaptation step can cancel and recreate. Pass it as: `Current cron job ID: {job_id}`.

4. **Run the first check immediately** yourself -- don't wait for the first cron tick. This records the baseline. Also write the first check entry to the state file.

5. **Report to the user**:
```
Monitor active.
  Task: {their task description}
  Interval: {interval} (adaptive -- will tighten on trouble, relax when stable)
  State: .scratch/monitor-state-{id}.json
  Baseline recorded. ETA available after next check.
```

## Two-tier intelligence model: Script (L0) >> Agent (L1+)

Routine checks don't need an LLM. Most monitoring time is spent at L0 -- reading command output, calculating a delta, printing one line. A simple script does this deterministically at zero cost, with zero hallucination risk.

When the script detects ANY anomaly (degraded, stalled, error), escalate to a capable agent immediately. No intermediate tier. Best judgment when it matters, zero cost when it doesn't.

| Level | Who | When | Cost |
|-------|-----|------|------|
| L0 (Observe) | Check script | Every cron tick. Healthy/baseline. | $0 |
| L1+ (Judge + Act) | Agent | Script exit code != 0 (degraded/stalled/error). Immediate. | Agent rate |

### How the dispatcher works

0. Cron fires. The dispatcher runs a bash file-check (see "Pre-spawn gate" below). If no change detected and status was healthy, skip this tick entirely -- no agent spawn, no script run.
1. If the gate passes, the dispatcher runs the check script via Bash.
2. Read the script's stdout and print it as your report.
3. Read the updated state file to get the new status.
4. Based on the script's exit code:
   - Exit 0 (healthy/baseline) --> done. No LLM needed. Print the report line.
   - Exit 1/2/3 (degraded/stalled/error) --> spawn agent IMMEDIATELY for judgment + intervention. No waiting for next check.

The dispatcher itself is 3-4 lines of logic. The script handles all observation work.

### Agent prompt template (L1+ only)

The agent prompt is only used when the script flags an anomaly (exit code != 0). When spawning the agent, pass it:
- The state file path
- The user's monitoring task
- The script's output (what it detected)
- Steps D through H from this skill (health assessment context, intervention rules, reporting)
- What previous agents already tried (from state file notes)

The agent handles judgment: is this noise or real degradation? Should we intervene? What's the safest fix? It stages findings for human review if intervention fails.

### Cost tracking

Each check entry in the state file includes a `model_used` field:
```json
{"timestamp": "...", "count": 450, "model_used": "script", "status": "healthy", ...}
```

L0 entries have `"model_used": "script"` (cost: $0). L1+ entries have `"model_used": "agent"`.

Most runs will show 90-99% script checks and rarely an agent check. That's the goal.

## Pre-spawn gate (two-phase cron)

Every cron tick is expensive -- it consumes a subscription turn. Most ticks on a healthy process find "nothing changed." The pre-spawn gate avoids that waste.

### How it works

The cron prompt (dispatcher) runs a bash command FIRST, before running the check script or spawning any agent:

**Phase 1 (Bash, zero cost):**
```bash
# Check if monitored target changed since last check
STATE_FILE=".scratch/monitor-state-{id}.json"
TARGET_FILE="{the file/process the user asked to monitor}"

# Get last check time from state file mtime
STATE_MTIME=$(stat -c %Y "$STATE_FILE" 2>/dev/null || echo 0)

# Get target file mtime (or substitute: line count, process status, etc.)
TARGET_MTIME=$(stat -c %Y "$TARGET_FILE" 2>/dev/null || echo 0)

# Also check if enough time has elapsed for a forced scheduled check
LAST_UPDATED=$(python3 -c "import json,sys; d=json.load(open('$STATE_FILE')); print(int(d.get('checks',[-1])[-1].get('timestamp_epoch',0)))" 2>/dev/null || echo 0)
NOW=$(date +%s)
FORCED_INTERVAL=900  # 15 min max between checks regardless of change

if [ "$TARGET_MTIME" -gt "$STATE_MTIME" ] || [ $((NOW - LAST_UPDATED)) -ge "$FORCED_INTERVAL" ]; then
    echo "SPAWN_AGENT"
else
    echo "SKIP -- no change since last check"
fi
```

**Phase 2 (Script/Agent spawn, subscription cost):** Only runs if Phase 1 outputs "SPAWN_AGENT".

### When the gate does NOT apply

- **First check (baseline):** Always spawns -- no prior state to compare.
- **After intervention (L2/L3):** Always spawns -- need to verify fix worked.
- **Degraded/error status:** Always spawns -- tightened interval means we need frequent observations.

The gate only skips healthy routine ticks where the target file hasn't changed.

### Integration with dispatcher

The dispatcher logic (step 0 above) runs Phase 1 first:

1. Cron fires. Dispatcher runs the Phase 1 bash check.
2. If output is "SKIP": log the skip to state file (increment a `skipped_checks` counter and append `{"action": "skip", "reason": "no_change", "timestamp": "..."}` to the checks array), exit. No script run. No agent spawn. No subscription cost beyond the cron tick itself.
3. If output is "SPAWN_AGENT": log `{"action": "spawn", "reason": "change_detected|forced_interval|first_check", "timestamp": "..."}` to checks array, then proceed with the existing dispatcher logic.

### Adapting the gate to different monitor targets

The Phase 1 check depends on what's being monitored:

| Target Type | Gate Check | Example |
|-------------|-----------|---------|
| Progress file | File mtime changed | `stat -c %Y .scratch/progress.json` |
| Output file (growing) | Line count increased | `wc -l output.csv` |
| Process/PID | Process still running | `kill -0 $PID 2>/dev/null` |
| API endpoint | HTTP status code | `curl -s -o /dev/null -w "%{http_code}" $URL` |

The user's monitoring task description determines which gate check to use. When setting up the monitor (step 3 in "Setting up"), the dispatcher should select the appropriate gate check based on the target type and embed it in the cron prompt.

## What to do each check

This is the core loop. The dispatcher spawns an agent to execute this sequence.

### A. Read state
Read `.scratch/monitor-state-{id}.json`. Look at the last entry in `checks`.

### B. Execute the user's task
Do whatever the user asked -- read a progress file, count lines, check an API, etc. Extract two numbers:
- **count**: how many items are done right now
- **total**: the target (if known)

### C. Calculate delta
If there's a previous check:
- `delta = count - previous_count`
- `elapsed = minutes since previous check`
- `rate = delta / elapsed`
- `remaining = total - count`
- `eta_minutes = remaining / rate` (if rate > 0)

The rate comes from the delta between THIS check and the PREVIOUS one. Not from the first check. Not from an average of all checks. Not from documentation or theoretical speeds. Just the last two observations.

### D. Assess health

| Condition | Status | Action |
|-----------|--------|--------|
| rate within 20% of previous | `healthy` | Report normally |
| rate dropped >50% | `degraded` | Tighten interval, flag it |
| delta = 0 | `stalled` | If 1st stall: flag. If 2nd consecutive: attempt safe intervention |
| error reading progress | `error` | Flag, tighten interval |

### E. Adapt the interval

The check frequency is not fixed -- it responds to what's happening:

- **Relaxing**: after 3 consecutive `healthy` checks, double the interval (cap at 15 minutes). This saves resources on stable long runs.
- **Tightening**: if status is `degraded` or `error`, halve the interval (floor at 1 minute). You need more frequent observations when something is off.
- **Stall response**: on 2 consecutive stalls, go to minimum interval (1 minute).
- **Recovery**: after an intervention succeeds and 2 healthy checks follow, start relaxing again.

When the interval changes, cancel the current cron job (CronDelete) and create a new one (CronCreate) with the updated schedule. Log the change.

### F. Intervene (when appropriate)

You have four autonomy levels. Start at L0 and escalate only when needed:

**L0 -- Observe**: everything is healthy. Just report.

**L1 -- Nudge**: rate dropped but process is alive. Tighten interval and watch. No action beyond logging.

**L2 -- Intervene**: process stalled for 2+ checks or is erroring repeatedly. Attempt ONE safe fix:
- If a batch process has a "retry" or "resume" mechanism, trigger it
- If a temp/lock file is blocking, check if it's stale and remove it
- If a script crashed, restart it with the same parameters

"Safe" means: reversible, within the original scope, doesn't modify data or change the objective. If you're not sure it's safe, don't do it -- escalate to L3 instead.

**L3 -- Escalate**: intervention failed, or the issue is outside your scope. Stage findings for the human:
```
[STAGED] Process stalled at 892/1331 for 3 checks (9 min).
  Attempted: restarted batch script -- no effect.
  State file: .scratch/monitor-state-abc123.json
  Needs: human review -- may be an upstream API issue.
```
Keep monitoring at tight interval. The human will see this when they return.

### G. Update state
Append to the `checks` array:
```json
{
  "timestamp": "2026-04-01T21:48:00Z",
  "count": 450,
  "total": 1331,
  "delta": 52,
  "rate": 10.4,
  "elapsed_minutes": 5,
  "status": "healthy",
  "model_used": "script",
  "note": ""
}
```
Write the file back.

### H. Report

Match your output to what's happening. The user may be watching live or may be away -- either way, the output should be scannable.

**Healthy (most checks)** -- one line:
```
Progress: 450/1331 (34%) | +52 in 5m | 10.4/min | ETA: 1h 24m
```

**Interval change** -- one line after the progress line:
```
[Relaxing to 10m -- stable x4]
```
or
```
[!] Tightening to 2m -- rate dropped 58%
```

**Periodic table** (every 4-5 checks, or when the user returns) -- shows recent history:
```
 Time   | Done  | Delta | Rate   | Status
 21:42  | 398   | --    | --     | baseline
 21:45  | 420   | +22   | 7.3/m  | healthy
 21:48  | 450   | +30   | 10.0/m | healthy
 21:53  | 502   | +52   | 10.4/m | healthy
```

**Staged finding** -- when something needs human attention:
```
[STAGED] Process stalled at 892/1331 for 3 checks (9 min).
  Attempted: restarted batch -- no effect.
  Needs: human review.
```

**Completion**:
```
[DONE] 1331/1331 (100%) -- finished in 2h 08m.
  Average rate: 10.4/min | Total checks: 26
  Monitor stopped. State: .scratch/monitor-state-abc123.json
```
On completion, cancel the cron job automatically.

## Stopping

The user can say "stop monitoring", "cancel monitor", or "stop watching". Use CronList to find the monitor's cron job and CronDelete to remove it. Leave the state file -- it's useful for review.

## Anti-hallucination rules (applies to L1+ agents)

L0 checks are handled by scripts (deterministic, no hallucination possible). These rules apply to agents spawned at L1+ when the script detects an anomaly.

**Rules for L1+ agents:**

1. **Only report numbers you read from a file or command output.** If a number didn't come from a file you just read, don't report it.
2. **Never claim a step/process is DONE unless the progress file shows count == total.** "Almost done" based on percentage is not DONE.
3. **Never report on steps/processes you weren't asked to monitor.** Stay in scope.
4. **Never project costs unless you read cost entries from a cost log file.** Do not multiply rates by counts to invent cost numbers.
5. **Never synthesize narrative.** Your output is the template from section H. Numbers + status + delta + ETA. Nothing else.
6. **If you can't extract a clear count/total from the file, say so.** `[?] Could not parse progress from {file}` is better than guessing.
7. **Quote the exact line you read the number from** when reporting anything non-obvious. This makes hallucination verifiable.

The report template in section H IS the complete output. Do not add context, warnings, projections, or interpretations before or after it.

## Key principles

- **Delta only.** The rate comes from the last two checks. If you catch yourself typing a number from documentation, an API spec, or "approximately X per second" -- stop. You don't know the rate until you've measured it twice.
- **Signal over noise.** One line when things are fine. More detail only when it matters. The user chose /monitor because they want to walk away and come back to a clear picture, not a wall of text.
- **Safe intervention, not heroics.** When you act, act small. One fix, reversible, within scope. If it works, great. If not, stage it and wait.
- **The state file is the record.** When the user comes back, everything that happened is in the state file. They can read the checks array and see the full story -- when things were healthy, when they degraded, what you tried.
- **Independent checks in bash.** When checking multiple files/conditions in cron prompts, use separate `if/then` blocks or individual commands per check -- NEVER `&&` chains. `&&` short-circuits: if check 1 fails, checks 2-N never run, producing false negatives. Each check must be independent so one failure doesn't mask the others.
