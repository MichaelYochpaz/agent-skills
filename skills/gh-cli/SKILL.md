---
name: gh-cli
description: GitHub CLI (gh) for interacting with GitHub from the command line. Covers repositories, issues, pull requests, releases, Actions, code search, and the GitHub REST/GraphQL API. Use when performing any GitHub-related operation, or when looking up code examples and implementation patterns in remote repositories.
---

# GitHub CLI (`gh`)

Interact with GitHub from the command line: repositories, releases, issues, PRs, search, code review, and Actions.

## Agent Guidelines

- When a task requires searching across files or exploring unfamiliar code where paths aren't known upfront, clone to a temp directory (`gh repo clone owner/repo <temp-dir> -- --depth 1`) and use local file-reading and search tools. For quick reads of specific known files, use the API with raw media type; see [API Patterns](references/api-patterns.md). When exploring via API, list directories before reading files: `gh api "repos/OWNER/REPO/contents/src" --jq '.[] | "\(.type) \(.name)"'`.
- Prefer default text output over `--json` for reading/viewing — it is more token-efficient. Use `--json` with `--jq` only when extracting specific fields programmatically.
- When viewing logs or diffs, scope output first (e.g., `--name-only`, `--log-failed`) before fetching full content.
- The `--repo` flag is unnecessary when running inside a cloned repository — the current directory's repo is used by default. For `gh api`, use the explicit path (`repos/OWNER/REPO/...`) or set the `GH_REPO` environment variable.
- When unsure about available flags for a `gh` subcommand, run `gh <command> <subcommand> --help` rather than guessing flag names.

## Safety

- **Write operations** (`create`, `comment`, `review`, `close`, `merge`, `delete`, `rerun`) modify GitHub state. Confirm with the user before executing, especially on repositories you do not own.
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

These flags are available on most commands across all command groups:

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

### Read a remote file

For quick single-file reads without cloning, use the raw media type to get plain text directly:

```bash
gh api "repos/OWNER/REPO/contents/path/to/file" -H "Accept: application/vnd.github.raw+json"
```

Append `?ref=BRANCH` to target a specific branch. For multi-file exploration, clone instead (see Agent Guidelines). For directory listings and additional patterns, see [API Patterns](references/api-patterns.md).

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

JSON fields: `tagName`, `name`, `publishedAt`, `createdAt`, `isLatest`, `isDraft`, `isPrerelease`, `isImmutable`

### View (changelog, assets)

Display a release's changelog body, tag, assets, and metadata. Omit the tag to view the latest release.

```bash
gh release view --repo owner/repo                         # Latest release
gh release view v1.2.0 --repo owner/repo                  # Specific tag
gh release view v1.2.0 --json tagName,body,assets,publishedAt
```

JSON fields: `tagName`, `name`, `body`, `assets`, `author`, `publishedAt`, `createdAt`, `databaseId`, `id`, `isDraft`, `isPrerelease`, `isImmutable`, `targetCommitish`, `tarballUrl`, `zipballUrl`, `url`

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

JSON fields: `number`, `title`, `state`, `stateReason`, `author`, `labels`, `assignees`, `body`, `closed`, `closedAt`, `closedByPullRequestsReferences`, `comments`, `createdAt`, `updatedAt`, `id`, `isPinned`, `milestone`, `projectItems`, `reactionGroups`, `url`

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
gh issue reopen 123
```

Close reasons: `completed` (default), `not planned`.

### Status

Show a summary of issues relevant to you: assigned to you, mentioning you, and opened by you.

```bash
gh issue status
```

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

Key JSON fields: `number`, `title`, `state`, `author`, `headRefName`, `baseRefName`, `labels`, `reviewDecision`, `isDraft`, `additions`, `deletions`, `changedFiles`, `mergedAt`, `mergedBy`, `url`, `statusCheckRollup`, `files`, `commits`, `reviews`, `createdAt`, `updatedAt`

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

## Search

Search across all of GitHub for issues, PRs, code, commits, and repositories. All search commands support `--owner`, `--limit`, `--json`, and `--jq`. Most also support `--repo` (except `gh search repos`). All search subcommands except `gh search code` support `--order {asc|desc}` (default: `desc`), used with `--sort`.

For the full search query syntax, see the [GitHub search docs](https://docs.github.com/search-github/searching-on-github). For flags specific to each subcommand, run `gh search <subcommand> --help`.

**Rate limits:** Search APIs have stricter rate limits than the core API. Code search is the most restrictive (~10/min authenticated; requires authentication). Other search commands allow ~30/min authenticated or ~10/min unauthenticated. Check current quota with `gh api rate_limit --jq '.resources | {search, code_search}'`.

**When to clone instead:** See Agent Guidelines for when to clone vs. use the API.

**Reconnaissance:** When searching an unfamiliar repository, check its primary language first to select correct `--extension` and `--language` values:

```bash
gh repo view owner/repo --json primaryLanguage --jq '.primaryLanguage.name'
```

### Issues

Search for issues across repositories using keywords, labels, state, or GitHub search syntax.

```bash
gh search issues "error handling" --repo owner/repo
gh search issues --label bug --state open --assignee @me
gh search issues --involves username --comments ">10" --repo owner/repo
```

Flags:
- `--state STRING` -- `open` (default) or `closed`
- `--label STRINGS` -- Filter by label (repeat for multiple)
- `--assignee STRING` / `--author STRING` -- Filter by assignee or author (`@me` for self)
- `--involves USER` / `--mentions USER` / `--commenter USER` -- Filter by user involvement
- `--comments NUMBER` -- Filter by comment count (e.g., `">10"`)
- `--match STRINGS` -- Restrict search to: `title`, `body`, `comments`
- `--sort STRING` -- Sort by: `comments`, `created`, `updated`, `reactions`, `interactions` (default: `best-match`)
- `--include-prs` -- Include pull requests in results

JSON fields: `assignees`, `author`, `body`, `closedAt`, `commentsCount`, `createdAt`, `id`, `labels`, `number`, `repository`, `state`, `title`, `updatedAt`, `url`

### PRs

Search for pull requests across repositories. Supports filtering by author, review status, merge state, and draft status.

```bash
gh search prs "refactor" --repo owner/repo
gh search prs --review-requested @me --state open
gh search prs --author username --merged --repo owner/repo
```

Flags:
- `--state STRING` -- `open` (default) or `closed` (not `merged` — use `--merged` separately)
- `--merged` / `--draft` -- Filter by merge or draft status
- `--author STRING` / `--assignee STRING` -- Filter by author or assignee (`@me` for self)
- `--label STRINGS` -- Filter by label
- `--review STRING` -- Filter by review status: `none`, `required`, `approved`, `changes_requested`
- `--review-requested USER` / `--reviewed-by USER` -- Filter by reviewer
- `--base BRANCH` / `--head BRANCH` (-B/-H) -- Filter by base or head branch
- `--checks STRING` -- Filter by CI status: `pending`, `success`, `failure`
- `--match STRINGS` -- Restrict search to: `title`, `body`, `comments`
- `--sort STRING` -- Sort by: `comments`, `created`, `updated`, `reactions`, `interactions` (default: `best-match`)

JSON fields: `assignees`, `author`, `body`, `closedAt`, `commentsCount`, `createdAt`, `id`, `isDraft`, `labels`, `number`, `repository`, `state`, `title`, `updatedAt`, `url`

### Code

Search within file contents across GitHub repositories. Returns matching lines only (no line numbers, no surrounding context). Useful for locating files containing a pattern, but follow up with file reads or clone the repo to understand code logic.

**Limitations:** Uses a legacy search engine (results may not match github.com). Only searches the default branch. Only files under 384 KB are indexed. Every query must include at least one search term (qualifier-only searches like `--extension ts` alone will fail). Does not support `--sort` or `--order` — results are always ranked by relevance.

```bash
gh search code "functionName" --repo owner/repo
gh search code "createServer" --repo owner/repo --extension ts
gh search code "lint" --repo owner/repo --filename package.json
```

Flags:
- `--extension STRING` -- Filter by file extension (without dot: `ts`, `py`, `go`)
- `--filename STRING` -- Filter by filename (e.g., `package.json`, `Makefile`)
- `--language STRING` -- Filter by GitHub-detected language (e.g., `typescript`, `python`)
- `--match VALUE` -- Restrict where search terms are matched: `file` (content only) or `path` (file path only). Default: both. Note: `--match path` matches terms against path text — it does not filter by directory.
- `--owner STRINGS` -- Filter by repository owner (searches all repos of that owner)
- `--repo STRINGS` (-R) -- Filter by specific repository (`owner/repo`)
- `--size RANGE` -- Filter by file size in kilobytes (e.g., `>100`, `<50`)

JSON fields: `path`, `repository`, `sha`, `textMatches`, `url`

The `textMatches` field provides fragment context with character-level match positions — use `--json path,textMatches` when you need more context than the default text output provides.

### Commits

Search commits by message text, author, committer date, or hash.

```bash
gh search commits "fix bug" --repo owner/repo
gh search commits --author username --committer-date ">2024-01-01"
gh search commits --hash abc1234
```

Flags:
- `--author STRING` / `--committer STRING` -- Filter by author or committer login
- `--author-date DATE` / `--committer-date DATE` -- Filter by date (e.g., `">2024-01-01"`, `"2024-01-01..2024-06-01"`)
- `--author-name STRING` / `--author-email STRING` -- Filter by git author name or email
- `--hash STRING` -- Filter by commit SHA
- `--merge` -- Filter to merge commits only
- `--sort STRING` -- Sort by: `author-date`, `committer-date` (default: `best-match`)

JSON fields: `author`, `commit`, `committer`, `id`, `parents`, `repository`, `sha`, `url`

### Repositories

Search for repositories by keyword, language, topic, stars, license, or owner. Note: `--repo` is not available on this subcommand — use `--owner` to filter by owner.

```bash
gh search repos "keyword" --language python --sort stars --order desc
gh search repos --topic cli --stars ">1000" --language go
```

Flags:
- `--language STRING` -- Filter by primary language
- `--topic STRINGS` -- Filter by topic (repeat for multiple)
- `--stars NUMBER` -- Filter by star count (e.g., `">1000"`, `"100..500"`)
- `--forks NUMBER` -- Filter by fork count
- `--license STRINGS` -- Filter by license (e.g., `mit`, `apache-2.0`)
- `--created DATE` / `--updated DATE` -- Filter by date (e.g., `">2024-01-01"`)
- `--match STRINGS` -- Restrict search to: `name`, `description`, `readme`
- `--sort STRING` -- Sort by: `stars`, `forks`, `updated`, `help-wanted-issues` (default: `best-match`)
- `--include-forks STRING` -- Include forks: `false` (default), `true`, `only`
- `--visibility STRINGS` -- Filter: `public`, `private`, `internal`

JSON fields: `createdAt`, `defaultBranch`, `description`, `forksCount`, `fullName`, `id`, `language`, `license`, `name`, `openIssuesCount`, `owner`, `stargazersCount`, `updatedAt`, `url`, `visibility`

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

## Troubleshooting

- **Not authenticated** -- Run `gh auth login` to authenticate. Verify with `gh auth status`.
- **Rate limited** -- Check quota with `gh api rate_limit --jq '.rate | "\(.remaining)/\(.limit)"'`. Code search is the most restrictive (~10/min).
- **404 on file read** -- Verify the path exists by listing the parent directory first: `gh api "repos/OWNER/REPO/contents/src" --jq '.[].name'`.
- **Wrong repository targeted** -- For standard `gh` commands, use `--repo owner/repo`. For `gh api`, use the explicit path (`repos/OWNER/REPO/...`) — `--repo` does not apply to `gh api`.

## References

- [Pull Requests](references/pull-requests.md) -- Creating, reviewing, merging, and managing PRs
- [GitHub Actions](references/actions.md) -- Workflow runs, debugging failures, rerunning jobs
- [API Patterns](references/api-patterns.md) -- `gh api` for file contents, comparing commits, and operations beyond standard subcommands
