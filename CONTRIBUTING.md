# Contributing to Claude Code Toolkit

Contributions are welcome. Here's how to submit a skill or CLAUDE.md section.

## What We're Looking For

### Skills

A skill is a folder with a `SKILL.md` and optionally a `README.md` and reference files.

**Quality bar:**
- **Atomic** -- one skill, one purpose. If it does two things, split it into two skills.
- **Self-contained** -- works by dropping the folder into `.claude/skills/`. No external dependencies beyond what Claude Code provides.
- **Opinionated** -- don't water down the approach to be "more flexible." The value is in the specific methodology, not in configurability.
- **Tested** -- you've used it yourself in real work. Theoretical skills that haven't been battle-tested are not ready.

### CLAUDE.md Sections

A section is a single `.md` file in `claude-md-sections/`.

**Quality bar:**
- **Copy-paste ready** -- a user can paste it directly into their CLAUDE.md
- **Brief** -- under 50 lines. If it's longer, it's probably trying to do too much.
- **Behavioral** -- it changes how Claude works, not what Claude knows. Configuration over information.

## How to Submit

1. Fork this repo
2. Add your skill or section following the existing directory structure
3. Open a pull request with:
   - What it does (one sentence)
   - Why it's useful (the problem it solves)
   - How you've used it (real examples)

## Review Process

Pull requests are reviewed in weekly batches. Expect feedback within 7 days.

Common rejection reasons:
- Too generic (could apply to any AI tool, not specific to Claude Code workflows)
- Not self-contained (requires external setup or dependencies)
- Overlaps with an existing piece without clear improvement
- No evidence of real-world usage

## Style Guidelines

- No emojis in skill files or documentation
- Use ASCII alternatives for indicators (`>>`, `[OK]`, `[X]`, `[!]`)
- Keep descriptions concrete and actionable
- Include usage examples with realistic scenarios

## License

By contributing, you agree that your contribution is licensed under the MIT license.
