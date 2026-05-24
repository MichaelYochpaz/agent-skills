---
name: acli-jira
description: >-
  Atlassian CLI (acli) for Jira Cloud. View issues, search with JQL, navigate
  issue hierarchy (parents, children, epic contents), read comments, list
  attachments and links, and modify issues (comment, transition, edit, assign,
  link, create). Use when the user mentions Jira tickets, issues, stories,
  epics, bugs, tasks, spikes, JQL queries, or references a Jira issue key (e.g.,
  "PROJ-123"). Also use for sprint context, board queries, or any Jira
  Cloud interaction.
---

# Atlassian CLI -- Jira (`acli jira`)

Interact with Jira Cloud from the command line: view and search issues, navigate issue hierarchy, read comments, and update issue state.

Verified with `acli` 1.3.18.

## Agent Guidelines

- For `search`, `board search`, `board list-sprints`, and `sprint list-workitems`: use `--csv` for compact, complete output. Default table output wastes tokens on box-drawing characters and may truncate values.
- For `view`: default text output is the most token-efficient option. Use `--json` only when extracting specific field values programmatically (e.g., parent key).
- For `comment list`, `link list`, and `attachment list`: use `--json` for compact output. Default table output inflates size 3-5x with box-drawing characters and padding.
- Scope `view` output with `--fields` to request only the fields you need. The default fields (`key,issuetype,summary,status,assignee,description`) cover most read scenarios.
- For hierarchy traversal, use JQL search to find children in bulk rather than viewing individual issues one at a time.
- For multiple issues, use `search --jql "key in (KEY-1, KEY-2)"` instead of separate `view` calls.
- For formatted descriptions and comments (headings, lists, code blocks, tables), use ADF JSON — the only format Jira renders for rich text. See the [ADF Formatting](references/adf-formatting.md) reference. Plain text is fine for simple updates.

## Safety

Write operations modify Jira state — confirm with the user before executing. Mutation commands include `comment create/update/delete`, `transition`, `edit`, `assign`, `workitem create`, `link create/delete`.

## Prerequisites

Verify `acli` is installed and authenticated:

```bash
acli --version
acli jira auth status
```

If not authenticated, guide the user through `acli jira auth login`.

## Common Flags

Available across most subcommands:

- `--json` -- JSON output (see Agent Guidelines for when to use)
- `--csv` -- CSV output; preferred format for agents when available (on `search`, `board search`, `board list-sprints`, `sprint list-workitems`)
- `--fields FIELDS` -- Comma-separated field list to include in output
- `--jql QUERY` -- JQL filter (on `search`, `edit`, `assign`, `transition`)
- `--filter ID` -- Use a saved Jira filter instead of `--jql` (on `search`, `edit`, `assign`, `transition`)
- `--limit N` -- Maximum results to return
- `--paginate` -- Fetch all pages (ignores `--limit`)
- `--yes` -- Skip confirmation prompts (on `edit`, `assign`, `transition`, `link delete`)
- `--web` -- Open in browser instead of terminal

## Viewing Issues

View an issue with default fields (key, type, summary, status, assignee, description):

```bash
acli jira workitem view PROJ-123
```

### Scoping Fields

Use `--fields` to request specific fields or reduce output:

```bash
# Only summary and status
acli jira workitem view PROJ-123 --fields summary,status

# All available fields
acli jira workitem view PROJ-123 --fields '*all'

# All navigable fields
acli jira workitem view PROJ-123 --fields '*navigable'

# Default fields minus description (quick status check)
acli jira workitem view PROJ-123 --fields '-description'

# Metadata for context: parent, priority, labels, components, version
acli jira workitem view PROJ-123 --fields 'summary,status,priority,parent,labels,components,fixVersions'
```

### JSON Output

Use `--json` for structured data when you need to extract specific field values:

```bash
acli jira workitem view PROJ-123 --fields 'parent,summary,status' --json
```

The JSON response contains top-level keys `key`, `fields`, `id`, and others. Field values are under `fields`.

## Navigating Issue Hierarchy

### Parent

Extract the parent from `view` output. Text output shows the parent key directly when the issue has one. For reliable programmatic extraction, use JSON:

```bash
acli jira workitem view PROJ-123 --fields parent --json
```

To walk the full parent chain (Story -> Epic -> Feature -> Initiative), repeat: extract parent key, view that parent, until no parent exists.

### Children and Subtasks

Use JQL search to find child issues:

```bash
# Subtasks and direct children
acli jira workitem search --jql "parent = PROJ-123" --fields "key,summary,status,issuetype" --csv

# Ordered by status
acli jira workitem search --jql "parent = PROJ-123 ORDER BY status" --fields "key,summary,status,issuetype" --csv
```

For epics in classic Jira projects, children may use the legacy "Epic Link" field instead of `parent`:

```bash
acli jira workitem search --jql "'Epic Link' = PROJ-100" --fields "key,summary,status,issuetype" --csv
```

### Issue Links

List all links (blocks, is blocked by, relates to, clones, etc.):

```bash
acli jira workitem link list --key PROJ-123 --json
```

List available link types on the instance:

```bash
acli jira workitem link type
```

## Searching Issues

```bash
acli jira workitem search --jql "project = PROJ AND status = 'In Progress'" --fields "key,summary,assignee,status" --csv
```

### Count Only

Get the number of matching issues without fetching details:

```bash
acli jira workitem search --jql "project = PROJ AND issuetype = Bug AND status != Done" --count
```

### Pagination

Default limit is 50 results. Use `--limit` for a specific count or `--paginate` for all results:

```bash
# First 10 results
acli jira workitem search --jql "project = PROJ" --limit 10 --csv

# All results (automatic pagination)
acli jira workitem search --jql "project = PROJ AND sprint in openSprints()" --paginate --csv
```

### Field Support

`search --fields` supports: `key`, `summary`, `status`, `issuetype`, `assignee`, `priority`, `description`, `labels`, `reporter`. Other fields (e.g., `updated`, `created`, `parent`, `components`, `fixVersions`, `resolution`, `sprint`) return "field not allowed" errors. Use `view` to access these fields on individual issues, or JQL `ORDER BY` for date-based sorting.

### Common JQL Patterns

For constructing queries beyond these patterns, see the [JQL Reference](references/jql-reference.md).

- **Assigned to me**: `project = PROJ AND assignee = currentUser()`
- **Open issues**: `project = PROJ AND statusCategory != Done`
- **Issues by type**: `project = PROJ AND issuetype = Story`
- **Current sprint**: `project = PROJ AND sprint in openSprints()`
- **Recently updated**: `project = PROJ AND updated >= -7d ORDER BY updated DESC`
- **Unassigned**: `project = PROJ AND assignee is EMPTY`
- **By label**: `project = PROJ AND labels = "my-label"`
- **Children of issue**: `parent = PROJ-123`
- **Epic children (classic, legacy)**: `"Epic Link" = PROJ-100` — use `parent` for new queries
- **Text search**: `project = PROJ AND text ~ "dependency conflict"`
- **By component**: `project = PROJ AND component = "build-system"`
- **Multiple specific issues**: `key in (PROJ-100, PROJ-200, PROJ-300)`

## Comments

### List Comments

```bash
acli jira workitem comment list --key PROJ-123 --json

# Latest 5 comments
acli jira workitem comment list --key PROJ-123 --limit 5 --json

# Oldest first
acli jira workitem comment list --key PROJ-123 --order "+created" --json
```

### Add a Comment

```bash
acli jira workitem comment create --key PROJ-123 --body "Investigation complete. Root cause: constraint resolver selects incompatible version."
```

To update or delete comments, see [Write Operations](references/write-operations.md#comments).

## Attachments

### List Attachments

```bash
acli jira workitem attachment list --key PROJ-123 --json
```

### Download an Attachment

`acli` lists attachments but cannot download them. Use the bundled script with the attachment's `content` URL from issue metadata:

```bash
# Step 1: Get attachment metadata with content URLs
acli jira workitem view PROJ-123 --fields attachment --json
# → fields.attachment[].content contains the download URL

# Step 2: Download
uv run scripts/download-attachment.py <content_url> -o <output_path>
```

Requires `JIRA_API_TOKEN` environment variable. Site and email are auto-detected from acli profiles (tries current profile first, then others). Use `--site` to target a specific site.

## Advanced: Fields via JSON

Custom fields and deeply nested metadata are only accessible through JSON output:

```bash
# All fields as JSON
acli jira workitem view PROJ-123 --fields '*all' --json
```

Useful fields in JSON output under `fields`:
- `parent` -- Parent issue key and summary
- `subtasks` -- List of subtask objects
- `issuelinks` -- Linked issues with link type and direction
- `comment` -- Comment data (prefer `comment list` for readability)
- `attachment` -- Attachment metadata including content URLs
- `worklog` -- Time tracking / work log entries
- `components`, `fixVersions`, `labels` -- Categorization fields
- `created`, `updated`, `resolutiondate` -- Timestamps
- `customfield_*` -- Custom fields (IDs vary by instance)

## Known Limitations

Use the Jira REST API directly for features `acli` does not expose:

- **Components and Fix Versions on edit** -- `acli edit` does not support `components` or `fixVersions`. Set them via `additionalAttributes` on [create](references/write-operations.md#setting-components-and-fix-versions), or the [REST API fallback](#rest-api-fallback) for existing issues.
- **Remote links** -- External links (GitLab MRs, GitHub PRs) are served from a separate endpoint (`/rest/api/3/issue/{key}/remotelink`) that `acli` does not call. They are not included in `--fields '*all' --json` output.
- **Changelog / issue history** -- Field change history requires the `expand=changelog` parameter, which `acli` does not support. The `changelog` field in JSON output is always `null`.
- **Attachment download** -- `acli` lists attachments but cannot download them. See [Attachments](#attachments).

## REST API Fallback

When `acli` does not support a write operation, use the Jira REST API with basic auth. Requires `JIRA_API_TOKEN` environment variable. Extract the site and email from `acli jira auth status`:

```bash
# Get site and email
acli jira auth status
# → Site: example.atlassian.net
# → Email: user@example.com

# Set fields on an existing issue (e.g., components, fixVersions)
curl -s -X PUT \
  "https://<site>/rest/api/3/issue/PROJ-123" \
  -u "<email>:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fields":{"components":[{"name":"Component Name"}]}}'
```

## Troubleshooting

- **Not authenticated** -- Run `acli jira auth login` to authenticate. In CI, verify `JIRA_API_TOKEN` is set and acli is configured.
- **Issue not found (404)** -- Verify the issue key is correct and includes the project prefix (e.g., `PROJ-123` not `123`).
- **Permission denied (403)** -- The authenticated user lacks access to the project or issue. Ask the user to verify their permissions.
- **Invalid transition** -- The target status is not reachable from the current status. View the issue to check its current status, then use a valid transition.
- **JQL syntax error** -- Check quoting: field names with spaces need single quotes (`'Epic Link'`), string values need double quotes (`"In Progress"`). See [JQL Reference](references/jql-reference.md) for full syntax rules.

## References

- [Write Operations](references/write-operations.md) -- Create, edit, transition, assign, and link issues
- [ADF Formatting](references/adf-formatting.md) -- Rich text formatting (headings, lists, code, tables, panels) for descriptions and comments
- [Sprints & Boards](references/sprint-and-boards.md) -- Find boards, list sprints, view sprint work items
- [JQL Reference](references/jql-reference.md) -- Syntax rules, operators, functions, and field guidance for constructing JQL queries

## Documentation

- [Atlassian CLI command reference](https://developer.atlassian.com/cloud/acli/reference/commands/jira/) -- Official `acli jira` command tree
- [acli jira workitem](https://developer.atlassian.com/cloud/acli/reference/commands/jira-workitem/) -- Work item command family
- [Jira Cloud REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/) -- REST API overview and authentication patterns
