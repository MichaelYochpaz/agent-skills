# Repository Contents and gh api Patterns

Use `gh api` when standard `gh` subcommands lack the required data or operation. All requests are authenticated automatically. Default method is GET (read-only); adding `-f`/`-F` parameters switches the default to POST.

For known remote files or directories, prefer `gh repo read-file` / `gh repo read-dir` (preview in `gh` 2.95). Use `gh api` contents endpoints as the fallback for older `gh` versions or API-specific metadata.

Placeholder values `{owner}` and `{repo}` are auto-replaced from the current directory's repository context. Always quote API paths containing these placeholders (e.g., `"repos/{owner}/{repo}/..."`) — unquoted curly braces cause parse errors in PowerShell. For other repositories, use the explicit path (e.g., `"repos/cli/cli/..."`).

## Key Flags

- `-X, --method METHOD` -- HTTP method (`GET` default, `POST`, `PUT`, `PATCH`, `DELETE`)
- `-f, --raw-field key=value` -- String parameter
- `-F, --field key=value` -- Typed parameter (`true`/`false`/integers auto-convert; `@file` reads from file)
- `-H, --header key:value` -- HTTP header
- `--input FILE` -- Read request body from file (use `-` for stdin). Useful for complex payloads.
- `--jq EXPRESSION` -- Filter JSON response with jq syntax
- `--paginate` -- Fetch all pages of paginated results
- `--slurp` -- Combine all paginated pages into a single JSON array (use with `--paginate`)
- `--cache DURATION` -- Cache the response (e.g., `3600s`, `60m`, `1h`)
- `--silent` -- Suppress response body output (useful when only the side effect matters)
- `--verbose` -- Include full HTTP request and response in output (useful for debugging)

## Safety

- **GET requests** (default): Read-only, always safe.
- **Write requests** (`--method POST/PUT/PATCH/DELETE`, or `-f`/`-F` without `--method GET`): Modify GitHub state. Confirm with the user before executing.
- Verify the endpoint and payload before running write operations, especially on repositories you do not own.

## Repository Contents

Fetch known files or list known directories without cloning.

### Preferred: `gh repo read-file` / `read-dir`

Use these preview commands when `gh` 2.95+ is available:

```bash
# Read a file from a branch, tag, or commit
gh repo read-file README.md --repo cli/cli --ref v2.95.0

# List a directory
gh repo read-dir skills/gh --repo cli/cli --ref v2.95.0

# Parse directory entries; output is wrapped in an "entries" object
gh repo read-dir skills/gh --repo cli/cli --json name,path,type,size --jq '.entries[] | "\(.type) \(.path)"'
```

`read-file` prints file contents by default. Use `--output PATH` to write raw bytes to disk; add `--clobber` to overwrite existing files. Terminal output refuses files containing escape sequences by default; use `--allow-escape-sequences` only when you intentionally want raw terminal control sequences.

`read-dir --json` returns an object with `entries`, not a bare array: `{ "entries": [...] }`. Key entry fields: `name`, `path`, `type`, `size`, `gitSHA`, `gitType`, `modeOctal`, `submodule`.

### Fallback: REST contents API

Use the contents API when `gh repo read-file` / `read-dir` is unavailable or you need endpoint-specific metadata.

```bash
# Read a text file as raw content
gh api "repos/OWNER/REPO/contents/src/main.py?ref=main" -H "Accept: application/vnd.github.raw+json"

# List a directory
gh api "repos/OWNER/REPO/contents/src?ref=main" --jq '.[] | "\(.type) \(.name)"'
```

The raw response is plain text. `--jq` requires JSON — use it with directory listings and metadata queries. To get file metadata (`sha`, `size`, `type`) without raw content: `gh api "repos/OWNER/REPO/contents/src/main.py" --jq "{name, sha, size, type}"`.

Contents API size limits:
- Up to 1 MB: default JSON response includes base64-encoded `content`; raw media type works too.
- 1-100 MB: use raw media type (`Accept: application/vnd.github.raw+json`) or object media type; default JSON content is not returned.
- Over 100 MB: contents API is unsupported. Clone the repository or use git data APIs if you only need metadata.

Directory listings are capped at 1,000 entries. For larger directories, recursive traversal, local search, or multi-file reasoning, clone the repository to a temp directory and work locally.

### When to clone

Clone the repository to a temp directory for unknown paths, many files, local search, binary-heavy output, large files, generated diffs, or code reasoning that spans multiple files.

## PR Review Comments

Standard `gh pr view --json reviews` provides review-level summaries but lacks inline comment details (file path, line number, comment threads). Use the API for full review comment data.

### Fetch inline review comments

```bash
gh api "repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments" --jq '.[] | {id, user: .user.login, path, line, body, in_reply_to_id}'
```

Key fields:
- `id` -- Comment ID (needed for replies)
- `path` -- File path the comment is on
- `line` -- Line number in the diff
- `body` -- Comment text
- `in_reply_to_id` -- If set, this comment is a reply (use to reconstruct threads)
- `user.login` -- Author

### Filter to top-level comments only

```bash
gh api "repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments" --jq '[.[] | select(.in_reply_to_id == null)] | .[] | {id, user: .user.login, path, line, body}'
```

### Group comments into threads

```bash
gh api "repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments" --jq 'group_by(.in_reply_to_id // .id) | .[] | {thread_id: .[0].id, path: .[0].path, line: .[0].line, messages: [.[] | {user: .user.login, body}]}'
```

### Reply to a review comment

```bash
gh api --method POST "repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments/<COMMENT_ID>/replies" -f body="Reply text"
```

Use the `id` of any comment in the thread. The reply appends to the same thread.

### Submit an inline review with comments on specific lines

```bash
# Single inline comment
gh api --method POST "repos/{owner}/{repo}/pulls/<PR_NUMBER>/reviews" -f body="Overall review summary" -f event="COMMENT" -f 'comments[][path]=src/main.py' -F 'comments[][line]=42' -f 'comments[][body]=Consider renaming this variable'
```

Valid `event` values: `APPROVE`, `REQUEST_CHANGES`, `COMMENT`.

For multiple inline comments in one review:

```bash
gh api --method POST "repos/{owner}/{repo}/pulls/<PR_NUMBER>/reviews" -f body="Review summary" -f event="REQUEST_CHANGES" -f 'comments[0][path]=src/main.py' -F 'comments[0][line]=42' -f 'comments[0][body]=Fix this variable name' -f 'comments[1][path]=src/utils.py' -F 'comments[1][line]=15' -f 'comments[1][body]=Missing error handling'
```

## Comparing Commits

Compare two refs (branches, tags, commits) to see what changed between them.

```bash
# Summary (commit count and files changed)
gh api "repos/OWNER/REPO/compare/v1.0.0...v1.1.0" --jq '{total_commits: .total_commits, files_changed: (.files | length)}'

# List changed files
gh api "repos/OWNER/REPO/compare/main...feature-branch" --jq '.files[] | "\(.status) \(.filename)"'

# Commit messages between two refs
gh api "repos/OWNER/REPO/compare/v1.0.0...v1.1.0" --jq '.commits[] | "\(.sha[0:7]) \(.commit.message | split("\n") | .[0])"'
```

## Pagination

API responses are paginated (default 30 items, max 100 per page).

```bash
# Fetch all pages automatically
gh api repos/OWNER/REPO/issues --paginate --jq '.[].title'

# Merge all pages into a single array
gh api repos/OWNER/REPO/issues --paginate --slurp --jq '[.[][]] | length'

# Set per-page count
gh api 'repos/OWNER/REPO/issues?per_page=100' --paginate --jq '.[].title'
```

## Other Useful Endpoints

### Repository metadata

```bash
gh api repos/OWNER/REPO/topics --jq '.names[]'          # Topics
gh api repos/OWNER/REPO/languages                        # Languages (with byte counts)
gh api repos/OWNER/REPO/branches --jq '.[].name'         # Branches
gh api repos/OWNER/REPO/tags --jq '.[] | "\(.name) \(.commit.sha[0:7])"'  # Tags
```

### PR changed files

```bash
# Token-efficient summary (no full patches)
gh api "repos/OWNER/REPO/pulls/<PR_NUMBER>/files" --jq '.[] | "\(.status) \(.filename) +\(.additions) -\(.deletions)"'

# With patch details (can be large)
gh api "repos/OWNER/REPO/pulls/<PR_NUMBER>/files" --jq '.[] | {filename, status, additions, deletions, patch: (.patch // "binary")}'
```

### Issue/PR timeline

```bash
gh api "repos/OWNER/REPO/issues/<NUMBER>/timeline" --jq '.[] | {event, actor: .actor.login, created_at}'
```

### Rate limit

Check remaining API quota (useful when making many requests). GitHub has separate rate limit tiers: `core` (5,000/hr authenticated), `search` (~30/min authenticated, ~10/min unauthenticated), and `code_search` (~10/min, requires authentication).

```bash
gh api rate_limit --jq '.resources | {core: "\(.core.remaining)/\(.core.limit)", search: "\(.search.remaining)/\(.search.limit)", code_search: "\(.code_search.remaining)/\(.code_search.limit)", graphql: "\(.graphql.remaining)/\(.graphql.limit)"}'

# Discover all current buckets
gh api rate_limit --jq '.resources | keys'
```

## GraphQL

Use `gh api graphql` when the REST API lacks the data you need. GraphQL allows fetching exactly the fields required in a single request. Multi-line examples below use bash line continuation (`\`). In PowerShell, join into a single line or use backtick (`` ` ``).

```bash
# Fetch repository info with specific fields
gh api graphql -F owner='OWNER' -F name='REPO' -f query='
  query($owner: String!, $name: String!) {
    repository(owner: $owner, name: $name) {
      name
      description
      stargazerCount
      defaultBranchRef { name }
    }
  }
'

# Paginate GraphQL results (requires $endCursor variable and pageInfo fields)
gh api graphql --paginate -f query='
  query($endCursor: String) {
    viewer {
      repositories(first: 100, after: $endCursor) {
        nodes { nameWithOwner }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
'
```

## Documentation

- [REST repository contents API](https://docs.github.com/en/rest/repos/contents) -- Contents endpoint behavior, media types, and size limits
- [REST pull request review comments](https://docs.github.com/en/rest/pulls/comments) -- Inline PR review comments and replies
- [REST rate limit API](https://docs.github.com/en/rest/rate-limit/rate-limit) -- Rate-limit resource buckets
- [GitHub GraphQL API](https://docs.github.com/graphql) -- GraphQL schema and query patterns
