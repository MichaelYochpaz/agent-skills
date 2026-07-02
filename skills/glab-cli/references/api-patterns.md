# API Patterns

Use `glab api` when standard subcommands lack the required data or operation. All requests are authenticated automatically. Default method is GET (read-only); adding `--field`, `--raw-field`, or `--form` parameters switches the default to POST.

`glab api` has no `--jq` flag — pipe to external `jq` for filtering. No `--slurp` flag — paginated results are auto-merged into a single array. Use `--output ndjson` to stream array elements as individual JSON lines for efficient `jq` processing.

## Key Flags

- `--method METHOD` (`-X`) -- HTTP method (`GET` default, `POST`, `PUT`, `PATCH`, `DELETE`)
- `--field KEY=VALUE` (`-F`) -- Typed parameter (booleans/integers auto-convert; `@file` reads file; endpoint placeholders expanded in values). **`-F` means `--field` here, not `--output`.**
- `--raw-field KEY=VALUE` (`-f`) -- String parameter (no type conversion)
- `--form KEY=VALUE` -- Multipart form field; use `file=@path` for file uploads or `file=@-` for stdin. Mutually exclusive with `--field`, `--raw-field`, and `--input`. Requires `glab` v1.91.0+.
- `--input FILE` -- Raw request body from file (`-` for stdin)
- `--header KEY:VALUE` (`-H`) -- Additional HTTP header
- `--include` (`-i`) -- Show response headers
- `--output VALUE` -- `json` (default, pretty-printed) or `ndjson` (streams array elements as individual lines)
- `--paginate` -- Fetch all pages. REST: follows `Link` header, auto-sets `per_page=100`, GET only. GraphQL: requires `$endCursor` pattern, POST allowed.
- `--silent` -- Suppress response body
- `--hostname HOST` -- Override GitLab instance for this request

## Safety

- **GET requests** (default): Read-only, always safe.
- **Write requests** (`--method POST/PUT/PATCH/DELETE`): Modify GitLab state. Confirm with the user before executing.
- Adding `--field`, `--raw-field`, or `--form` switches the default method to POST. Use explicit `--method GET` when passing field parameters to a GET endpoint.

## Endpoint Placeholders

Placeholders are auto-populated from the current Git context:

- `:id` -- Numeric project ID (resolved via API call)
- `:fullpath` -- URL-encoded `group/subgroup/project` (e.g., `gitlab-org%2Fcli`)
- `:group/:namespace/:repo` -- Same as `:fullpath`
- `:namespace/:repo` -- URL-encoded `namespace/project`
- `:group` -- Top-level group name
- `:namespace` -- Namespace portion
- `:repo` -- Project name only
- `:user` / `:username` -- Authenticated user (resolved via API call)
- `:branch` -- Current Git branch

Placeholders also work inside `--field` values (auto-expanded).

## Request Bodies

### Scalar Parameters

Use `--raw-field` for literal string parameters. Use `--field` when you need type conversion (`true`, `false`, `null`, integers), placeholder expansion, or `@file` value reads.

Neither flag parses nested JSON arrays or objects; those values are sent as strings. Use `--input` for raw JSON bodies:

```bash
glab api projects/:fullpath/protected_branches/main --method PATCH \
  --header "Content-Type: application/json" \
  --input payload.json
```

### Multipart Uploads

Use `--form` for endpoints that require `multipart/form-data`, such as wiki attachment uploads:

```bash
glab api --method POST projects/:fullpath/wikis/attachments --form "file=@./image.png" --form "branch=main"
```

Do not combine `--form` with `--field`, `--raw-field`, or `--input`.

### Project Path Encoding

`:fullpath` handles URL-encoding automatically in current `glab` versions; that behavior was fixed in v1.102.0. For manual paths or older `glab` versions, encode `/` as `%2F`:

```bash
# Automatic (recommended)
glab api projects/:fullpath/issues

# Manual encoding
glab api projects/my-group%2Fmy-project/issues
```

## Pagination

### REST

API responses are paginated (default 20 items, max 100 per page). Use `--paginate` to fetch all pages — results are auto-merged into a single JSON array.

```bash
glab api projects/:fullpath/issues --paginate | jq '.[].title'
glab api 'projects/:fullpath/issues?per_page=100' | jq length
glab api projects/:fullpath/issues --paginate --output ndjson | jq 'select(.state == "opened") | .title'
```

### GraphQL

GraphQL pagination requires a `$endCursor: String` variable and `pageInfo { hasNextPage, endCursor }` in the query:

```bash
glab api graphql --paginate --raw-field query='
  query($endCursor: String) {
    project(fullPath: "group/project") {
      issues(first: 100, after: $endCursor) {
        nodes { title state }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
'
```

## Common Endpoints

### Read a file

```bash
glab api projects/:fullpath/repository/files/path%2Fto%2Ffile.py/raw --method GET --raw-field ref=main
```

File paths in the URL must be URL-encoded (`/` → `%2F`).

### List a directory

```bash
glab api 'projects/:fullpath/repository/tree?path=src&ref=main' | jq '.[] | "\(.type) \(.name)"'
```

### MR changed files

Workaround for the missing `mr diff --name-only`:

```bash
# File paths only
glab api projects/:fullpath/merge_requests/123/diffs | jq '.[].new_path'

# Summary with status
glab api projects/:fullpath/merge_requests/123/diffs | jq '.[] | "\(.renamed_file // .new_file | if . then "A" else "M" end) \(.new_path)"'
```

### MR discussions

Prefer `glab mr note` for common MR discussion operations (list, create, reply, resolve, reopen). Use the discussions API only when you need fields or operations not exposed by `mr note`.

Fetch discussion threads on a merge request:

```bash
glab api projects/:fullpath/merge_requests/123/discussions | jq '.[] | {id, notes: [.notes[] | {author: .author.username, body}]}'
```

For inline review comments, prefer `glab mr note create --file --line`. Hand-built API `position[...]` payloads can fail position validation and fall back to general comments depending on server behavior.

### Project metadata

```bash
glab api projects/:fullpath | jq '{name, default_branch, visibility, web_url}'
glab api projects/:fullpath/languages
glab api projects/:fullpath/repository/branches | jq '.[].name'
glab api projects/:fullpath/repository/tags | jq '.[] | "\(.name) \(.commit.short_id)"'
```

## GraphQL

Use `glab api graphql` when the REST API lacks the data you need. All `--field`/`--raw-field` parameters except `query` and `operationName` are auto-grouped into a `variables` object.

```bash
glab api graphql --raw-field query='
  query {
    project(fullPath: "group/project") {
      name
      description
      repository { rootRef }
    }
  }
'
```

With variables:

```bash
glab api graphql --raw-field query='
  query($fullPath: ID!) {
    project(fullPath: $fullPath) {
      name
      mergeRequests(state: opened, first: 10) {
        nodes { iid title state }
      }
    }
  }
' --raw-field fullPath="group/project"
```

The endpoint path `graphql` is auto-detected and routed to `/api/graphql`.

## Self-Managed Instances

Use `--hostname` to target a specific instance for API requests:

```bash
glab api projects/:fullpath/issues --hostname gitlab.example.com
```

## Documentation

- [GitLab CLI documentation](https://docs.gitlab.com/cli/) -- CLI command reference
- [REST API reference](https://docs.gitlab.com/api/rest/) -- Endpoints, parameters, and response schemas
- [GraphQL API reference](https://docs.gitlab.com/api/graphql/) -- Schema explorer and query documentation
