# Write Operations

Commands that modify Jira state. Confirm with the user before executing. Use `--yes` to skip confirmation prompts in pre-approved automation (available on `edit`, `assign`, `transition`, `link delete`). Comment commands (`comment create`, `comment update`, `comment delete`) execute without prompting.

## Formatting

The `--body`, `--body-file`, `--description`, and `--description-file` flags accept **plain text** or **[ADF JSON](adf-formatting.md)**. `acli` auto-detects the format (valid JSON is treated as ADF; everything else is plain text). Plain markdown syntax produces literal text — use ADF for any formatting beyond plain text.

- **Plain text** for short updates: `--body "Fixed in commit abc123."`
- **ADF JSON** for structured content (headings, lists, code blocks, tables, panels): `--body-file report.json`

See the [ADF Formatting](adf-formatting.md) reference for syntax and examples.

## Assign

```bash
# Self-assign
acli jira workitem assign --key PROJ-123 --assignee "@me"

# Assign to a specific user
acli jira workitem assign --key PROJ-123 --assignee "user@redhat.com"

# Assign to project default
acli jira workitem assign --key PROJ-123 --assignee "default"

# Remove assignee
acli jira workitem assign --key PROJ-123 --remove-assignee

# Assign multiple issues
acli jira workitem assign --key "PROJ-123,PROJ-456" --assignee "@me" --yes

# Assign by JQL query
acli jira workitem assign --jql "project = PROJ AND labels = needs-owner" --assignee "@me" --yes
```

## Transition Status

Move an issue to a different status. The target status must be a valid transition from the current status.

```bash
acli jira workitem transition --key PROJ-123 --status "In Progress"
acli jira workitem transition --key PROJ-123 --status "Done"

# Transition multiple issues
acli jira workitem transition --key "PROJ-123,PROJ-456" --status "Done" --yes

# Transition by JQL
acli jira workitem transition --jql "project = PROJ AND assignee = currentUser() AND status = 'In Review'" --status "Done" --yes
```

## Edit Fields

Update issue metadata. Multiple fields can be edited in a single call.

```bash
# Edit summary
acli jira workitem edit --key PROJ-123 --summary "Updated summary"

# Edit description (plain text)
acli jira workitem edit --key PROJ-123 --description "New description text"

# Edit description from file (plain text or ADF JSON)
acli jira workitem edit --key PROJ-123 --description-file description.txt

# Add labels
acli jira workitem edit --key PROJ-123 --labels "reviewed,priority"

# Remove labels
acli jira workitem edit --key PROJ-123 --remove-labels "old-label"

# Change issue type
acli jira workitem edit --key PROJ-123 --type "Bug"

# Combine multiple edits
acli jira workitem edit --key PROJ-123 --summary "Fixed title" --labels "reviewed" --assignee "@me" --yes

# Edit multiple issues by JQL
acli jira workitem edit --jql "project = PROJ AND labels = stale" --labels "archived" --yes
```

**Supported fields:** `summary`, `description`, `labels`, `type`, `assignee`. Fields like `components` and `fixVersions` require the [REST API fallback](../SKILL.md#rest-api-fallback).

## Create Issues

```bash
# Create a task
acli jira workitem create --project PROJ --type Task --summary "Investigate build failure" --assignee "@me"

# Create with description
acli jira workitem create --project PROJ --type Story --summary "Add caching layer" --description "Implement Redis caching for API responses" --label "enhancement"

# Create as child of existing issue (child type must be valid for the parent's hierarchy level)
acli jira workitem create --project PROJ --type Sub-task --summary "Subtask title" --parent PROJ-123

# Read description from file
acli jira workitem create --project PROJ --type Bug --summary "Bug title" --description-file details.txt

# Read summary and description from file (first line = summary, remaining lines = description)
acli jira workitem create --project PROJ --type Bug --from-file issue.txt

# Create with JSON for complex field configuration
acli jira workitem create --generate-json  # generates template
acli jira workitem create --from-json workitem.json
```

Issue types: `Epic`, `Story`, `Task`, `Sub-task`, `Bug`, `Spike`.

### Setting Components and Fix Versions

CLI flags for `components` and `fixVersions` are not available on `create`. Use `--from-json` with `additionalAttributes` to set these fields at creation time:

```json
{
  "projectKey": "PROJ",
  "type": "Task",
  "summary": "Issue title",
  "additionalAttributes": {
    "components": [{"name": "Component Name"}],
    "fixVersions": [{"name": "1.0"}]
  }
}
```

```bash
acli jira workitem create --from-json workitem.json
```

`additionalAttributes` accepts any Jira field key, including custom fields (`customfield_*`). Component and version names must already exist in the project.

**Note:** `additionalAttributes` is only supported on `create`, not `edit`. To set these fields on existing issues, use the [REST API fallback](../SKILL.md#rest-api-fallback).

## Link Issues

```bash
# List available link types
acli jira workitem link type

# Create a link (outward "blocks" inward)
acli jira workitem link create --out PROJ-123 --in PROJ-456 --type "Blocks"

# List existing links (use --json to extract link IDs)
acli jira workitem link list --key PROJ-123 --json

# Delete a link by ID (get LINK_ID from link list --json output)
acli jira workitem link delete --id LINK_ID --yes
```

Common link types: `Blocks` / `is blocked by`, `Cloners` / `is cloned by`, `Relates`.

## Comments

```bash
# Add a comment
acli jira workitem comment create --key PROJ-123 --body "Completed implementation. PR submitted."

# Add comment from file
acli jira workitem comment create --key PROJ-123 --body-file comment.txt

# Comment on multiple issues
acli jira workitem comment create --key "PROJ-123,PROJ-456" --body "Batch update: resolved in v3.4"

# Update an existing comment (get COMMENT_ID from: comment list --key PROJ-123 --json)
acli jira workitem comment update --key PROJ-123 --id COMMENT_ID --body "Updated comment text"

# Delete a comment
acli jira workitem comment delete --key PROJ-123 --id COMMENT_ID
```

## Troubleshooting

- **Invalid transition** -- Target status not reachable from current status. View the issue to check its current status, then use a valid transition name. Status names are project-specific (e.g., "Closed" vs "Done").
- **Invalid parent/type hierarchy** -- Creating a child with `--parent` requires `Sub-task` type. Using `Task` or other types produces "does not belong to appropriate hierarchy."
- **ADF `INVALID_INPUT`** -- Malformed ADF JSON. Common causes: missing `version` field, text nodes directly inside `doc` (must be wrapped in a block node), or `code` mark combined with other marks.
- **Field not on screen** -- Some fields cannot be set via `edit` if they are not configured on the issue's edit screen. The error message indicates which field.
