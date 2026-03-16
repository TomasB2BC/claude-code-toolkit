---
name: research
description: Research any topic using parallel investigator agents with multi-perspective debate. Use when you need to understand a topic deeply before making decisions or writing code.
argument-hint: <topic or question>
---

# Research Workflow

Research any topic by spawning parallel investigator agents that approach the question from different angles, then synthesize their findings into a single actionable document.

## Input

Topic or question provided: `$ARGUMENTS`

If no arguments: respond with "Usage: /research <topic or question>"

## Step 1: Classify the Topic

Determine the topic type to guide research strategy:

| Signal | Type |
|--------|------|
| References project files, architecture, internal tools | `codebase` |
| References external technologies, markets, industry topics | `external` |
| Mix of internal and external (e.g., "should we add X library") | `mixed` |

## Step 2: Set Up Output

Create an output directory for the research:

```bash
# Create a slug from the topic (lowercase, hyphens, max 50 chars)
SLUG=$(echo "$ARGUMENTS" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | cut -c1-50)
RESEARCH_DIR=".scratch/research/${SLUG}"
mkdir -p "$RESEARCH_DIR"
```

Check if prior research exists:
```bash
ls "${RESEARCH_DIR}/RESEARCH.md" 2>/dev/null
```

If it exists, ask the user: re-research, view existing, or cancel.

## Step 3: Gather Project Context

Collect relevant context to orient the researchers:

```bash
# Grab project-level context if available
PROJECT_CONTEXT=""
[ -f "CLAUDE.md" ] && PROJECT_CONTEXT=$(head -50 CLAUDE.md)
[ -f ".planning/STATE.md" ] && PROJECT_CONTEXT="$PROJECT_CONTEXT\n$(head -30 .planning/STATE.md)"
```

## Step 4: Spawn Research Agents

Spawn 3 parallel Task agents, each with a distinct perspective:

### Agent 1: Optimist (Primary Researcher)

Owns the final RESEARCH.md. Focuses on established patterns, practical approaches, what works well.

```
Task(
  prompt="You are a research agent with an optimist perspective.

Topic: {TOPIC}
Topic type: {TOPIC_TYPE}
Project context: {PROJECT_CONTEXT}

Research this topic thoroughly using WebSearch and WebFetch.
Focus on: established patterns, proven approaches, practical solutions.

Write your findings to: {RESEARCH_DIR}/RESEARCH.md

Use this structure:
# {TOPIC} -- Research

**Researched:** {date}
**Confidence:** HIGH/MEDIUM/LOW

## Summary
[2-3 paragraph overview with key findings]

## Key Findings
[Structured findings with tables, data, comparisons]

## Recommended Approach
[Specific, actionable recommendations]

## Common Pitfalls
[What to watch out for]

## Open Questions
[What needs further investigation]

## Sources
### Primary (HIGH confidence)
- [Source with URL]
### Secondary (MEDIUM confidence)
- [Source with URL]

After writing your draft, wait for challenge messages from the other researchers.
Then add a 'Dissenting Views / Risks & Alternatives' section incorporating their perspectives.",
  description="Research (optimist): {TOPIC}"
)
```

### Agent 2: Devil's Advocate

Challenges assumptions, finds risks, edge cases, reasons things might fail.

```
Task(
  prompt="You are a research agent with a devil's advocate perspective.

Topic: {TOPIC}
Topic type: {TOPIC_TYPE}
Project context: {PROJECT_CONTEXT}

Research this topic with a critical eye using WebSearch and WebFetch.
Focus on: risks, challenges, edge cases, why approaches might fail, hidden costs.

Write your critical analysis to: {RESEARCH_DIR}/advocate-notes.md

After drafting, read the optimist's RESEARCH.md and send 2-3 specific challenges
to the optimist agent. Each challenge should be evidence-based (not just skepticism).",
  description="Research (devil's advocate): {TOPIC}"
)
```

### Agent 3: Explorer

Finds unconventional approaches, alternative solutions, innovations.

```
Task(
  prompt="You are a research agent with an explorer perspective.

Topic: {TOPIC}
Topic type: {TOPIC_TYPE}
Project context: {PROJECT_CONTEXT}

Research this topic looking for unconventional angles using WebSearch and WebFetch.
Focus on: alternative approaches, novel patterns, what others haven't tried.

Write your exploration to: {RESEARCH_DIR}/explorer-notes.md

After drafting, read the optimist's RESEARCH.md and send 2-3 alternative perspectives
to the optimist agent.",
  description="Research (explorer): {TOPIC}"
)
```

## Step 5: Wait and Synthesize

After all 3 agents complete:

1. Verify `RESEARCH.md` exists and includes the "Dissenting Views" section
2. Clean up temporary notes:
   ```bash
   rm "${RESEARCH_DIR}/advocate-notes.md" 2>/dev/null
   rm "${RESEARCH_DIR}/explorer-notes.md" 2>/dev/null
   ```

## Step 6: Present Results

```
>> Research complete: {RESEARCH_DIR}/RESEARCH.md

Options:
- Review the full document
- Use findings to inform a decision
- Research a follow-up topic: /research <follow-up>
```

## Fallback: Single-Agent Research

If Task agents are not available (e.g., running in a constrained environment), fall back to single-agent research:

1. Research the topic yourself using WebSearch and WebFetch
2. Write RESEARCH.md directly with all sections
3. Self-challenge: after drafting, re-read with a critical eye and add the "Dissenting Views" section

## Quality Requirements

Every RESEARCH.md must have:
- Confidence levels (HIGH/MEDIUM/LOW) with reasoning
- Source citations with URLs where available
- Honest reporting of gaps and uncertainty
- Actionable recommendations (not just information dumps)
- A "Dissenting Views" section (even in single-agent mode)
