# /monitor -- Autonomous Progress Watchdog

Watch long-running processes with adaptive polling, real-time ETAs, and automatic intervention when things stall.

## What It Does

Monitors any long-running process (file growth, API runs, batch jobs) with three modes:

| Mode | Trigger | Best For |
|------|---------|----------|
| **Standard** | `/monitor 3m check progress.json` | Watching a batch process with known targets |
| **Brief-driven** | `/monitor --brief verify-brief.md` | Cross-session work validation (another session builds, this one watches) |
| **Watch** | `/monitor --watch output/` | Event-driven: notify immediately when files change |

Key features:
- **Delta-based ETAs** -- rates come from comparing the last two observations, never from theoretical speeds
- **Adaptive frequency** -- relaxes when stable (saves resources), tightens when degraded (catches problems fast)
- **Two-tier intelligence** -- cheap script checks handle 90%+ of ticks, agent escalation only on anomalies
- **Safe intervention** -- on stalls, attempts one reversible fix before escalating to human
- **Pre-spawn gate** -- skips cron ticks when nothing changed, saving subscription turns

## When to Use It

- Running a batch job that takes 30+ minutes and you want to walk away
- Cross-session monitoring: one session builds, another watches for completion
- Watching for file changes in a directory (event-driven, not polling)
- Any time you want to know "when will this finish?" with a real answer

## Example Usage

```
# Watch a progress file, check every 3 minutes
/monitor 3m check .scratch/progress.json and report items done out of 1000

# Count lines in a growing CSV
/monitor 2m count lines in .scratch/output.csv -- target is 500

# Cross-session: watch for work completion using a brief
/monitor --brief .scratch/verify-brief.md --watch

# Event-driven: notify when files appear in a directory
/monitor --watch output/ "notify when results appear"

# Default interval (5m), custom task
/monitor check the API endpoint at localhost:8080/health
```

## How It Works

1. **Parses your input** -- extracts interval and task description
2. **Records a baseline** -- runs the first check immediately
3. **Creates a cron job** -- fires at the specified interval with a pre-spawn gate
4. **Each tick**: gate check (bash, free) --> script check (L0, free) --> agent escalation (L1+, only on anomaly)
5. **Adapts**: 3 healthy checks = double interval. Degraded/stalled = halve interval.
6. **Intervenes**: on 2 consecutive stalls, attempts one safe fix. If it fails, stages findings for human review.
7. **Completes**: cancels the cron job when target is reached

## Autonomy Levels

| Level | When | What Happens |
|-------|------|--------------|
| L0 -- Observe | Healthy | Script reports one line. No agent needed. |
| L1 -- Nudge | Rate dropped | Tightens interval, flags it. No action. |
| L2 -- Intervene | 2+ stalls | Attempts ONE safe, reversible fix (retry, clear stale lock, restart script). |
| L3 -- Escalate | Intervention failed | Stages findings for human review. Keeps monitoring. |

## Output Format

```
Progress: 450/1331 (34%) | +52 in 5m | 10.4/min | ETA: 1h 24m
```

When something needs attention:
```
[STAGED] Process stalled at 892/1331 for 3 checks (9 min).
  Attempted: restarted batch -- no effect.
  Needs: human review.
```

## Install

**Option A: Script**
```bash
python install.py monitor-watchdog
```

**Option B: Manual**
Copy `monitoring/monitor-watchdog/` to `.claude/skills/monitor-watchdog/`

## Requirements

- Claude Code with CronCreate/CronDelete support
- Python 3.10+ (for check scripts)
- Git (for watch mode baseline snapshots)
