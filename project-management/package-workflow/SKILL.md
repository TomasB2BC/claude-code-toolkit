---
name: package
description: Shape any deliverable for its specific audience. Loads an audience profile, then formats the output so the reader gets exactly what they need -- no jargon they don't know, no details they don't care about, in the format they prefer.
argument-hint: <audience> [--type <deliverable-type>] [--topic "<topic>"]
---

# Package Workflow

Gather audience context and shape a deliverable for a specific reader. The same information packaged differently for a technical lead vs. a CEO vs. a new hire.

## Input

Arguments provided: `$ARGUMENTS`

## Step 1: Parse Arguments

Extract from `$ARGUMENTS`:

1. **Audience** (required): Who is reading this -- a person, role, or team name
2. **--type** (optional): Deliverable type -- brief, email, report, memo, presentation, etc.
3. **--topic** (optional): Subject matter in quotes

If no audience provided: respond with "Usage: /package <audience> [--type <type>] [--topic \"<topic>\"]"

## Step 2: Load Audience Profile

Search for an audience profile in order of priority:

1. `audience-profiles/<audience>.md` (project-level)
2. `.claude/audience-profiles/<audience>.md` (user-level)

**If found**, extract:
- Communication style (technical depth, jargon tolerance, preferred format)
- What they care about (metrics, outcomes, risks, timelines)
- What to avoid (unnecessary detail, certain terminology, assumptions)
- Decision authority (what they can approve, what they escalate)
- Preferred format (doc, email, Slack, bullet points, narrative)

**If not found**, build a lightweight profile from the audience name:

```markdown
## Inferred Profile: {audience}

Based on the role/name provided, assuming:
- Communication style: [infer from role -- engineer=technical, executive=outcomes-focused]
- Key interests: [infer from role]
- Format: [default to structured bullet points]

[!] This is an inferred profile. Create `audience-profiles/{audience}.md` for better results.
```

## Step 3: Gather Source Material

Based on --type and --topic, collect the raw material to package:

### For types that need project context:
```bash
# Recent work
git log --oneline -10 2>/dev/null

# Project state
cat README.md 2>/dev/null | head -50

# Relevant files (if --topic narrows the scope)
# Search for topic-related content in the project
```

### For types that need external context:
- Use WebSearch if the topic requires current information
- Read relevant project documents

### Source priority by deliverable type:

| Type | Primary Sources |
|------|----------------|
| brief | Project state, recent decisions, key metrics |
| email | Recent conversations, action items, tone from profile |
| report | Data, analysis, findings, recommendations |
| memo | Decision context, options, tradeoffs |
| presentation | Key points, visuals, narrative arc |
| meeting-prep | Recent context, open items, stakeholder priorities |

## Step 4: Shape the Deliverable

Apply the audience profile to the raw material:

### Formatting Rules

1. **Technical depth:** Match the reader's level. Don't explain what they already know. Don't skip what they need to understand.

2. **Vocabulary:** Use their language. If the profile says "no jargon," translate technical terms. If the profile says "technical," use precise terminology.

3. **Structure:** Follow their preferred format. Some readers want narrative. Others want bullet points. Some want the conclusion first, then supporting details.

4. **Length:** Match their attention budget. Executives get one page. Engineers get as much detail as needed. Default to shorter.

5. **Emphasis:** Lead with what they care about. If they care about cost, cost is paragraph one. If they care about timeline, timeline is paragraph one.

### Adaptation Checklist

Before finalizing, verify:
- [ ] Would this person understand every term used?
- [ ] Is the most important information (for them) in the first paragraph?
- [ ] Is the format what they'd expect to receive?
- [ ] Are there any assumptions that need explaining for this reader?
- [ ] Is it the right length for their context?

## Step 5: Output

1. **Present the deliverable** in the conversation
2. **Save to file** if appropriate:
   - `.scratch/deliverables/{audience}-{type}-{date}.md` for drafts
   - Or a project-appropriate location for final versions
3. **Summary line:** "Packaged for {audience} ({type}) -- {word count} words, {format}."

## Creating Audience Profiles

For best results, create audience profiles at `audience-profiles/<name>.md`:

```markdown
# Audience Profile: {Name}

## Role
{Job title or relationship}

## Communication Style
- Technical depth: [none | basic | moderate | deep]
- Jargon tolerance: [low | medium | high]
- Preferred length: [brief | standard | detailed]
- Format preference: [bullets | narrative | structured | visual]

## What They Care About
- {Priority 1}
- {Priority 2}
- {Priority 3}

## What to Avoid
- {Anti-pattern 1}
- {Anti-pattern 2}

## Language
- Primary: {language}
- Notes: {any language-specific preferences}

## Examples of What Works
- {A deliverable format or approach that landed well}
```

## Usage Examples

```
/package ceo --type brief --topic "Q1 infrastructure costs"
  >> Shapes a brief focused on business impact and cost, minimal technical detail

/package engineering-lead --type report --topic "database migration options"
  >> Shapes a report with full technical depth, comparison tables, risk analysis

/package new-hire --type memo --topic "how our deployment pipeline works"
  >> Shapes an explanatory memo assuming no prior context, defines all terms

/package investor --type email --topic "product update"
  >> Shapes a concise email focused on traction metrics and milestones
```

## Why This Matters

The same information fails or succeeds based on how it's packaged. A database migration plan written for an engineer works. That same document sent to a CEO fails -- not because the content is wrong, but because the packaging is wrong. This skill makes the packaging automatic.
