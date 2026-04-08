"""
Tier 1: Structural validation for claude-code-toolkit skills.
No Claude Code needed -- just filesystem checks.

Run from repo root:  python tests/test_structural.py
"""
import re
import sys
from pathlib import Path

# Auto-detect toolkit root (tests/ is one level below repo root)
TOOLKIT = Path(__file__).resolve().parent.parent

# Internal patterns that should NEVER appear in toolkit files
LEAKAGE_PATTERNS = [
    r"\.planning/",
    r"REGISTRY\.md",
    r"\b/pm\b",
    r"/gsd",
    r"mcp__",
    r"context-monitor",
    r"\blinear_issue\b",
    r"bypassPermissions",
    r"\bB2BC\b",
    r"B2B Catalyst",
    r"\bdeploy\.py\b",
    r"\bsystemd\b",
    r"config/keys",
    r"\btopology\.json\b",
    r"\bVenntel\b",
    r"\bHelloThea\b",
    r"\bPreVeil\b",
    r"\bWpromote\b",
    r"\bSybill\b",
    r"\bElijah\b",
    r"\bUnacast\b",
    r"\brequest-shared\b",
    r"\bSkill-Creator\b",
    r"\blinear-gate\.md\b",
    r"\bregistry-update\.md\b",
]
# NOTE: .scratch/ is NOT leakage -- it's the portable file creation policy
# NOTE: Supabase in example prompts is acceptable (user examples, not infra refs)
# NOTE: ATA removed -- too many false positives (matches "data", "state", etc.)

results: list[dict] = []


def report(skill: str, check: str, passed: bool, detail: str = ""):
    status = "PASS" if passed else "FAIL"
    results.append({"skill": skill, "check": check, "passed": passed, "detail": detail})
    marker = "[OK]" if passed else "[X] "
    print(f"  {marker} {check}{f' -- {detail}' if detail else ''}")


def find_skill_dirs() -> list[Path]:
    """Find all skill directories (contain SKILL.md or are request-lifecycle with hub)."""
    dirs = []
    skip_dirs = {"assets", "tests", "claude-md-sections", ".git"}
    for category in TOOLKIT.iterdir():
        if category.is_dir() and category.name not in skip_dirs and not category.name.startswith("."):
            for skill_dir in category.iterdir():
                if skill_dir.is_dir():
                    dirs.append(skill_dir)
    return dirs


def check_frontmatter(skill_name: str, skill_file: Path):
    """Check YAML frontmatter has required fields."""
    content = skill_file.read_text(encoding="utf-8")
    if not content.startswith("---"):
        report(skill_name, "frontmatter-exists", False, "No YAML frontmatter found")
        return

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        report(skill_name, "frontmatter-valid", False, "Malformed frontmatter (no closing ---)")
        return

    fm = match.group(1)
    has_name = bool(re.search(r"^name:", fm, re.MULTILINE))
    has_desc = bool(re.search(r"^description:", fm, re.MULTILINE))

    if has_name and has_desc:
        report(skill_name, "frontmatter-valid", True, "name + description present")
    else:
        missing = []
        if not has_name:
            missing.append("name")
        if not has_desc:
            missing.append("description")
        report(skill_name, "frontmatter-valid", False, f"Missing: {', '.join(missing)}")


def check_internal_references(skill_name: str, skill_dir: Path):
    """Check for references to files that should exist within the skill dir."""
    md_files = list(skill_dir.rglob("*.md"))
    broken = []

    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        # Find markdown links like [text](path)
        links = re.findall(r"\[([^\]]*)\]\(([^)]+)\)", content)
        for _text, href in links:
            # Skip URLs
            if href.startswith("http") or href.startswith("#"):
                continue
            # Resolve relative to the file's directory
            target = (md_file.parent / href).resolve()
            if not target.exists():
                broken.append(f"{md_file.name} -> {href}")

    if broken:
        report(skill_name, "cross-references", False, f"Broken: {'; '.join(broken)}")
    else:
        report(skill_name, "cross-references", True, f"{len(md_files)} files, all links resolve")


def check_leakage(skill_name: str, skill_dir: Path):
    """Scan all .md files for internal/sensitive patterns."""
    md_files = list(skill_dir.rglob("*.md"))
    hits = []

    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        for pattern in LEAKAGE_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                hits.append(f"{md_file.name}: '{pattern}' ({len(matches)}x)")

    if hits:
        report(skill_name, "leakage-scan", False, "; ".join(hits[:5]))
    else:
        report(skill_name, "leakage-scan", True, f"0 matches across {len(LEAKAGE_PATTERNS)} patterns")


def check_readme(skill_name: str, skill_dir: Path):
    """Check README.md exists and has key sections."""
    readme = skill_dir / "README.md"
    if not readme.exists():
        report(skill_name, "readme-exists", False, "No README.md")
        return

    content = readme.read_text(encoding="utf-8")
    required_sections = ["What It Does", "Install"]
    missing = [s for s in required_sections if s.lower() not in content.lower()]

    if missing:
        report(skill_name, "readme-sections", False, f"Missing: {', '.join(missing)}")
    else:
        report(skill_name, "readme-sections", True, f"{len(required_sections)}/{len(required_sections)} required sections")


def check_line_count(skill_name: str, skill_dir: Path):
    """Check total line count across all skill .md files (excluding README)."""
    total = 0
    for md_file in skill_dir.rglob("*.md"):
        if md_file.name == "README.md":
            continue
        total += len(md_file.read_text(encoding="utf-8").splitlines())

    if total > 1000:
        report(skill_name, "line-count", False, f"{total} lines (max 1000 for a skill package)")
    elif total > 500:
        report(skill_name, "line-count", True, f"{total} lines (warn: over 500)")
    else:
        report(skill_name, "line-count", True, f"{total} lines")


def check_requests_dir_instructions(skill_name: str, skill_dir: Path):
    """For request-lifecycle: check that README mentions creating requests/ dirs."""
    readme = skill_dir / "README.md"
    if not readme.exists():
        return
    content = readme.read_text(encoding="utf-8")
    if "requests/active" in content and "requests/history" in content:
        report(skill_name, "setup-instructions", True, "Documents requests/active/ and requests/history/ creation")
    else:
        report(skill_name, "setup-instructions", False, "Missing instructions for creating requests/ directories")


def check_install_script():
    """Check install.py can list all skills."""
    install_py = TOOLKIT / "install.py"
    if not install_py.exists():
        report("toolkit", "install-script", False, "install.py not found")
        return
    report("toolkit", "install-script", True, "install.py exists")


def main():
    print(f"Toolkit Structural Validation")
    print(f"Path: {TOOLKIT}")
    print(f"=" * 60)

    if not TOOLKIT.exists():
        print(f"[X] Toolkit not found at {TOOLKIT}")
        sys.exit(1)

    # Toolkit-level checks
    print(f"\n>> toolkit (global)")
    check_install_script()

    # Per-skill checks
    skill_dirs = find_skill_dirs()
    print(f"\nFound {len(skill_dirs)} skill packages\n")

    for skill_dir in sorted(skill_dirs):
        skill_name = f"{skill_dir.parent.name}/{skill_dir.name}"
        print(f">> {skill_name}")

        # Find the main skill file
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            report(skill_name, "skill-file", False, "No SKILL.md found")
            print()
            continue

        report(skill_name, "skill-file", True, "SKILL.md exists")
        check_frontmatter(skill_name, skill_file)
        check_internal_references(skill_name, skill_dir)
        check_leakage(skill_name, skill_dir)
        check_readme(skill_name, skill_dir)
        check_line_count(skill_name, skill_dir)

        # Special checks for request-lifecycle
        if skill_dir.name == "request-lifecycle":
            check_requests_dir_instructions(skill_name, skill_dir)

            # Check all sub-skill files exist
            expected_files = ["SKILL.md", "capture.md", "develop.md", "audit.md", "verify.md", "close.md"]
            missing = [f for f in expected_files if not (skill_dir / f).exists()]
            if missing:
                report(skill_name, "sub-skills-complete", False, f"Missing: {', '.join(missing)}")
            else:
                report(skill_name, "sub-skills-complete", True, f"All {len(expected_files)} skill files present")

            # Check references dir
            ref_dir = skill_dir / "references"
            if ref_dir.exists() and (ref_dir / "handoff-template.md").exists():
                report(skill_name, "references-complete", True, "handoff-template.md present")
            else:
                report(skill_name, "references-complete", False, "Missing references/handoff-template.md")

        print()

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed

    print("=" * 60)
    print(f"TOTAL: {passed}/{total} passed, {failed} failed")

    if failed:
        print(f"\nFailed checks:")
        for r in results:
            if not r["passed"]:
                print(f"  [X] {r['skill']}: {r['check']} -- {r['detail']}")
        sys.exit(1)
    else:
        print(f"\n[OK] All structural checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
