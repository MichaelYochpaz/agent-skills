# Agent Skills

A collection of reusable [Agent Skills](https://agentskills.io) for AI coding assistants.

## Available Skills

<!-- SKILLS_TABLE_START -->
| Skill | Description |
|-------|-------------|
| [`acli-jira`](skills/acli-jira/) | Helps agents use Atlassian CLI (`acli`) to inspect Jira issues, search with JQL, read or add comments, manage attachments, and update tickets. |
| [`gh-cli`](skills/gh-cli/) | Helps agents use GitHub CLI (`gh`) to inspect repositories, manage issues and pull requests, review releases and Actions, search code, and call GitHub APIs. |
| [`glab-cli`](skills/glab-cli/) | Helps agents use GitLab CLI (`glab`) to inspect projects, manage issues and merge requests, work with pipelines and releases, call the GitLab API, and target self-managed hosts. |
<!-- SKILLS_TABLE_END -->

## Installation

Install skills using GitHub CLI / Skills CLI.
Both support `antigravity`, `claude-code`, `cline`, `codex`, `cursor`, `gemini-cli`, `github-copilot`, `opencode`, `pi`, `windsurf` and more.

### GitHub CLI

Install individual skills using [`gh skill`](https://cli.github.com/manual/gh_skill_install):

```bash
# Interactive (shows all available skills)
gh skill install michaelyochpaz/agent-skills

# Install a specific skill for a specific agent ('claude-code', 'codex', etc.)
gh skill install michaelyochpaz/agent-skills <skill-name> --agent <agent>

# Install to user scope (available across all projects)
gh skill install michaelyochpaz/agent-skills <skill-name> --agent <agent> --scope user
```

> **Note:** `gh skill install` defaults to project scope.
> Add `--scope user` for personal installs available across all projects.

### npx skills

Install using Vercel's [`skills` CLI](https://github.com/vercel-labs/skills):

```bash
# Install a specific skill
npx skills add michaelyochpaz/agent-skills --skill <skill-name>

# Install all skills for a specific agent
npx skills add michaelyochpaz/agent-skills --skill '*' -a <agent>
```

### Manual

Clone the repo and copy or symlink individual skill directories into your
agent's skill path:

```bash
git clone https://github.com/michaelyochpaz/agent-skills.git
cp -r agent-skills/skills/<skill-name> <target-path>
```

## License

[MIT](LICENSE)
