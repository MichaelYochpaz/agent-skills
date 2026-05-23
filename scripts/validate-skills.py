"""Validate skill directory structure and README table entries.

Checks:
  - Every skills/*/ directory contains a SKILL.md file
  - Directory names match the Agent Skills spec format
  - SKILL.md has YAML frontmatter with required name and description fields
  - SKILL.md frontmatter name matches the directory name
  - Every skill directory has a matching README table entry
  - Every README table entry has a matching skill directory

Exit 0 if all checks pass. Exit 1 on validation errors.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
README_PATH = REPO_ROOT / "README.md"

DIR_NAME_RE = re.compile(r"^[a-z0-9](-?[a-z0-9])*$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.+?\n)---\s*\n", re.DOTALL)
FRONTMATTER_NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
FRONTMATTER_DESC_RE = re.compile(r"^description:\s*(.+)$", re.MULTILINE)

TABLE_START = "<!-- SKILLS_TABLE_START -->"
TABLE_END = "<!-- SKILLS_TABLE_END -->"

# Matches table rows like: | [`skill-name`](skills/skill-name/) | ... |
TABLE_ENTRY_RE = re.compile(r"\[`([^`]+)`\]\(skills/([^/)]+)/?\)")


def get_readme_skill_names() -> set[str]:
    """Extract skill names from the README table between markers."""
    if not README_PATH.is_file():
        return set()

    content = README_PATH.read_text(encoding="utf-8")
    start = content.find(TABLE_START)
    end = content.find(TABLE_END)
    if start == -1 or end == -1:
        return set()

    table_content = content[start:end]
    names: set[str] = set()
    for match in TABLE_ENTRY_RE.finditer(table_content):
        names.add(match.group(2))  # Use the path segment as the canonical name
    return names


def validate() -> list[str]:
    """Run all validations. Return list of error messages."""
    errors: list[str] = []

    # Discover all directories under skills/ (including those without SKILL.md).
    all_dirs: list[Path] = []
    if SKILLS_DIR.is_dir():
        all_dirs = sorted(
            d
            for d in SKILLS_DIR.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        )

    # Check that every skills/ directory has a SKILL.md.
    for d in all_dirs:
        if not (d / "SKILL.md").is_file():
            errors.append(f"{d.name}: missing SKILL.md")

    # Validate directories that have SKILL.md.
    skill_dirs = [d for d in all_dirs if (d / "SKILL.md").is_file()]
    skill_names: set[str] = set()

    for skill_dir in skill_dirs:
        name = skill_dir.name
        skill_names.add(name)

        # Directory name format.
        if len(name) > 64:
            errors.append(f"{name}: directory name exceeds 64 characters")
        if not DIR_NAME_RE.match(name):
            errors.append(
                f"{name}: directory name must be lowercase a-z/0-9/hyphens, "
                "no leading/trailing/consecutive hyphens"
            )

        # Extract YAML frontmatter block.
        content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        fm_match = FRONTMATTER_RE.match(content)
        if not fm_match:
            errors.append(f"{name}: SKILL.md missing YAML frontmatter (---)")
            continue

        frontmatter = fm_match.group(1)

        # Frontmatter name must match directory name.
        name_match = FRONTMATTER_NAME_RE.search(frontmatter)
        if not name_match:
            errors.append(f"{name}: SKILL.md missing 'name:' in frontmatter")
            continue

        fm_name = name_match.group(1).strip().strip("\"'")
        if fm_name != name:
            errors.append(
                f"{name}: SKILL.md name '{fm_name}' does not match "
                f"directory name '{name}'"
            )

        # Frontmatter must include a description.
        desc_match = FRONTMATTER_DESC_RE.search(frontmatter)
        if not desc_match:
            errors.append(
                f"{name}: SKILL.md missing 'description:' in frontmatter"
            )
        elif not desc_match.group(1).strip().strip("\"'"):
            errors.append(f"{name}: SKILL.md 'description:' is empty")

    # Bi-directional README table validation.
    readme_names = get_readme_skill_names()

    for name in sorted(skill_names - readme_names):
        errors.append(
            f"{name}: skill directory exists but has no entry in the "
            "README skills table"
        )

    for name in sorted(readme_names - skill_names):
        errors.append(
            f"{name}: listed in README skills table but has no matching "
            "skill directory"
        )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Skill validation failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
