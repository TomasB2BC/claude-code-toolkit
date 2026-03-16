# /research -- Multi-Perspective Research Workflow

Research any topic using parallel investigator agents that debate and synthesize findings.

## What It Does

Instead of asking one AI to research something (single perspective, confirmation bias), this skill spawns 3 parallel agents with distinct roles:

| Agent | Role | Focus |
|-------|------|-------|
| Optimist | Primary researcher | What works, proven patterns, best practices |
| Devil's Advocate | Critical challenger | Risks, edge cases, hidden costs, why it might fail |
| Explorer | Alternative finder | Unconventional approaches, novel patterns, what others miss |

The optimist writes the main document. The other two challenge it. The final output incorporates all perspectives into one actionable RESEARCH.md.

## When to Use It

- Before choosing a technology or library
- Before designing a system architecture
- When exploring a market or domain you don't know well
- Before making any decision where being wrong is expensive
- When you catch yourself saying "just use X" without understanding tradeoffs

## Example Usage

```
/research WebSocket vs SSE for real-time updates
/research best practices for Supabase row-level security
/research Python packaging: uv vs pip vs poetry in 2026
```

## Output

Research documents are saved to `.scratch/research/<topic-slug>/RESEARCH.md` with:
- Executive summary
- Key findings with evidence
- Recommended approach
- Common pitfalls
- Dissenting views (from the challenger agents)
- Sources with confidence levels

## Install

**Option A: Script**
```bash
python install.py research-workflow
```

**Option B: Manual**
Copy the `prompt-engineering/research-workflow/` folder to `.claude/skills/research-workflow/`

## How It Works

The skill classifies your topic (codebase-internal, external, or mixed), gathers project context, then spawns 3 Task agents in parallel. Each researches independently, then they cross-review and challenge each other's findings. The final document includes a "Dissenting Views" section so you see the full picture, not just the optimistic case.

If parallel agents aren't available in your environment, it falls back to single-agent research with a self-challenge step.
