# Project Management

Labels, milestones, repository settings, todos, iterations, work items, packages, and registry commands with `glab label`, `glab milestone`, `glab repo`, `glab todo`, `glab iteration`, `glab work-items`, `glab packages`, and `glab container-registry`. Write operations modify GitLab state — see Safety in the main skill body.

## Labels

### Create

Create a project label. Text output only.

```bash
glab label create --name "priority::high" --color "#FF0000" --description "High priority items"
glab label create --name "area::backend" --priority 1
```

Flags:
- `--name TEXT` -- Label name
- `--color VALUE` -- Color in plain name or HEX (default `#428BCA`)
- `--description TEXT` -- Label description
- `--priority N` -- Label priority (integer)

### Get

Retrieve a label by its numeric ID. Supports JSON output.

```bash
glab label get <label-id>
glab label get <label-id> --output json --jq '.name'
```

## Milestones

### Create

Create a milestone. Text output only.

```bash
glab milestone create --title "Sprint 5" --description "Q2 deliverables" --due-date 2026-06-30T00:00:00Z
glab milestone create --title "v2.0" --start-date 2026-04-01T00:00:00Z --due-date 2026-07-31T00:00:00Z --group my-group
```

Flags:
- `--title TEXT` -- Milestone title
- `--description TEXT` -- Description
- `--due-date DATETIME` -- Due date, ISO 8601 datetime (e.g., `2026-06-30T00:00:00Z`)
- `--start-date DATETIME` -- Start date, ISO 8601 datetime
- `--group ID` -- Group ID or URL-encoded path
- `--project ID` -- Project ID or URL-encoded path

### Edit

Update a milestone. Accepts all `create` flags plus `--state`. Takes milestone ID as argument. Text output only.

```bash
glab milestone edit <milestone-id> --title "Sprint 5 (Extended)" --due-date 2026-07-15T00:00:00Z
glab milestone edit <milestone-id> --state close
```

Additional flag:
- `--state VALUE` -- `activate` or `close`

### Delete

Delete a milestone by ID. Text output only.

```bash
glab milestone delete <milestone-id>
glab milestone delete <milestone-id> --group my-group
```

Flags:
- `--group ID` -- Group scope
- `--project ID` -- Project scope

## Repositories

### Create

Create a new project. **No `-R` flag** — host is determined by `GITLAB_HOST` env var or the first configured host (defaults to `gitlab.com`). Text output only.

```bash
glab repo create --name my-project --private --readme
glab repo create --name my-project --group my-group --defaultBranch main --tag cli --tag tool
```

Flags:
- `--name TEXT` -- Project name
- `--description TEXT` -- Description (`"-"` opens editor)
- `--group GROUP` -- Namespace or group (defaults to current user's namespace)
- `--defaultBranch NAME` -- Default branch (defaults to `master`)
- `--private` / `--public` / `--internal` -- Visibility (default: internal)
- `--readme` -- Initialize with README.md
- `--remoteName NAME` -- Remote name (default `origin`)
- `--tag NAME` -- Tags for the project (repeat for multiple)
- `--skipGitInit` -- Skip initializing a local Git repository

### Update

Update project settings. **No `-R` flag.** Text output only.

```bash
glab repo update --description "Updated project description"
glab repo update --defaultBranch main
glab repo update --archive  # Archive (lock) the project
glab repo update --archive=false  # Unarchive
```

Flags:
- `--description TEXT` -- New description
- `--defaultBranch NAME` -- New default branch
- `--archive` -- Archive the project. Use `--archive=false` to unarchive.

### Fork

Fork a repository to your account or namespace.

```bash
glab repo fork owner/repo --clone
glab repo fork owner/repo --name my-fork --path my-fork-path
```

Key flags: `--clone`, `--name`, `--path`, `--remote`.

### Contributors

List repository contributors with commit counts.

```bash
glab repo contributors
glab repo contributors --order name --sort asc
```

For issue create/update/close/note, triage filters, subscriptions, and deletion, see [Issues](issues.md).

## Todos and Planning

### Todos

List pending items that need your attention, such as assigned issues or requested reviews. `todo list` and `todo done` require `glab` v1.92.0+. Marking todos done changes GitLab state.

```bash
glab todo list
glab todo list --type MergeRequest --action approval_required --output json --jq '.[].target_url'
glab todo done <todo-id>
```

### Iterations

Iterations are time-boxed periods similar to sprints. List project or group iterations:

```bash
glab iteration list
glab iteration list --group my-group
```

### Work Items

`glab work-items` is experimental. Prefer stable `glab issue` commands unless the task explicitly requires work items.

```bash
glab work-items list --type issue --repo my-group/my-project
```

### Issue Boards

`glab issue board view` is interactive; avoid it in non-interactive agent workflows. Use `issue list` filters for programmatic triage.

```bash
glab issue board create --name "Triage"
glab issue board view
```

## Packages and Registry

These command groups are useful for artifact management but include destructive operations. `packages list` and `container-registry` require `glab` v1.103.0+, `packages upload` requires v1.104.0+, and `packages download`/`delete` require v1.106.0+:

- `glab packages list` -- List packages by name/type.
- `glab packages download` -- Download generic package files; checksum verification is enabled by default. `--no-verify` skips integrity checks.
- `glab packages upload` / `glab packages delete` -- Mutate package registry state.
- `glab container-registry repository list` / `tag list` -- Inspect container registry repositories and tags.
- `glab container-registry ... delete` -- Delete registry tags or repositories; confirm exact IDs/names first.

## Documentation

- [Labels](https://docs.gitlab.com/ee/user/project/labels.html) -- GitLab label documentation
- [Milestones](https://docs.gitlab.com/ee/user/project/milestones/) -- GitLab milestone documentation
- [glab label](https://docs.gitlab.com/cli/label/) -- CLI command reference for labels
- [glab milestone](https://docs.gitlab.com/cli/milestone/) -- CLI command reference for milestones
- [glab todo](https://docs.gitlab.com/cli/todo/) -- To-do list command reference
- [glab work-items](https://docs.gitlab.com/cli/work-items/) -- Experimental work items command reference
