# /package -- Audience-Aware Deliverable Packaging

Shape any output for its specific reader. Same information, different packaging.

## What It Does

Loads an audience profile (who is reading this, what they care about, how they prefer information) and shapes the deliverable accordingly. A database migration plan for an engineer looks completely different from one for a CEO -- this skill handles that translation automatically.

## When to Use It

- Writing an email, report, or brief for a specific person
- Preparing meeting notes for different stakeholders
- Translating technical findings for non-technical readers
- Any time the reader matters as much as the content

## Example Usage

```
/package ceo --type brief --topic "infrastructure costs"
/package engineering-lead --type report --topic "database migration"
/package new-hire --type memo --topic "deployment pipeline"
```

## How It Works

1. **Loads audience profile** -- who they are, what they care about, their jargon tolerance, preferred format
2. **Gathers source material** -- project state, recent work, relevant data
3. **Shapes the output** -- adjusts technical depth, vocabulary, structure, length, and emphasis
4. **Verifies fit** -- checks that every term is understandable, priorities are front-loaded, format matches expectations

## Audience Profiles

For best results, create profiles at `audience-profiles/<name>.md` with:
- Communication style and technical depth
- What they care about (priorities)
- What to avoid (anti-patterns)
- Format preference

Without a profile, the skill infers a basic profile from the audience name/role.

## Install

**Option A: Script**
```bash
python install.py package-workflow
```

**Option B: Manual**
Copy `project-management/package-workflow/` to `.claude/skills/package-workflow/`
