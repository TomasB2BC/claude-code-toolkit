#!/usr/bin/env python3
"""
install.py -- Install skills and CLAUDE.md sections from the claude-code-toolkit.

Usage:
    python install.py --list                          List all available pieces
    python install.py research-workflow               Install a skill
    python install.py surgical-iteration --append     Append a section to CLAUDE.md
    python install.py starter                         Copy starter CLAUDE.md
    python install.py research-workflow --dry-run     Preview without copying

Zero dependencies -- uses Python standard library only.
"""

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent

# --- Piece Discovery ---

def discover_pieces():
    """Find all installable pieces in the repo."""
    pieces = []

    # Skills: any directory containing SKILL.md
    for skill_file in REPO_ROOT.rglob("SKILL.md"):
        skill_dir = skill_file.parent
        rel = skill_dir.relative_to(REPO_ROOT)
        name = skill_dir.name

        # Read first line of README for description
        readme = skill_dir / "README.md"
        desc = ""
        if readme.exists():
            first_line = readme.read_text(encoding="utf-8").split("\n")[0]
            # Strip markdown heading prefix
            desc = first_line.lstrip("# ").strip()

        pieces.append({
            "name": name,
            "type": "skill",
            "path": rel,
            "description": desc or f"Skill: {name}",
        })

    # CLAUDE.md sections: .md files in claude-md-sections/
    sections_dir = REPO_ROOT / "claude-md-sections"
    if sections_dir.exists():
        for md_file in sorted(sections_dir.glob("*.md")):
            name = md_file.stem

            # Read first line for description
            first_line = md_file.read_text(encoding="utf-8").split("\n")[0]
            desc = first_line.lstrip("# ").strip()

            pieces.append({
                "name": name,
                "type": "section",
                "path": md_file.relative_to(REPO_ROOT),
                "description": desc or f"CLAUDE.md section: {name}",
            })

    # Starter CLAUDE.md
    starter = REPO_ROOT / "starter-claude.md"
    if starter.exists():
        pieces.append({
            "name": "starter",
            "type": "starter",
            "path": Path("starter-claude.md"),
            "description": "Minimal starter CLAUDE.md with best sections pre-filled",
        })

    return pieces


def find_piece(name, pieces):
    """Find a piece by name (case-insensitive)."""
    name_lower = name.lower()
    for p in pieces:
        if p["name"].lower() == name_lower:
            return p
    return None


# --- Install Actions ---

def install_skill(piece, target_dir, dry_run=False):
    """Copy a skill folder to .claude/skills/."""
    src = REPO_ROOT / piece["path"]
    dest = target_dir / piece["name"]

    if dry_run:
        print(f"[DRY RUN] Would copy: {src} -> {dest}")
        for f in src.rglob("*"):
            if f.is_file():
                print(f"  {f.relative_to(src)}")
        return

    dest.mkdir(parents=True, exist_ok=True)
    for f in src.rglob("*"):
        if f.is_file():
            rel = f.relative_to(src)
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)

    print(f"[OK] Installed skill: {piece['name']}")
    print(f"     Location: {dest}")
    print(f"     Usage: /{piece['name']}")


def install_section(piece, target_file, dry_run=False, append=False):
    """Append a CLAUDE.md section to the target file."""
    src = REPO_ROOT / piece["path"]
    content = src.read_text(encoding="utf-8")

    # Extract just the section content (skip the description header and ---
    # separator that are instructions for the repo, not for the CLAUDE.md)
    lines = content.split("\n")
    section_start = None
    for i, line in enumerate(lines):
        if line.strip() == "---":
            section_start = i + 1
            break

    if section_start is not None:
        section_content = "\n".join(lines[section_start:]).strip()
    else:
        section_content = content.strip()

    if dry_run:
        print(f"[DRY RUN] Would append to {target_file}:")
        print(f"  Section: {piece['name']}")
        print(f"  Lines: {len(section_content.splitlines())}")
        return

    if not append:
        print(f"[!] Use --append to add this section to your CLAUDE.md:")
        print(f"    python install.py {piece['name']} --append")
        print()
        print("Preview:")
        print(section_content[:500])
        if len(section_content) > 500:
            print(f"  ... ({len(section_content)} chars total)")
        return

    # Append with spacing
    existing = ""
    if target_file.exists():
        existing = target_file.read_text(encoding="utf-8")

    separator = "\n\n" if existing and not existing.endswith("\n\n") else "\n" if existing and not existing.endswith("\n") else ""
    target_file.write_text(existing + separator + section_content + "\n", encoding="utf-8")

    print(f"[OK] Appended section: {piece['name']}")
    print(f"     File: {target_file}")


def install_starter(piece, target_file, dry_run=False):
    """Copy starter-claude.md as CLAUDE.md."""
    src = REPO_ROOT / piece["path"]

    if dry_run:
        print(f"[DRY RUN] Would copy: {src} -> {target_file}")
        return

    if target_file.exists():
        print(f"[!] {target_file} already exists.")
        print(f"    To overwrite, delete it first and re-run.")
        print(f"    To see the starter content: python install.py starter --dry-run")
        return

    shutil.copy2(src, target_file)
    print(f"[OK] Created: {target_file}")
    print(f"     Your CLAUDE.md is ready. Customize it for your project.")


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(
        description="Install skills and CLAUDE.md sections from claude-code-toolkit.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python install.py --list\n"
               "  python install.py research-workflow\n"
               "  python install.py surgical-iteration --append\n"
               "  python install.py starter\n"
               "  python install.py research-workflow --dry-run\n",
    )
    parser.add_argument("piece", nargs="?", help="Name of the skill or section to install")
    parser.add_argument("--list", action="store_true", help="List all available pieces")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be installed")
    parser.add_argument("--append", action="store_true", help="Append section to CLAUDE.md")
    parser.add_argument("--target", type=str, default=None, help="Override default target directory/file")

    args = parser.parse_args()
    pieces = discover_pieces()

    if args.list:
        print("Available pieces:\n")
        for p in pieces:
            icon = {"skill": "skill", "section": "section", "starter": "starter"}[p["type"]]
            print(f"  [{icon:>7}]  {p['name']:30s} {p['description']}")
        print(f"\nTotal: {len(pieces)} pieces")
        print("\nInstall:  python install.py <name>")
        print("Preview:  python install.py <name> --dry-run")
        return

    if not args.piece:
        parser.print_help()
        return

    piece = find_piece(args.piece, pieces)
    if not piece:
        print(f"[X] Unknown piece: {args.piece}")
        print(f"    Run 'python install.py --list' to see available pieces.")
        sys.exit(1)

    # Resolve target
    cwd = Path.cwd()

    if piece["type"] == "skill":
        target = Path(args.target) if args.target else cwd / ".claude" / "skills"
        install_skill(piece, target, dry_run=args.dry_run)

    elif piece["type"] == "section":
        target = Path(args.target) if args.target else cwd / "CLAUDE.md"
        install_section(piece, target, dry_run=args.dry_run, append=args.append)

    elif piece["type"] == "starter":
        target = Path(args.target) if args.target else cwd / "CLAUDE.md"
        install_starter(piece, target, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
