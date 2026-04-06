# Claude Code Toolkit

Skills, CLAUDE.md sections, and methodology workflows for Claude Code. Grab what you need.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)

---

## Get Started in 60 Seconds

### New to Claude Code?

1. [Install Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview)
2. Copy `starter-claude.md` to your project root as `CLAUDE.md`
3. Drop any skill folder into `.claude/skills/`
4. Done -- Claude now has that capability

### Already have your setup?

Browse the use-case directory below. Each piece is independent -- grab what you need, skip what you don't.

---

## What's Inside

### Skills (drop into `.claude/skills/`)

| Skill | Category | What It Does |
|-------|----------|--------------|
| [/research](prompt-engineering/research-workflow/) | Prompt Engineering | Multi-perspective research with parallel agents. 3 investigators debate a topic before synthesizing findings. |
| [/package](project-management/package-workflow/) | Project Management | Shape any deliverable for its specific audience. Same content, different packaging for different readers. |
| [/monitor](monitoring/monitor-watchdog/) | Monitoring | Autonomous watchdog for long-running processes. Delta-based ETAs, adaptive polling frequency, two-tier intelligence (script + agent), and safe auto-intervention on stalls. |
| [/request](project-management/request-lifecycle/) | Project Management | 6-skill family: capture >> develop >> audit cycle for bugs, improvements, and cross-session work. Hub routes to capture, develop, audit, verify, and close. Every fix produces a documentation trail. |
| [/wrap](project-management/session-wrap/) | Project Management | Session wrap-up with narrative accomplishments, decision capture, auto-commit, and daily logging. Clean handoff to your future self. |

### CLAUDE.md Sections (paste into your CLAUDE.md)

| Section | What It Does |
|---------|--------------|
| [Surgical Iteration](claude-md-sections/surgical-iteration.md) | Enforces precise, root-cause-driven changes instead of shotgun rewrites. |
| [File Creation Policy](claude-md-sections/file-creation-policy.md) | Prevents temp files from scattering across your project. Everything ephemeral goes to `.scratch/`. |

### Starter Config

| File | What It Does |
|------|--------------|
| [starter-claude.md](starter-claude.md) | Minimal CLAUDE.md with the highest-impact sections pre-filled. Copy as your `CLAUDE.md` and customize. |

---

## Install

### Option A: Script (recommended)

```bash
# Clone the repo
git clone https://github.com/TomasB2BC/claude-code-toolkit.git
cd claude-code-toolkit

# List everything available
python install.py --list

# Install a skill
python install.py research-workflow

# Append a CLAUDE.md section
python install.py surgical-iteration --append

# Copy the starter CLAUDE.md
python install.py starter

# Preview before installing
python install.py research-workflow --dry-run
```

### Option B: Manual

**Skills:** Copy the skill folder to `.claude/skills/<skill-name>/`
```bash
cp -r prompt-engineering/research-workflow/ .claude/skills/research-workflow/
```

**Sections:** Open the `.md` file, copy the content, paste into your `CLAUDE.md`.

**Starter:** Copy `starter-claude.md` to your project root as `CLAUDE.md`.

---

## What Makes These Different

Most Claude Code skills are **implementation skills** -- they do a specific task (generate tests, lint code, create components). These are **methodology skills** -- they change *how* Claude approaches work:

- **/research** doesn't just search the web. It spawns investigators with opposing viewpoints and forces them to challenge each other before presenting findings.
- **/package** doesn't just format output. It loads a profile of who's reading and reshapes everything -- vocabulary, structure, emphasis, depth -- for that specific person.

The CLAUDE.md sections work the same way -- they're not feature toggles, they're behavioral constraints that prevent common AI failure modes (over-engineering, temp file sprawl).

---

## Related

- **[diagram-engine](https://github.com/TomasB2BC/diagram-engine)** -- Generate publication-quality diagrams from natural language. 2,100-line layout engine with arrow routing, typography, and visual validation.
- These skills work standalone. If you want a full project workflow system, [GSD](https://github.com/coleam00/gsd) pairs well.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting skills or sections.

## License

[MIT](LICENSE) -- use it however you want.
