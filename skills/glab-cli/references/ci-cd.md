# CI/CD

Pipelines, jobs, schedules, and variables with `glab ci`, `glab schedule`, and `glab variable`. Write operations (`run`, `retry`, `cancel`, `trigger`, `delete`, `set`, `update`) modify GitLab state — see Safety in the main skill body.

## Pipelines

### Run

Create a new pipeline on a branch. Variables can be passed in four ways.

```bash
glab ci run --branch main
glab ci run --branch main --variables key1:value1,key2:value2
glab ci run --branch develop --variables-env SECRET_KEY:production
glab ci run --branch main --variables-file config:settings.yml
glab ci run --branch main --variables-from vars.json
```

Typed pipeline inputs use the `--input` flag. Parenthesized types require shell quoting:

```bash
glab ci run --branch main --input 'deploy_count:int(3)' --input 'verbose:bool(true)'
glab ci run --branch main --input 'targets:array(staging,prod)'
```

Flags:
- `--branch NAME` -- Branch or ref for the pipeline
- `--variables KEY:VALUE` -- Pipeline variables (comma-separated or repeat)
- `--variables-env KEY:VALUE` -- Environment-type variables
- `--variables-file KEY:FILENAME` -- File variable (file contents become the value)
- `--variables-from FILE` -- JSON file with `[{key, value, variable_type}]`
- `--input KEY:VALUE` -- Pipeline inputs with optional types: `key:string(val)`, `key:int(N)`, `key:float(N)`, `key:bool(true)`, `key:array(a,b)`
- `--mr` -- Run MR pipeline. **Incompatible with all variable and input flags.**
- `--web` -- Open in browser

Array inputs support trailing-comma edge cases: `array(foo,bar,)` means `[foo, bar]`, `array()` is an empty array, and `array(,)` is an array with an empty string.

### Cancel Pipeline

Cancel one or more running pipelines.

```bash
glab ci cancel pipeline <pipeline-id>
glab ci cancel pipeline 123,456                           # Cancel multiple (comma-separated)
glab ci cancel pipeline 123 --dry-run                     # Simulate
```

### Delete

Delete pipelines by ID or by filter criteria. Supports bulk deletion.

```bash
glab ci delete <pipeline-id>
glab ci delete --status failed --older-than 720h. # Delete failed pipelines older than 30 days
glab ci delete --source schedule --paginate --dry-run  # Preview scheduled pipeline cleanup
```

Flags:
- `--status VALUE` -- Filter by status (`running`, `pending`, `success`, `failed`, etc.)
- `--source VALUE` -- Filter by pipeline source
- `--older-than DURATION` -- Duration filter (units: `h`, `m`, `s`)
- `--dry-run` -- Simulate without deleting
- `--paginate` -- Fetch all pages before deleting
- `--page N --per-page N` -- Pagination

### Lint

Validate `.gitlab-ci.yml` syntax. Use `--dry-run` for server-side pipeline simulation (more thorough than static lint).

```bash
glab ci lint
glab ci lint --dry-run --ref main --include-jobs
```

Flags:
- `--dry-run` -- Server-side pipeline simulation
- `--include-jobs` -- Include job list in response
- `--ref NAME` -- Branch context for simulation (only with `--dry-run`)

### Config Compile

Expand and resolve the full CI config — resolves `include:`, YAML anchors, and `extends:`. Outputs merged YAML. Different from `lint`: shows the resolved result without validating it.

```bash
glab ci config compile
```

### Pipeline Status and Details

Use `ci get` for non-interactive pipeline/job inspection. It can target a pipeline by ID, branch, or MR head pipeline; the MR head pipeline can differ from the latest source-branch pipeline for forks or detached pipelines. The `--merge-request` and `--status` filters require `glab` v1.98.1+.

```bash
glab ci get --pipeline-id 12345 --with-job-details
glab ci get --merge-request 42 --status failed --with-job-details
glab ci get --branch main --output json --jq '.status'
```

Flags:
- `--pipeline-id ID` -- Specific pipeline
- `--branch NAME` -- Latest pipeline for a branch (default: current branch)
- `--merge-request IID` -- Head pipeline for an MR
- `--status STATE` -- Show only jobs in the given state
- `--with-job-details` -- Include extended job information
- `--with-variables` -- Include pipeline variables (requires Maintainer role; may expose values)
- `--output text|json` / `--jq` -- Structured output and filtering

`ci status` is useful for quick branch status checks:

```bash
glab ci status --compact
glab ci status --branch main --output json
```

`ci status --output json` is incompatible with `--live` and `--compact`.

## Jobs

### Retry

Retry a failed or cancelled job. **Operates on individual jobs, not pipelines.** Accepts job ID (numeric) or job name (string). Always provide an ID or name — omitting it triggers interactive selection, which is unusable for agents.

```bash
glab ci retry <job-id>
glab ci retry "test-unit" --branch main
glab ci retry "deploy" --pipeline-id 789  # Disambiguate when name appears in multiple pipelines
```

Flags:
- `--branch NAME` -- Branch to search for the job
- `--pipeline-id ID` -- Pipeline ID to narrow search when job name is ambiguous

### Cancel Job

Cancel one or more running jobs.

```bash
glab ci cancel job <job-id>
glab ci cancel job 111,222                                # Cancel multiple (comma-separated)
glab ci cancel job 111 --dry-run
```

### Trigger

Play a manual job (`when: manual`). **Triggers manual jobs, not pipelines** — use `ci run` to create pipelines. Always provide a job ID or name — omitting it triggers interactive selection, which is unusable for agents.

```bash
glab ci trigger <job-id>
glab ci trigger "manual-deploy" --branch main
glab ci trigger "manual-deploy" --pipeline-id 789
```

Flags:
- `--branch NAME` -- Branch to search for the job
- `--pipeline-id ID` -- Pipeline ID

### Trace

Stream a job's log output. **Can block until a running job finishes** — there is no `--no-follow` flag. Always provide a job ID or name; omitting it triggers interactive selection, which is unusable for agents.

Check job status with `ci get` before tracing. Trace only completed jobs, redirecting output to a file:

```bash
glab ci trace <job-id> > job-output.log
glab ci trace "test-unit" --branch main --pipeline-id 789 > test.log
```

Flags:
- `--branch NAME` -- Branch to search for the job
- `--pipeline-id ID` -- Pipeline ID to narrow search

### Artifacts

Download job artifacts from the most recent successful pipeline for a ref and job name, or list artifact file paths. Prefer `glab job artifact`; `glab ci artifact` is deprecated.

```bash
glab job artifact <refName> <jobName>
glab job artifact main build --path ./artifacts
glab job artifact main deploy --list-paths  # Print the paths of downloaded artifacts
glab job artifact refs/merge-requests/123/head build  # MR head pipeline
glab job artifact refs/merge-requests/123/merge build  # Merged-result pipeline
```

Flags:
- `--path PATH` -- Download directory (default `./`)
- `--list-paths` -- Print the paths of downloaded artifacts

## Schedules

### List

```bash
glab schedule list
```

### Create

Create a pipeline schedule with a cron expression.

```bash
glab schedule create --cron "0 2 * * *" --ref main --description "Nightly build"
glab schedule create --cron "30 8 * * 1-5" --cronTimeZone "America/New_York" --ref develop --description "Weekday morning build"
```

Flags:
- `--cron EXPR` -- 5-field standard cron: `min hour day month weekday`
- `--cronTimeZone ZONE` -- IANA timezone (default `UTC`)
- `--ref NAME` -- Target branch or tag
- `--description TEXT` -- Schedule description
- `--active` -- Active state (default `true`)
- `--variable KEY:VALUE` -- Variables (repeat for multiple)

### Update

Update a schedule. Uses **three separate variable flags** for modifications:

```bash
glab schedule update <schedule-id> --cron "0 3 * * *"
glab schedule update <schedule-id> --create-variable new_key:value
glab schedule update <schedule-id> --update-variable existing_key:new_value
glab schedule update <schedule-id> --delete-variable old_key
```

Flags:
- `--cron EXPR` -- Cron interval pattern
- `--cronTimeZone ZONE` -- IANA timezone
- `--ref NAME` -- Target branch or tag
- `--description TEXT` -- Schedule description
- `--active` -- Active state (default: no change)
- `--create-variable KEY:VALUE` -- Add new variables
- `--update-variable KEY:VALUE` -- Update existing variables
- `--delete-variable KEY` -- Remove variables (key only, no value)

### Run / Delete

```bash
glab schedule run <schedule-id>                           # Trigger immediately
glab schedule delete <schedule-id>
```

## Variables

### List

```bash
glab variable list
glab variable list --group my-group  # Group-level variables
glab variable list --instance  # Instance-level variables
glab variable list --output json
```

### Get

Retrieve a variable's value. **May expose secrets** — list metadata first to confirm the variable is safe to retrieve.

```bash
glab variable get SECRET_KEY
glab variable get SECRET_KEY --output json
glab variable get DB_URL --scope production  # Environment-scoped variable
glab variable get GROUP_VAR --group my-group
```

Flags:
- `--output text|json` -- Output format
- `--group GROUP` -- Group-level variable
- `--scope PATTERN` -- Environment scope (default `*`)

### Set

Create a variable. Value can be provided as a positional argument, with `--value`, or via stdin.

```bash
glab variable set API_KEY "the-value"
glab variable set API_KEY --value "the-value"
echo "the-value" | glab variable set API_KEY
glab variable set DB_CERT --type file --value @cert.pem
glab variable set SECRET --masked --protected --scope production
```

Flags:
- `--value TEXT` -- Variable value (alternative to positional)
- `--description TEXT` -- Variable description
- `--masked` -- Hide value in job logs
- `--protected` -- Available only on protected branches/tags
- `--hidden` -- Hidden variable
- `--raw` -- Disable variable expansion
- `--scope PATTERN` -- Environment scope (default `*`)
- `--type VALUE` -- `env_var` (default) or `file`
- `--group GROUP` -- Create as group-level variable

### Update / Delete

`variable update` accepts the same flags as `set` except `--hidden`.

```bash
glab variable update API_KEY "new-value" --masked
glab variable delete OLD_KEY
glab variable delete OLD_KEY --scope staging --group my-group
```

### Export

Export all variables. **Default output is `json`** (unlike all other commands which default to `text`).

```bash
glab variable export  # JSON output (default)
glab variable export --output env  # KEY=VALUE format (most compact)
glab variable export --output export  # export KEY=VALUE (shell-sourceable)
glab variable export --group my-group --scope production
```

Flags:
- `--output VALUE` -- `json` (default), `export`, `env`
- `--scope PATTERN` -- Environment scope (default `*`)
- `--page N --per-page N` -- Pagination (default per-page: 100)

## Workflows

### Debugging a failed pipeline

1. **Find the failed pipeline:**
   ```bash
   glab ci list --status failed --per-page 5
   ```

2. **View pipeline details and identify the failed job:**
   ```bash
   glab ci get --pipeline-id <id> --status failed --with-job-details
   ```

3. **Retry the failed job:**
   ```bash
   glab ci retry <job-id>
   ```

4. **If the job log is needed, trace a completed job:**
   ```bash
   glab ci trace <job-id> > failed-job.log
   ```

### Investigating MR CI failures

1. **View the MR to find the source branch:**
   ```bash
   glab mr view 123
   ```

2. **List failed pipelines for that branch:**
   ```bash
   glab ci list --ref <source-branch> --status failed
   ```

3. **Get pipeline details** (prefer MR head pipeline when available):
   ```bash
   glab ci get --merge-request <iid> --status failed --with-job-details
   ```

4. **Retry the failed job after pushing a fix:**
   ```bash
   glab ci retry <job-id>
   ```

## Documentation

- [CI/CD pipelines](https://docs.gitlab.com/ee/ci/pipelines/) -- Pipeline configuration and management
- [Pipeline schedules](https://docs.gitlab.com/ee/ci/pipelines/schedules.html) -- Scheduled pipeline execution
- [CI/CD variables](https://docs.gitlab.com/ee/ci/variables/) -- Variable types, scopes, and precedence
- [glab ci](https://docs.gitlab.com/cli/ci/) -- CLI command reference for CI/CD
