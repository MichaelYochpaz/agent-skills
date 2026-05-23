# gh api Patterns

Use `gh api` when standard `gh` subcommands lack the required data or operation. All requests are authenticated automatically. Default method is GET (read-only); adding `-f`/`-F` parameters switches the default to POST.

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
- **Write requests** (`--method POST/PUT/PATCH/DELETE`): Modify GitHub state. Confirm with the user before executing.
- Verify the endpoint and payload before running write operations, especially on repositories you do not own.

## File Contents

Fetch files from a remote repository without cloning.

### Read a text file

Use the raw media type to get file contents directly:

```bash
gh api "repos/OWNER/REPO/contents/path/to/file.py" -H "Accept: application/vnd.github.raw+json"

# From a specific ref (branch, tag, or commit SHA)
gh api "repos/OWNER/REPO/contents/path/to/file.py?ref=develop" -H "Accept: application/vnd.github.raw+json"
```

The raw response is plain text. `--jq` requires JSON — use it with directory listings and metadata queries.

Supports files up to 100 MB. For larger files or multi-file exploration, clone the repository.

To get file metadata (`sha`, `size`, `type`) without content: `gh api "repos/OWNER/REPO/contents/path" --jq "{name, sha, size, type}"`

### List a directory

```bash
gh api "repos/OWNER/REPO/contents/src" --jq '.[] | "\(.type) \(.name)"'
```

Append `?ref=BRANCH` to target a specific branch.

### When to clone vs. use the API

For multi-file exploration or searching, clone the repository to a temp directory and work locally (see Agent Guidelines in the main skill body). Use the API for quick reads of specific known files under 100 MB.

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
gh api rate_limit --jq '.rate | "\(.remaining)/\(.limit)"'
gh api rate_limit --jq '.resources | {core: "\(.core.remaining)/\(.core.limit)", search: "\(.search.remaining)/\(.search.limit)", code_search: "\(.code_search.remaining)/\(.code_search.limit)"}'
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
