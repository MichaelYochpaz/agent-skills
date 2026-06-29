---
name: gh-cli
description: GitHub CLI (gh) for interacting with GitHub from the command line. Covers repositories, issues, pull requests, releases, Actions, discussions, code search, and the GitHub REST/GraphQL API. Use when performing any GitHub-related operation, or when looking up code examples and implementation patterns in remote repositories.
license: MIT
metadata:
  author: Michael Yochpaz
  source: https://github.com/michaelyochpaz/agent-skills
---

# GitHub CLI (`gh`)

Interact with GitHub from the command line: repositories, releases, issues, PRs, discussions, search, code review, and Actions.

Verified with `gh` 2.95.0.

## Agent Guidelines

- For known remote files or directories, use `gh repo read-file` / `gh repo read-dir` (preview in `gh` 2.95). For older `gh` versions or API-only needs, use the contents API fallback in [API Patterns](references/api-patterns.md).
- When a task requires searching across files or exploring unfamiliar code where paths aren't known upfront, clone to a temp directory (`gh repo clone owner/repo <temp-dir> -- --depth 1`) and use local file-reading and search tools.
- Prefer default text output over `--json` for reading/viewing — it is more token-efficient. Use `--json` with `--jq` only when extracting specific fields programmatically. To discover supported fields, run the command with `--json` and no field list, then request only the fields you need.
- When viewing logs or diffs, scope output first (e.g., `--name-only`, `--log-failed`) before fetching full content.
- The `--repo` flag is unnecessary when running inside a cloned repository — the current directory's repo is used by default. For `gh api`, use the explicit path (`repos/OWNER/REPO/...`) or set the `GH_REPO` environment variable.
- Use this skill for covered workflows. When a needed flag or field is missing here, a command fails with an unknown/changed flag, or the command is marked preview, check that specific command's help (e.g., `gh pr diff --help`).

## Safety

- **Write operations** (`create`, `edit`, `comment`, `review`, `close`, `merge`, `delete`, `rerun`, `run cancel`, `workflow run/enable/disable`, discussion mutations) modify GitHub state. Confirm with the user before executing, especially on repositories you do not own.
- **`gh api` with `--method POST/PUT/PATCH/DELETE`** sends write requests. Double-check the endpoint and payload. Default method is GET (safe); adding `-f`/`-F` parameters switches the default to POST.
- **Destructive operations** (`delete`, `close`, `merge --admin`) may be irreversible. Require explicit user confirmation.

## Prerequisites

Verify `gh` is installed and authenticated before running commands:

```bash
gh --version
gh auth status
```

If not authenticated, guide the user through `gh auth login`.

## Common Flags

These flags are available on many command groups, but support varies by command:

- `--repo OWNER/REPO` -- Target a different repository (default: current directory's repo). Also accepts full URLs.
- `--json FIELDS` -- Output as JSON with specified fields. Pass without a value to list available fields.
- `--jq EXPRESSION` -- Filter JSON output using jq syntax. Requires `--json`.
- `--template STRING` -- Format JSON output using a Go template (alternative to `--jq`).
- `--web` -- Open the resource in the browser instead of displaying in terminal.
- `--limit N` -- Maximum number of results for list commands (default is usually 30).

```bash
gh pr list --json number,title,author --jq '.[] | "\(.number) \(.title) (\(.author.login))"'
gh issue view 123 --web
```

## Repositories

### View

Display a repository's description, README, stars, language breakdown, and other metadata.

```bash
gh repo view owner/repo
gh repo view owner/repo --json name,description,defaultBranchRef,languages,stargazerCount
```

### Clone

Clone a repository locally. Automatically configures the remote and, for forks, sets up the upstream remote.

```bash
gh repo clone owner/repo [target-directory]
```

### Read remote repository contents

For quick reads of known files or directories, use the repository read commands (preview in `gh` 2.95):

```bash
# Known file
gh repo read-file src/main.py --repo owner/repo --ref main

# Known directory
gh repo read-dir src --repo owner/repo --ref main

# Fallback for older gh versions
gh api "repos/OWNER/REPO/contents/src/main.py?ref=main" -H "Accept: application/vnd.github.raw+json"
```

For output shapes, file-size limits, and directory-listing caveats, see [API Patterns](references/api-patterns.md). For multi-file exploration, clone instead (see Agent Guidelines).

### List repositories

List repositories owned by a user or organization, with optional language and visibility filters.

```bash
gh repo list owner --limit 30
```

## Releases

### List

List releases in a repository, ordered by creation date (newest first). Defaults to showing all releases including pre-releases and drafts.

```bash
gh release list --repo owner/repo --limit 10
```

Flags:
- `--exclude-pre-releases` -- Exclude pre-releases
- `--exclude-drafts` -- Exclude drafts

Key JSON fields: `tagName`, `name`, `publishedAt`, `isLatest`, `isDraft`, `isPrerelease`, `isImmutable`

### View (changelog, assets)

Display a release's changelog body, tag, assets, and metadata. Omit the tag to view the latest release.

```bash
gh release view --repo owner/repo                         # Latest release
gh release view v1.2.0 --repo owner/repo                  # Specific tag
gh release view v1.2.0 --json tagName,body,assets,publishedAt
```

Key JSON fields: `tagName`, `name`, `body`, `assets`, `author`, `publishedAt`, `isDraft`, `isPrerelease`, `isImmutable`, `url`

## Issues

### List

List issues in a repository, filtered by state, label, assignee, or search query. Defaults to open issues only.

```bash
gh issue list --repo owner/repo
gh issue list --repo owner/repo --state all --label bug --assignee @me
gh issue list --repo owner/repo --search "error no:assignee sort:created-asc"
```

Flags:
- `--state VALUE` -- `open` (default), `closed`, `all`
- `--label NAME` -- Filter by label (repeat for multiple)
- `--assignee LOGIN` -- Filter by assignee (`@me` for self)
- `--search QUERY` -- GitHub search syntax

Key JSON fields: `number`, `title`, `state`, `stateReason`, `author`, `labels`, `assignees`, `createdAt`, `updatedAt`, `url`

### View

Display an issue's title, body, labels, assignees, and status. Use `--comments` to include the full comment thread.

```bash
gh issue view 123
gh issue view 123 --comments
gh issue view 123 --json title,body,labels,comments,state
```

### Create

Create a new issue with a title, body, labels, and assignees.

```bash
gh issue create --title "Bug: description" --body "Details..." --label bug --assignee user1
```

### Edit

Update an issue's title, body, labels, assignees, or milestone. All flags can be combined in a single call.

Flags:
- `--title TEXT` / `--body TEXT` -- Update title or body
- `--add-label NAME` / `--remove-label NAME` -- Modify labels
- `--add-assignee LOGIN` / `--remove-assignee LOGIN` -- Modify assignees
- `--milestone NAME` / `--remove-milestone` -- Set or remove milestone

### Comment

Add a comment to an existing issue.

```bash
gh issue comment 123 --body "Comment text"
```

### Close / Reopen

Close or reopen an issue. Optionally specify a close reason and leave a comment.

```bash
gh issue close 123 --comment "Fixed in PR #456" --reason "not planned"
gh issue close 123 --duplicate-of 456
gh issue reopen 123
```

Close reasons: `completed` (default), `not planned`, `duplicate`.

### Status

Show a summary of issues relevant to you: assigned to you, mentioning you, and opened by you.

```bash
gh issue status
```

For issue types, sub-issues, parent relationships, blocking dependencies, and their JSON fields (requires supported GitHub hosts), see [Issues reference](references/issues.md).

## Pull Requests

Use these commands to view and inspect PRs. For creating, merging, reviewing, and managing PRs, see [Pull Requests reference](references/pull-requests.md).

### List

List pull requests in a repository, filtered by state, author, label, or search query. Defaults to open PRs only.

```bash
gh pr list --repo owner/repo
gh pr list --repo owner/repo --state all --author @me --label "needs-review"
gh pr list --repo owner/repo --search "status:success review:required"
gh pr list --repo owner/repo --app dependabot
```

Flags:
- `--state VALUE` -- `open` (default), `closed`, `merged`, `all`
- `--draft` -- Filter by draft state
- `--author LOGIN` / `--assignee LOGIN` -- Filter by author or assignee
- `--label NAME` -- Filter by label
- `--search QUERY` -- GitHub search syntax
- `--app NAME` -- Filter by GitHub App author (e.g., `dependabot`)

Key JSON fields: `number`, `title`, `state`, `author`, `headRefName`, `baseRefName`, `labels`, `reviewDecision`, `isDraft`, `statusCheckRollup`, `files`, `commits`, `reviews`, `url`

### View

Display a PR's title, body, review status, checks, and other metadata. Without an argument, shows the PR for the current branch. Use `--comments` to include the comment thread.

```bash
gh pr view 123
gh pr view 123 --comments
gh pr view 123 --json title,body,files,commits,reviews,reviewDecision
```

### Status

Show a summary of PRs relevant to you: the current branch's PR, PRs you created, and PRs where your review is requested.

```bash
gh pr status
```

## Discussions

Use `gh discussion` for repository Discussions (preview in `gh` 2.94). Start with read commands and verify flags with `--help` because the command set is preview:

```bash
gh discussion list --repo owner/repo --limit 10
gh discussion view 123 --repo owner/repo --comments
```

For creating, editing, commenting, reply threads, JSON output shapes, and GraphQL fallback patterns, see [Discussions reference](references/discussions.md).

## Search

Search across GitHub for issues, PRs, code, commits, and repositories. Use `gh issue list` / `gh pr list` for one repository; use `gh search ...` for cross-repo or owner-wide queries.

For the full search query syntax, see the [GitHub search docs](https://docs.github.com/search-github/searching-on-github). For flags specific to each subcommand, run `gh search <subcommand> --help`.

**Rate limits:** Search APIs have stricter rate limits than the core API. Code search is the most restrictive (~10/min authenticated; requires authentication). Other search commands allow ~30/min authenticated or ~10/min unauthenticated. Check current quota with `gh api rate_limit --jq '.resources | {search, code_search}'`.

**When to clone instead:** See Agent Guidelines for when to clone vs. use the API.

**Bots and apps:** For GitHub App authors such as Dependabot, use `--app dependabot`; `--author dependabot` filters user accounts, not app authors.

**Reconnaissance:** When searching an unfamiliar repository, check its primary language first to select correct `--extension` and `--language` values:

```bash
gh repo view owner/repo --json primaryLanguage --jq '.primaryLanguage.name'
```

### Issues

Search for issues across repositories using keywords, labels, state, or GitHub search syntax.

```bash
gh search issues "error handling" --repo owner/repo
gh search issues --label bug --state open --assignee @me
gh search issues --app dependabot --repo owner/repo
gh search issues --involves username --comments ">10" --repo owner/repo
```

Key flags: `--repo`, `--owner`, `--state`, `--label`, `--assignee`, `--author`, `--app`, `--involves`, `--comments`, `--match`, `--sort`, `--include-prs`.

### PRs

Search for pull requests across repositories. Supports filtering by author, review status, merge state, and draft status.

```bash
gh search prs "refactor" --repo owner/repo
gh search prs --review-requested @me --state open
gh search prs --app dependabot --repo owner/repo
gh search prs --author username --merged --repo owner/repo
```

Key flags: `--repo`, `--owner`, `--state`, `--merged`, `--draft`, `--author`, `--assignee`, `--app`, `--label`, `--review`, `--review-requested`, `--base`, `--head`, `--checks`, `--sort`.

### Code

Search within file contents across GitHub repositories. Returns matching lines only (no line numbers, no surrounding context). Useful for locating files containing a pattern, but follow up with file reads or clone the repo to understand code logic.

**Limitations:** Uses a legacy search engine (results may not match github.com). Only searches the default branch. Only files under 384 KB are indexed. Every query must include at least one search term (qualifier-only searches like `--extension ts` alone will fail). Does not support `--sort` or `--order` — results are always ranked by relevance.

```bash
gh search code "functionName" --repo owner/repo
gh search code "createServer" --repo owner/repo --extension ts
gh search code "lint" --repo owner/repo --filename package.json
```

Key flags: `--repo`, `--owner`, `--extension`, `--filename`, `--language`, `--match`, `--size`.

Key JSON fields: `path`, `repository`, `sha`, `textMatches`, `url`.

The `textMatches` field provides fragment context with character-level match positions — use `--json path,textMatches` when you need more context than the default text output provides.

### Commits

Search commits by message text, author, committer date, or hash.

```bash
gh search commits "fix bug" --repo owner/repo
gh search commits --author username --committer-date ">2024-01-01"
gh search commits --hash abc1234
```

Key flags: `--repo`, `--owner`, `--author`, `--committer`, `--author-date`, `--committer-date`, `--author-name`, `--author-email`, `--hash`, `--merge`, `--sort`.

### Repositories

Search for repositories by keyword, language, topic, stars, license, or owner. Note: `--repo` is not available on this subcommand — use `--owner` to filter by owner.

```bash
gh search repos "keyword" --language python --sort stars --order desc
gh search repos --topic cli --stars ">1000" --language go
```

Key flags: `--owner`, `--language`, `--topic`, `--stars`, `--forks`, `--license`, `--created`, `--updated`, `--match`, `--sort`, `--include-forks`, `--visibility`.

### Excluding qualifiers (hyphen prefix)

Search queries with exclusions like `-label:bug` need special syntax to avoid shell flag interpretation. All flags (e.g., `--limit`) must appear before `--`; anything after `--` is interpreted as search query text:

```bash
# Unix-like shells
gh search issues -- "my query -label:bug"

# PowerShell
gh --% search issues -- "my query -label:bug"
```

## Other Commands

These commands are available but rarely needed in typical agent workflows. Run `gh <command> --help` for flags and usage.

- `gh browse` -- Open a repo, issue, PR, or file in the browser. Use `--no-browser` to print the URL instead of opening it.
- `gh label` -- List, create, edit, and delete repository labels. For _applying_ existing labels to issues/PRs, use `gh issue edit --add-label` or `gh pr edit --add-label` instead.
- `gh repo fork` -- Fork a repository to your account or an org (`--org NAME`), optionally cloning it (`--clone`).
- `gh repo sync` -- Sync a fork's branch with the upstream repository.
- `gh skill` -- Preview, install, list, and update agent skills (preview). Use only for explicit skill-management tasks.

## Troubleshooting

- **Not authenticated** -- Run `gh auth login` to authenticate. Verify with `gh auth status`.
- **Rate limited** -- Check quota with `gh api rate_limit --jq '.resources | {core, search, code_search, graphql}'`. Code search is the most restrictive (~10/min).
- **404 on file read** -- Verify the path exists by listing the parent directory first: `gh repo read-dir src --repo owner/repo` or `gh api "repos/OWNER/REPO/contents/src" --jq '.[].name'`.
- **Wrong repository targeted** -- For standard `gh` commands, use `--repo owner/repo`. For `gh api`, use the explicit path (`repos/OWNER/REPO/...`) — `--repo` does not apply to `gh api`.

## References

- [Pull Requests](references/pull-requests.md) -- Creating, reviewing, merging, and managing PRs
- [GitHub Actions](references/actions.md) -- Workflow runs, debugging failures, rerunning jobs
- [Issues](references/issues.md) -- Issue types, sub-issues, blocking relationships, and duplicate closure
- [Discussions](references/discussions.md) -- Preview `gh discussion` commands for listing, viewing, creating, and commenting
- [API Patterns](references/api-patterns.md) -- Repository contents, `gh api`, comparing commits, and operations beyond standard subcommands

## Documentation

For command-flag gaps or version conflicts, check the specific command's help. The links below cover release history and API references not captured by command help.

- [GitHub CLI releases](https://github.com/cli/cli/releases) -- Version history and release notes
- [GitHub REST API](https://docs.github.com/rest) -- REST endpoint reference for `gh api` fallbacks
- [GitHub GraphQL API](https://docs.github.com/graphql) -- GraphQL reference for data not exposed by REST or typed commands
