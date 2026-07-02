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

Interact with GitLab from the command line: repositories, issues, merge requests, CI/CD pipelines, releases, and API requests across GitLab.com, GitLab Self-Managed, and GitLab Dedicated instances.

Verified with `glab` 1.106.0.

## Version Compatibility

If the installed `glab` version is not 1.106.0, run `glab --version` and verify version-gated commands with `glab <command> <subcommand> --help` before using them. Notable recent changes:

- `--jq` on standard non-`api` commands requires v1.100.0+. Older versions may still support `--output json`; pipe to external `jq` or use `glab api`.
- `glab api --form` requires v1.91.0+.
- `glab todo list` / `todo done` require v1.92.0+.
- `glab search semantic` and `issue/mr create --template` require v1.93.0+.
- `mr note` subcommands changed across v1.90-v1.101: `list`/`resolve`/`reopen` in v1.90, `create` in v1.93, reply/diff-comment flags in v1.94, `update`/`delete` in v1.98.1, and `--resolvable` in v1.101.
- `ci get --merge-request` / `--status` require v1.98.1+.
- `glab api` placeholder URL encoding for `:fullpath` was fixed in v1.102.0; manually URL-encode paths if older versions mis-handle nested project paths.
- `glab packages` and `glab container-registry` are recent: package/registry listing in v1.103, package upload in v1.104, package download/delete in v1.106.

## Agent Guidelines

- Always use long flag names in commands (`--output`, `--output-format`, `--field`). Where present, the short flag `-F` maps to `--output-format` on `issue list`/`incident list`, `--field` on `glab api`, `--notes-file` on `release create`, and `--output` elsewhere (with `variable export` accepting `json`/`export`/`env` instead of the usual `text`/`json`).
- Default text output is most token-efficient for quick reading. For structured extraction on supported read commands, use `--output json --jq '<expr>'` when the command has `--output`; a few newer groups expose `--jq` without `--output`. `glab` has no `gh --json FIELDS`, general `--csv`, Go-template, or custom `--format` mode.
- `glab api` has no built-in `--jq` flag. Pipe API output to external `jq`; for large paginated arrays, prefer `glab api --paginate --output ndjson | jq ...`.
- Use `--output-format ids` on `issue list` and `incident list` when only IDs are needed. For list commands with JSON output but no `--output-format` (for example `mr list`), use `--output json --jq`.
- Use `ci status --compact` for quick pass/fail checks. `ci view` is TUI-only and unsuitable for programmatic use.
- Use `ci status --output json` for machine-readable status; it is incompatible with `--live` and `--compact`.
- `ci trace` streams job output and can block until a running job finishes — there is no `--no-follow` flag. Check job status first with `ci get`; trace only completed jobs, redirecting output to a file.
- Use `variable export --output env` for compact `KEY=VALUE` output instead of the default JSON.
- Omit `--comments`, `--system-logs`, `--with-job-details`, and `--with-variables` unless specifically needed — they significantly increase output size.
- Scope list output with `--per-page` to control result count. Most list commands use `--page`/`--per-page`; commands with ranked results, such as `search semantic`, may use `--limit`.
- Use `glab search semantic` only for beta GitLab Duo semantic code search when approximate natural-language matching is acceptable. For exact text, regex, or multi-file code exploration, clone to a temp directory (`glab repo clone owner/repo <temp-dir> -- --depth 1`) and search locally with file-reading and search tools.
- Use `glab api` for quick reads of specific known files or repository metadata.
- When unsure about flags, run `glab <command> <subcommand> --help`.

## Safety

- **Write operations** include command verbs such as `create`, `update`, `merge`, `approve`, `close`, `delete`, `run`, `retry`, `cancel`, `trigger`, `note`, `resolve`, `reopen`, `upload`, `rotate`, `revoke`, plus `todo done`, `subscribe`/`unsubscribe`, `fork`, `archive`, and variable/settings changes. Confirm with the user before executing.
- **`glab mr merge` defaults `--auto-merge` to `true`** — when a pipeline is running, this queues the MR to merge when checks pass. Use `--auto-merge=false` only when immediate merge is intended, and use `--sha` to guard the reviewed HEAD.
- **`glab api` method defaults:** GET without parameters, POST when `--field`, `--raw-field`, or `--form` are present. Use explicit `--method` (`-X`) for PUT, PATCH, and DELETE.
- **Secret exposure:** `token create`, `token rotate`, `auth status --show-token`, `variable get`, and `variable export` can expose token or secret values into agent context. List metadata first when possible; do not print secret values unless explicitly requested.
- **Comment shell escaping:** For note/comment bodies containing backticks, `$`, or shell metacharacters, pass the body via stdin where supported (for example `glab mr note create 123 < body.md`) or load a temp file into the flag (`--message "$(<body.md)"`) instead of inlining it in double quotes.
- **Package and registry deletion** (`packages delete`, `container-registry ... delete`, `release delete --with-tag`) can remove published artifacts or tags. Require explicit target IDs/names before executing.

## Prerequisites

Verify `glab` is installed and authenticated:

```bash
glab --version
glab auth status
```

If not authenticated: `glab auth login` (interactive) or `glab auth login --hostname <host> --token <pat>` (non-interactive). Check command-specific flags with `glab <command> --help`.

## Host Targeting and Self-Managed GitLab

`glab` auto-detects the target instance from Git remotes. Override project/host context with `-R OWNER/REPO` (also accepts nested namespaces and URLs), `GITLAB_HOST`, or `--hostname` on `auth` commands.

- **Host precedence:** `-R`/`--repo` → Git remote → `GITLAB_HOST`/`GITLAB_URI`/`GL_HOST` → local config → global config → `gitlab.com`.
- **Token precedence:** `GITLAB_TOKEN`/`GITLAB_ACCESS_TOKEN`/`OAUTH_TOKEN` env vars override `--token`, keyring credentials, and config-file tokens.
- **Multi-instance:** Switching is implicit via context (git remote, env var, `-R`). There is no explicit `auth switch` command.

Self-managed login:

```bash
glab auth login --hostname gitlab.example.com --token <pat>
```

Minimum token scopes: `api`, `write_repository`. In GitLab CI, set `GLAB_ENABLE_CI_AUTOLOGIN=true` with `GITLAB_CI=true` to use `CI_JOB_TOKEN` and `CI_SERVER_FQDN`; `GITLAB_TOKEN` still takes precedence.

## Common Flags

Available on most read commands:

- `--output text|json` -- Output format. Default: `text` on most read commands.
- `--jq EXPRESSION` -- Filter JSON output using jq syntax. Use with `--output json` when the command has `--output`; not available on `glab api`.
- `--page N --per-page N` -- Pagination. Default per-page varies by command.
- `-R`/`--repo OWNER/REPO` -- Target a different project. Also accepts full URLs and nested group paths.
- `--web` / `-w` -- Open the result in a browser.

## Issues

Use these commands to list and view issues. For creating, updating, closing, commenting, advanced triage, subscriptions, and deletion, load [Issues](references/issues.md).

### List

List issues in a project, filtered by label, assignee, or search query. Defaults to open issues.

```bash
glab issue list
glab issue list --label bug --assignee @me
glab issue list --closed --search "error" --per-page 10
glab issue list --output-format ids                       # Most compact: one IID per line
glab issue list --output json --jq '.[].iid'
```

Key filters: `--search` with `--in title,description`, `--label`/`--not-label`, `--assignee @me`/`--not-assignee`, `--author`, `--milestone`, `--issue-type`, `--iteration`, `--closed`/`--all`, `--group` + `--epic`.

Output: `--output-format ids|urls` (default `details`) is most compact for IDs/URLs; its short flag is `-F`. JSON uses `--output json --jq`; short output flag is `-O`, not `-F`.

### View

Display an issue's title, description, labels, assignees, and status.

```bash
glab issue view 123
glab issue view 123 --comments
glab issue view 123 --output json
glab issue view 123 --output json --jq '.title'
```

Key flags: `--comments` includes comments and activities; `--system-logs` includes system activities; `--page`/`--per-page` paginate comments.

## Merge Requests

Use these commands to view and inspect MRs. For creating, updating, merging, reviewing, and managing MRs, load [Merge Requests](references/merge-requests.md).

### List

List merge requests in a project, filtered by author, label, or search query. Defaults to open MRs.

```bash
glab mr list
glab mr list --assignee @me --merged
glab mr list --label "needs-review" --draft
glab mr list --source-branch feature-x --per-page 10
glab mr list --output json --jq '.[].iid'
```

Key filters: `--search`, `--assignee @me`, `--reviewer`, `--author`, `--label`/`--not-label`, `--milestone`, `--source-branch`, `--target-branch`, `--closed`/`--merged`/`--all`, `--draft`/`--not-draft`, `--deployed-after`/`--deployed-before` + `--environment`, `--group`.

Output: `mr list` has no `--output-format`; use `--output json --jq` for structured extraction.

### View

Display an MR's title, description, reviewers, and metadata. Text output shows reviewer names but not approval or pipeline status — use `--output json` for those fields.

```bash
glab mr view 123
glab mr view 123 --comments
glab mr view 123 --unresolved
glab mr view 123 --output json
```

Key flags: `--comments`, `--resolved`/`--unresolved` (implies `--comments`), `--system-logs`, and `--page`/`--per-page` for comment context size.

### Diff

View the file changes in an MR as a unified diff.

```bash
glab mr diff 123
glab mr diff 123 --color=never                            # Machine-readable output
```

Key flags: `--color=never` for machine-readable output; `--raw` for pipeable raw diff.

There is no `--name-only` flag. Use `glab api` for a changed file summary — see [API Patterns](references/api-patterns.md).

### Approvers

List approval requirements and status for an MR.

```bash
glab mr approvers 123
glab mr approvers 123 --output json --jq '.rules[] | {name, approvals_required, approved}'
```

Use `--output json --jq` to extract rule names, required approvals, or approval state.

## CI/CD Pipelines

Use these commands to view pipeline and job status. For running pipelines, retrying jobs, managing schedules, and working with variables, load [CI/CD](references/ci-cd.md).

### List Pipelines

List recent pipelines, filtered by status, branch, or source.

```bash
glab ci list
glab ci list --status failed --per-page 5
glab ci list --ref main --source push
glab ci list --yaml-errors                                # Find pipelines with config errors
glab ci list --status failed --output json --jq '.[].id'
```

Key filters: `--status` (`running`, `pending`, `success`, `failed`, `canceled`, `skipped`, `created`, `manual`, `waiting_for_resource`, `preparing`, `scheduled`), `--ref`, `--source` (`push`, `trigger`, `pipeline`, `parent_pipeline`, `merge_request_event`), `--name`, `--scope`, `--username`, `--sha`, and `--yaml-errors`.

### View Pipeline Details

View a pipeline's summary, job statuses, and variables. Specify a pipeline with `--pipeline-id` or `--branch` — positional arguments are not accepted.

```bash
glab ci get --pipeline-id 12345
glab ci get --pipeline-id 12345 --with-job-details
glab ci get --merge-request 42 --status failed --with-job-details
glab ci get --branch main --output json
```

Key flags: `--pipeline-id`, `--branch`, `--merge-request` (MR head pipeline; requires v1.98.1+), `--status` (job state filter; requires v1.98.1+), `--with-job-details`, `--with-variables` (requires Maintainer role and may expose values).

### Pipeline Status

Show the latest pipeline status for a branch.

```bash
glab ci status
glab ci status --compact                                  # Most concise status check
glab ci status --branch main
glab ci status --branch main --output json
```

Key flags: `--compact` for the most concise check, `--branch`, `--live` for streaming updates, and `--output json` for machine-readable status. JSON is incompatible with `--live` and `--compact`.

## Repositories

### View

Display a repository's description and metadata. Use `--branch` to view branch-specific repository metadata.

```bash
glab repo view
glab repo view owner/repo --output json
glab repo view --branch develop
glab repo view owner/repo --output json --jq '.default_branch'
```

### Clone

Clone a repository locally. Use a shallow clone for code exploration when exact text, regex, or multi-file reasoning is needed.

```bash
glab repo clone owner/repo [target-directory]
glab repo clone owner/repo [target-directory] -- --depth 1
glab repo clone --group my-group --archived=false --paginate
```

### List

List repositories accessible to the authenticated user. Defaults to projects you own (`--mine`).

```bash
glab repo list
glab repo list --group my-group --include-subgroups
glab repo list --starred --per-page 50
glab repo list --all --output json
glab repo list --group my-group --output json --jq 'length'
```

Key filters: `--mine` (default), `--all`, `--member`, `--user`, `--starred`, `--group`, `--include-subgroups`, `--archived true|false`, `--order`, `--sort`.

### Search and Semantic Code Search

Search for repositories by keyword, or use beta GitLab Duo semantic code search for approximate natural-language code matching. For exact text or regex, clone and search locally.

```bash
glab repo search --search "keyword" --per-page 20
glab repo search --search "cli" --output json
glab search semantic --query "authentication middleware" --repo owner/repo --limit 5
glab search semantic --query "CI pipeline triggers" --repo owner/repo --output json --jq '.[].path'
```

`glab search semantic` requires `glab` v1.93.0+ and GitLab Duo semantic code search. For repository creation, updating, forking, contributors, labels, milestones, todos, packages, and registry commands, load [Project Management](references/project-management.md).

## Releases

### List

List releases in a project, ordered by creation date (newest first).

```bash
glab release list
glab release list --per-page 10
glab release list --output json --jq '.[].tag_name'
```

### View

Display a release's notes, tag, and assets. Omit the tag to view the latest release.

```bash
glab release view v1.2.0
glab release view --output json --jq '.tag_name'
```

For creating, uploading, downloading, deleting releases, and generating changelogs, load [Releases](references/releases.md).

## API

Use `glab api` for operations beyond standard subcommands. Requests are authenticated automatically.

```bash
glab api 'projects/:fullpath/issues?per_page=5'
glab api projects/:fullpath/merge_requests/123 | jq '.title'
```

Endpoint placeholders (`:id`, `:fullpath`, `:user`, `:branch`) are populated from the current Git context; `:fullpath` URL-encodes group/project paths in current `glab` versions. Method defaults are GET without parameters and POST when `--field`, `--raw-field`, or `--form` are present; use explicit `--method` for PUT, PATCH, and DELETE.

The `-F` flag means `--field` on `glab api`, not `--output`. `glab api` has no `--jq` flag — pipe to external `jq`:

```bash
glab api projects/:fullpath/issues | jq '.[].title'
glab api projects/:fullpath/issues --paginate --output ndjson | jq 'select(.state == "opened")'
```

For endpoint patterns, pagination, GraphQL, and common recipes, load [API Patterns](references/api-patterns.md).

## Other Commands

Run `glab <command> --help` for exact flags. Load [Project Management](references/project-management.md) for label and milestone mutations, repository settings, forking, contributors, todos, iterations, work items, packages, and registry commands.

- `glab label list --output json --jq '.[].name'` -- List labels. Use `--group` for group labels.
- `glab milestone list --project my-group/my-project --state active` -- List milestones; use `--show-id` before `milestone get/edit/delete`.
- `glab incident list --output-format ids` / `glab incident view 456` -- Incidents use the issue interface, including `--output-format ids|urls`.
- `glab todo list` -- List todos (requires v1.92.0+). `todo done` changes GitLab state.
- `glab token`, `glab packages`, and `glab container-registry` expose or mutate credentials/artifacts. Package/registry listing requires v1.103.0+, package upload v1.104.0+, and package download/delete v1.106.0+.

## Troubleshooting

- **Not authenticated** -- Run `glab auth login`. Verify with `glab auth status`.
- **`auth status` shows wrong host** -- `glab auth status` respects `GITLAB_HOST`. Use `--hostname` or `GITLAB_HOST` to check a specific instance.
- **Wrong project targeted** -- Use `-R OWNER/REPO` or verify Git remotes with `git remote -v`.

## References

- [Merge Requests](references/merge-requests.md) -- Creating, updating, merging, reviewing, and managing MRs
- [Issues](references/issues.md) -- Creating, updating, closing, commenting, triage, subscriptions, and deletion
- [CI/CD](references/ci-cd.md) -- Pipelines, jobs, schedules, and variables
- [API Patterns](references/api-patterns.md) -- `glab api`, pagination, GraphQL, file reads, and fallback recipes
- [Project Management](references/project-management.md) -- Labels, milestones, repository settings, todos, work items, packages, and registry
- [Releases](references/releases.md) -- Release creation, assets, deletion, and changelog generation

## Documentation

- [GitLab CLI documentation](https://docs.gitlab.com/cli/) -- Official `glab` docs
- [GitLab CLI releases](https://gitlab.com/gitlab-org/cli/-/releases) -- Version history and release notes
- [GitLab REST API](https://docs.gitlab.com/api/rest/) -- REST endpoint reference for `glab api`
- [GitLab GraphQL API](https://docs.gitlab.com/api/graphql/) -- GraphQL schema and query reference
