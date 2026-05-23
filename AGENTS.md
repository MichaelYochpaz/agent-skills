# AGENTS.md

## Overview

A public repository distributing reusable [Agent Skills](https://agentskills.io) for AI coding tools.
Skills live under `skills/` and can be consumed by many tools via two major installers:
- [GitHub CLI](https://cli.github.com/manual/) — [`gh skill install`](https://cli.github.com/manual/gh_skill_install)
- [Skills CLI](https://www.skills.sh/docs) — [`npx skills add`](https://github.com/vercel-labs/skills).

## Commands

- Run all pre-commit hooks: `prek run --all-files --show-diff-on-failure`
- Validate skill structure: `uv run scripts/validate-skills.py`

## Critical Rules

- Set SKILL.md frontmatter `name` to exactly match the parent directory name. Directory names: lowercase a-z, 0-9, hyphens only; max 64 chars; no leading, trailing, or consecutive hyphens.
- Include a non-empty `description` field in SKILL.md frontmatter.
- Add an entry to the README skills table between `<!-- SKILLS_TABLE_START -->` / `<!-- SKILLS_TABLE_END -->` markers for every new skill. The pre-commit hook validates that skill directories and README table entries match bidirectionally.

## Adding a Skill

Create `skills/<skill-name>/SKILL.md` with YAML frontmatter. Write the `description` field as trigger conditions for when agents should activate the skill.

Add a row to the README skills table:

```md
| [`<skill-name>`](skills/<skill-name>/) | <Brief human-facing description> |
```

Optional subdirectories: `references/` (supplementary docs), `scripts/` (executable tools), `assets/` (static files).

## Commit Messages

Format: `<type>(<scope>): <description>`

### Types

Select the first matching type:

1. `revert` — undoes a previous commit
2. `fix` — something was *wrong or broken* before this commit (not for adding something absent — that's `feat`)
3. `refactor` — changed *only where things are*, not *what they say or do* (file moves, renames, structural reorganization with no content change; if uncertain whether capability changed, use `feat`)
4. `feat` — **default**; everything else — new components, new content, value changes, behavioral modifications, capability additions

### Scopes

The scope is the **skill name** — the directory containing the skill: `skills/gh-cli/` → `gh-cli`.

Fixed scopes:

- `AGENTS.md`, `CLAUDE.md` → `rules`
- `.gitignore`, `LICENSE` → `repo`
- `scripts/` → `scripts`
- `README.md` → `readme`
- `.github/` → `ci`
- `prek.toml` → `hooks`

### Descriptions

- Imperative mood, lowercase after colon: `add`, `remove`, `update`
- No trailing period
- Describe purpose and impact, not implementation details — what capability was added or what behavior changed, not which files were touched or how the change works
- Revert format: `revert(<original-scope>): revert "<original-subject>"`
