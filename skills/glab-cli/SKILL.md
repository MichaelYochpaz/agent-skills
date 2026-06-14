---
name: glab-cli
description: >-
  GitLab CLI (glab) for interacting with GitLab from the command line. Covers
  repositories, issues, merge requests, CI/CD pipelines, releases, and the
  GitLab API. Use when performing any GitLab-related operation, managing
  CI/CD pipelines and jobs, working with merge requests, or when the user
  mentions GitLab, glab, MRs, pipelines, .gitlab-ci.yml, projects, or groups.
license: MIT
metadata:
  author: Michael Yochpaz
  source: https://github.com/michaelyochpaz/agent-skills
---

# GitLab CLI (`glab`)

`glab` is the official open-source CLI for GitLab, maintained by GitLab Inc. It works with GitLab.com, GitLab Self-Managed, and GitLab Dedicated instances, supporting multiple authenticated instances simultaneously. If `glab` is not installed, see the [installation guide](https://gitlab.com/gitlab-org/cli#installation).

## Agent Guidelines

- Always use long flag names in commands (`--output`, `--output-format`, `--field`). The short flag `-F` maps to `--output-format` on `issue list`/`incident list`, `--field` on `glab api`, `--notes-file` on `release create`, and `--output` everywhere else (with `variable export` accepting `json`/`export`/`env` instead of the usual `text`/`json`).
- Default text output is more token-efficient than `--output json` — JSON dumps all fields with no selection mechanism. Use text for reading and viewing.
- For filtered structured data, use `glab api` piped to external `jq`, or GraphQL queries. glab has no `--jq` or `--json FIELDS` equivalent.
- Use `--output-format ids` on `issue list` and `incident list` when only IDs are needed — this is the most compact output mode in glab.
- Use `ci status --compact` for quick pass/fail checks. `ci view` is TUI-only and unsuitable for programmatic use.
- `ci trace` streams job output and blocks until the job finishes — there is no `--no-follow` flag. Check job status first with `ci get`; trace only completed jobs, redirecting output to a file.
- Use `variable export --output env` for compact `KEY=VALUE` output instead of the default JSON.
- Omit `--comments`, `--system-logs`, `--with-job-details`, and `--with-variables` unless specifically needed — they significantly increase output size.
- Scope list output with `--per-page` to control result count. glab uses `--page`/`--per-page` for pagination, not `--limit`.
- glab has no code search command. Clone to a temp directory and search locally with file-reading and search tools.
- For multi-file exploration or cross-file search, clone the repo (`git clone --depth 1`). Use `glab api` for quick reads of specific known files.
- When unsure about flags, run `glab <command> <subcommand> --help`.

## Safety

- **Write operations** (`create`, `update`, `merge`, `approve`, `close`, `delete`, `run`, `retry`, `cancel`, `note`) modify GitLab state. Confirm with the user before executing.
- **`glab mr merge` defaults `--auto-merge` to `true`** — this queues the MR for auto-merge when checks pass rather than merging immediately. Use `--auto-merge=false` to merge immediately.
- **`glab api` method defaults:** GET without parameters, POST when `--field`/`--raw-field` are present. Use explicit `--method` (`-X`) for PUT, PATCH, and DELETE.
- **`variable get` and `variable export` can expose secrets** into agent context. List variable metadata first before retrieving values.

## Prerequisites

Verify `glab` is installed and authenticated:

```bash
glab --version
glab auth status
```

If not authenticated: `glab auth login` (interactive) or `glab auth login --hostname <host> --token <pat>` (non-interactive).

Check the [GitLab CLI documentation](https://docs.gitlab.com/cli/) or run `glab <command> --help`.

## Host Targeting and Self-Managed GitLab

glab auto-detects the target instance from Git remotes in the current directory. Override with:

- `-R OWNER/REPO` -- Target a different project. Also accepts `GROUP/NAMESPACE/REPO`, full URLs, and nested namespaces up to 7 levels deep.
- `GITLAB_HOST` env var -- Set the default GitLab instance.
- `--hostname` on `auth` commands -- Target a specific instance.

**Host resolution precedence (highest to lowest):** `-R`/`--repo` flag → Git remote detection → `GITLAB_HOST`/`GITLAB_URI`/`GL_HOST` env var → local config → global config → `gitlab.com`.

**Token resolution precedence:** `GITLAB_TOKEN`/`GITLAB_ACCESS_TOKEN`/`OAUTH_TOKEN` env var (always wins — overrides `--token` on `auth login` and stored credentials) → OS keyring → config file.

**Self-managed login:**

```bash
glab auth login --hostname gitlab.example.com --token <pat>
```

Minimum required token scopes: `api`, `write_repository`.

**CI auto-login:** Set `GLAB_ENABLE_CI_AUTOLOGIN=true` with `GITLAB_CI=true` — glab uses `CI_JOB_TOKEN` and `CI_SERVER_FQDN` automatically. `GITLAB_TOKEN` still takes precedence.

**Multi-instance:** Switching is implicit via context (git remote, env var, `-R` flag). There is no explicit `auth switch` command.

## Common Flags

Available on most read commands:

- `--output text|json` -- Output format. Default: `text`. JSON dumps all fields with no field selection.
- `--page N --per-page N` -- Pagination. Default per-page varies by command.
- `-R`/`--repo OWNER/REPO` -- Target a different project. Also accepts full URLs and nested group paths.
- `--web` / `-w` -- Open the result in a browser.

## Issues

### List

List issues in a project, filtered by label, assignee, or search query. Defaults to open issues.

```bash
glab issue list
glab issue list --label bug --assignee @me
glab issue list --closed --search "error" --per-page 10
glab issue list --output-format ids                       # Most compact: one IID per line
```

Flags:
- `--search TEXT` -- Search by text. Searches fields specified by `--in`.
- `--in VALUE` -- Fields to search: `title`, `description` (default: `title,description`)
- `--label NAME` -- Filter by label (repeat for multiple)
- `--not-label NAME` -- Exclude labels
- `--assignee USER` -- Filter by assignee. Supports `@me` for the authenticated user.
- `--not-assignee USER` -- Exclude assignees
- `--author USER` -- Filter by author
- `--milestone NAME` -- Filter by milestone
- `--epic ID` -- Filter by epic ID (requires `--group`)
- `--closed` -- Show only closed issues
- `--all` -- Show all issues (open and closed)
- `--confidential` -- Show only confidential issues
- `--group GROUP` -- Group-level listing (across projects)
- `--output text|json` -- Output format (short flag is `-O`, not `-F`)
- `--output-format VALUE` -- `details` (default), `ids`, `urls` (short flag is `-F`)
- `--order FIELD` / `--sort asc|desc` -- Ordering
- `--page N --per-page N` -- Pagination

### View

Display an issue's title, description, labels, assignees, and status.

```bash
glab issue view 123
glab issue view 123 --comments
glab issue view 123 --output json
```

Flags:
- `--comments` -- Include comments and activities
- `--system-logs` -- Include system activities
- `--output text|json` -- Output format
- `--page N --per-page N` -- Pagination (for comments)

### Create

Create a new issue with a title, description, labels, and assignees.

```bash
glab issue create --title "Bug: description" --description "Details..." --label bug --assignee user1
```

Flags:
- `--title TEXT` -- Issue title
- `--description TEXT` -- Description (`"-"` opens editor)
- `--assignee USER` -- Assign usernames (comma-separated or repeat)
- `--label NAME` -- Labels (comma-separated or repeat)
- `--milestone VALUE` -- Milestone ID or title
- `--epic ID` -- Epic to add the issue to
- `--confidential` -- Make confidential
- `--weight N` -- Issue weight (≥ 0)
- `--due-date YYYY-MM-DD` -- Due date
- `--linked-issues IIDs` -- IIDs to link (comma-separated)
- `--link-type VALUE` -- Link relationship: `relates_to` (default), `blocks`, `is_blocked_by`
- `--linked-mr IID` -- MR IID to resolve issues in
- `--yes` -- Skip confirmation

### Update

Update an issue's title, description, labels, assignees, or milestone. There is no `issue edit` command — use `issue update`.

```bash
glab issue update 123 --title "New title"
glab issue update 123 --assignee +user2                   # Add assignee
glab issue update 123 --assignee '!user1'                 # Remove assignee
glab issue update 123 --label new-label --unlabel old-label
glab issue update 123 --milestone ""                      # Remove milestone
```

Flags:
- `--title TEXT` -- New title
- `--description TEXT` -- New description (`"-"` opens editor, pre-filled)
- `--assignee USER` -- Modify assignees: `+user` to add, `!user` or `-user` to remove, plain name replaces all
- `--unassign` -- Remove all assignees
- `--label NAME` -- Add labels
- `--unlabel NAME` -- Remove labels
- `--milestone VALUE` -- Set milestone (`""` or `0` to clear)
- `--confidential` / `--public` -- Set visibility
- `--lock-discussion` / `--unlock-discussion` -- Lock or unlock discussion
- `--weight N` -- Set weight
- `--due-date YYYY-MM-DD` -- Set due date

### Close / Reopen

Close or reopen an issue. `issue close` has no `--comment` flag — use `issue note` separately to add a closing comment.

```bash
glab issue close 123
glab issue reopen 123
```

### Note

Add a comment to an issue. The flag is `--message`, not `--body`.

```bash
glab issue note 123 --message "Investigation complete."
```

## Merge Requests

Use these commands to view and inspect MRs. For creating, updating, merging, reviewing, and managing MRs, load [Merge Requests](references/merge-requests.md).

### List

List merge requests in a project, filtered by author, label, or search query. Defaults to open MRs.

```bash
glab mr list
glab mr list --assignee @me --merged
glab mr list --label "needs-review" --draft
glab mr list --source-branch feature-x --per-page 10
```

Flags:
- `--search TEXT` -- Search text
- `--assignee USER` -- Filter by assignee. Supports `@me`.
- `--reviewer USER` -- Filter by reviewer
- `--author USER` -- Filter by author
- `--label NAME` -- Filter by label
- `--not-label NAME` -- Exclude labels
- `--milestone NAME` -- Filter by milestone
- `--source-branch NAME` -- Filter by source branch
- `--target-branch NAME` -- Filter by target branch
- `--closed` -- Show only closed MRs
- `--merged` -- Show only merged MRs
- `--all` -- Show all MRs (open, closed, and merged)
- `--draft` / `--not-draft` -- Filter by draft status
- `--created-after DATE` / `--created-before DATE` -- Date filters, ISO 8601 format
- `--order FIELD` / `--sort asc|desc` -- Order by: `created_at`, `updated_at`, `merged_at`, `title`, `priority`, `label_priority`, `milestone_due`, `popularity`
- `--group GROUP` -- Group-level listing (across projects)
- `--output text|json` -- Output format (no `--output-format`)
- `--page N --per-page N` -- Pagination

### View

Display an MR's title, description, reviewers, and metadata. Text output shows reviewer names but not approval or pipeline status — use `--output json` for those fields.

```bash
glab mr view 123
glab mr view 123 --comments
glab mr view 123 --output json
```

Flags:
- `--comments` -- Show comments and discussions
- `--system-logs` -- Show system activities
- `--output text|json` -- Output format
- `--page N --per-page N` -- Paginate comments (controls context window size)

### Diff

View the file changes in an MR as a unified diff.

```bash
glab mr diff 123
glab mr diff 123 --color=never                            # Machine-readable output
```

Flags:
- `--color VALUE` -- `always`, `never`, `auto` (default: `auto`). Use `--color=never` for machine-readable output.
- `--raw` -- Raw diff format (pipeable)

There is no `--name-only` flag. Use `glab api` for a changed file summary — see [API Patterns](references/api-patterns.md).

### Approvers

List approval requirements and status for an MR. Text output only.

```bash
glab mr approvers 123
```

## CI/CD Pipelines

Use these commands to view pipeline and job status. For running pipelines, retrying jobs, managing schedules, and working with variables, load [CI/CD](references/ci-cd.md).

### List Pipelines

List recent pipelines, filtered by status, branch, or source.

```bash
glab ci list
glab ci list --status failed --per-page 5
glab ci list --ref main --source push
glab ci list --yaml-errors                                # Find pipelines with config errors
```

Flags:
- `--status VALUE` -- `running`, `pending`, `success`, `failed`, `canceled`, `skipped`, `created`, `manual`, `waiting_for_resource`, `preparing`, `scheduled`
- `--ref NAME` -- Filter by branch or tag
- `--source VALUE` -- Pipeline source. Commonly used: `push`, `trigger`, `pipeline`, `parent_pipeline`, `merge_request_event`. See [CI_PIPELINE_SOURCE values](https://docs.gitlab.com/ci/jobs/job_rules/#ci_pipeline_source-predefined-variable) for the full list.
- `--name TEXT` -- Filter by pipeline name
- `--scope VALUE` -- `running`, `pending`, `finished`, `branches`, `tags`
- `--username USER` -- Filter by triggering user
- `--sha VALUE` -- Filter by commit SHA
- `--yaml-errors` -- Show only pipelines with invalid configurations
- `--updated-after DATE` / `--updated-before DATE` -- Date filters, ISO 8601 format
- `--order FIELD` / `--sort asc|desc` -- Order by: `id` (default), `status`, `ref`, `updated_at`, `user_id`. Sort default: `desc`.
- `--output text|json` -- Output format
- `--page N --per-page N` -- Pagination

### View Pipeline Details

View a pipeline's summary, job statuses, and variables. Specify a pipeline with `--pipeline-id` or `--branch` — positional arguments are not accepted.

```bash
glab ci get --pipeline-id 12345
glab ci get --pipeline-id 12345 --with-job-details
glab ci get --branch main --output json
```

Flags:
- `--pipeline-id ID` -- Pipeline ID to view
- `--branch NAME` -- View the latest pipeline for this branch (default: current branch)
- `--with-job-details` -- Include extended job information (increases output)
- `--with-variables` -- Include pipeline variables (requires Maintainer role)
- `--output text|json` -- Output format

### Pipeline Status

Show the latest pipeline status for a branch.

```bash
glab ci status
glab ci status --compact                                  # Most concise status check
glab ci status --branch main
```

Flags:
- `--compact` -- Compact format (most concise output)
- `--live` -- Real-time updates (streams until pipeline finishes)
- `--branch NAME` -- Check status for a specific branch (default: current branch)

## Repositories

### View

Display a repository's description and metadata.

```bash
glab repo view
glab repo view owner/repo --output json
glab repo view --branch develop
```

Flags:
- `--branch NAME` -- View a specific branch
- `--output text|json` -- Output format

### Clone

Clone a repository locally.

```bash
glab repo clone owner/repo [target-directory]
```

### List

List repositories accessible to the authenticated user. Defaults to projects you own (`--mine`).

```bash
glab repo list
glab repo list --group my-group --include-subgroups
glab repo list --starred --per-page 50
glab repo list --all --output json
```

Flags:
- `--mine` -- List only projects you own (default when no filter is set)
- `--all` -- List all projects on the instance
- `--member` -- List only projects you are a member of
- `--user USER` -- List projects for a specific user
- `--starred` -- List only starred projects
- `--group GROUP` -- List projects in a specific group
- `--include-subgroups` -- Include projects in subgroups (use with `--group`)
- `--archived VALUE` -- Filter by archived status (`true`/`false`). Use with `--group`.
- `--order FIELD` / `--sort asc|desc` -- Order by: `id`, `name`, `path`, `created_at`, `updated_at`, `similarity`, `star_count`, `last_activity_at` (default)
- `--output text|json` -- Output format
- `--page N --per-page N` -- Pagination

### Search

Search for repositories by keyword.

```bash
glab repo search --search "keyword" --per-page 20
glab repo search --search "cli" --output json
```

Flags:
- `--search TEXT` -- Search by project name
- `--output text|json` -- Output format
- `--page N --per-page N` -- Pagination

### Fork

Fork a repository to your account.

```bash
glab repo fork owner/repo --clone
glab repo fork owner/repo --name my-fork --path my-fork-path
```

Flags:
- `--clone` -- Clone the fork after creating
- `--name TEXT` -- Name for the forked project
- `--path TEXT` -- Path for the forked project
- `--remote` -- Add a remote for the fork

### Contributors

List repository contributors with commit counts.

```bash
glab repo contributors
glab repo contributors --order name --sort asc
```

Flags:
- `--order VALUE` -- Order by: `commits` (default), `name`, `email`
- `--sort asc|desc` -- Sort direction
- `--page N --per-page N` -- Pagination

For creating and updating repositories, load [Project Management](references/project-management.md).

## Releases

### List

List releases in a project, ordered by creation date (newest first).

```bash
glab release list
glab release list --per-page 10
```

### View

Display a release's notes, tag, and assets. Text output only.

```bash
glab release view v1.2.0
```

For creating, uploading, downloading, deleting releases, and generating changelogs, load [Releases](references/releases.md).

## API

Use `glab api` for operations beyond standard subcommands. All requests are authenticated automatically.

```bash
glab api 'projects/:fullpath/issues?per_page=5'
glab api projects/:fullpath/merge_requests/123 | jq '.title'
```

Endpoint placeholders `:id`, `:fullpath`, `:user`, `:branch` are auto-populated from the current Git context. `:fullpath` auto-handles URL-encoding of group/project paths.

Method defaults: GET without parameters, POST when `--field`/`--raw-field` are present. Use `--method` (`-X`) for PUT, PATCH, and DELETE.

The `-F` flag means `--field` on `glab api` (not `--output`). Use long flag names to avoid confusion.

glab has no `--jq` flag — pipe to external `jq`:

```bash
glab api projects/:fullpath/issues | jq '.[].title'
```

For endpoint patterns, pagination, GraphQL, and common recipes, load [API Patterns](references/api-patterns.md).

## Other Commands

### Labels

List labels in a project or group.

```bash
glab label list
glab label list --output json
glab label list --group my-group
```

### Milestones

List or view milestones. Use `--project` or `--group` with `milestone list` for targeted listing.

```bash
glab milestone list --project my-group/my-project --state active
glab milestone list --group my-group --search "Sprint" --show-id
glab milestone get <milestone-id>
```

Flags for `milestone list`:
- `--project ID` -- Project ID or URL-encoded path
- `--group ID` -- Group ID or URL-encoded path
- `--state VALUE` -- `active` or `closed`
- `--search TEXT` -- Filter by title or description
- `--show-id` -- Show milestone IDs in output (useful for `get`/`edit`/`delete`)
- `--include-ancestors` -- Include milestones from parent groups
- `--page N --per-page N` -- Pagination

### Incidents

List and view incidents. Same interface as issues, including `--output-format ids|urls`.

```bash
glab incident list
glab incident list --output-format ids
glab incident view 456
```

For label and milestone creation, editing, and deletion, repository settings, and issue housekeeping, load [Project Management](references/project-management.md).

## Known Limitations

- **No field selection on JSON output** — `--output json` dumps all fields. Use `glab api` + `jq` or GraphQL for specific fields.
- **No `--jq` on any command** including `glab api` — pipe to external `jq`.
- **No `--csv`, `--template`, or `--format`** output modes.
- **`--output-format ids|urls`** exists only on `issue list` and `incident list` — not on `mr list`.
- **`ci view` is interactive TUI** — unsuitable for programmatic use. Use `ci status` or `ci get` instead.
- **`ci trace` blocks indefinitely** on running jobs with no `--no-follow` flag. Check status first.
- **`issue close` has no `--comment`** flag and no close reason. Use `issue note` separately.
- **`mr diff` has no `--name-only`** — use `glab api` for changed file summaries.

## Troubleshooting

- **Not authenticated** -- Run `glab auth login`. Verify with `glab auth status`.
- **`auth status` shows wrong host** -- `glab auth status` respects `GITLAB_HOST`. Use `--hostname` or `GITLAB_HOST` to check a specific instance.
- **Wrong project targeted** -- Use `-R OWNER/REPO` or verify Git remotes with `git remote -v`.
- **`repo archive` downloads source code** -- `repo archive` exports the repo as a zip/tar archive. To archive (lock) a project, use `glab repo update --archive`.
