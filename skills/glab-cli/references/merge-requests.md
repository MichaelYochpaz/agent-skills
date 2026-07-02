# Merge Requests

Creating, updating, merging, reviewing, and managing merge requests with `glab mr`. Write operations (`create`, `update`, `merge`, `approve`, `close`, `delete`, `note create/update/delete`, `note resolve/reopen`) modify GitLab state — see Safety in the main skill body.

## Commands

### Create

Create a merge request from the current branch. Use `--fill` to auto-populate the title and body from commit messages — this implicitly pushes the branch.

```bash
glab mr create --title "Feature: description" --description "Details..."
glab mr create --fill  # Auto-fill from commits + push
glab mr create --fill --yes  # Skip all prompts
glab mr create --target-branch develop --draft --reviewer user1 --label enhancement
glab mr create --related-issue 42 --copy-issue-labels  # Link to issue, copy its labels
glab mr create --title "Fix login" --template bug_fix --yes
```

Flags:
- `--title TEXT` -- MR title
- `--description TEXT` -- Description (`"-"` opens editor)
- `--fill` -- Auto-populate from commits. Implicitly sets `--push` to true.
- `--fill-commit-body` -- Fill description with each commit body (requires `--fill`)
- `--push` -- Push committed changes after creating
- `--draft` -- Mark as draft
- `--wip` -- Mark as draft (alias)
- `--template NAME` -- Use a local `.gitlab/merge_request_templates/` template (`.md` optional; requires v1.93.0+)
- `--recover` -- Save/restore options after a failed create (experimental)
- `--no-editor` -- Do not open an editor for description prompts
- `--create-source-branch` -- Create source branch on remote if it does not exist
- `--source-branch NAME` -- Source branch (default: current)
- `--target-branch NAME` -- Target branch
- `--head OWNER/REPO` -- Head repository for cross-repo MRs. Accepts `OWNER/REPO`, `GROUP/NAMESPACE/REPO`, project ID, or URL.
- `--assignee USER` -- Assign usernames
- `--reviewer USER` -- Request review
- `--label NAME` -- Add labels
- `--milestone VALUE` -- Milestone
- `--related-issue IID` -- Create MR for an issue (uses issue title if `--title` not given)
- `--copy-issue-labels` -- Copy labels from issue (with `--related-issue`)
- `--squash-before-merge` -- Squash on merge (overrides project default)
- `--remove-source-branch` -- Remove source branch on merge (overrides project default)
- `--allow-collaboration` -- Allow commits from other members (overrides project default)
- `--auto-merge` -- Set auto-merge on the created MR (requires v1.90.0+)
- `--signoff` -- Append DCO signoff to the description
- `--yes` -- Skip confirmation

### Update

Update an MR's title, description, labels, reviewers, or target branch. Modifier syntax for `--assignee` and `--reviewer`: `+user` to add, `!user` or `-user` to remove, plain name replaces all.

```bash
glab mr update 123 --title "New title" --ready
glab mr update 123 --assignee +user2 --reviewer +reviewer1
glab mr update 123 --label new-label --unlabel old-label
glab mr update 123 --draft  # Convert to draft
glab mr update 123 --target-branch release/v2
```

Flags:
- `--title TEXT` -- New title
- `--description TEXT` -- New description
- `--fill` / `--fill-commit-body` -- Populate from commit info
- `--assignee USER` -- Modify assignees (`+`/`!`/`-` syntax)
- `--unassign` -- Remove all assignees
- `--reviewer USER` -- Modify reviewers (`+`/`!`/`-` syntax)
- `--label NAME` -- Add labels
- `--unlabel NAME` -- Remove labels
- `--milestone VALUE` -- Set milestone (`""` or `0` to clear)
- `--draft` -- Mark as draft
- `--ready` -- Mark as ready for review
- `--target-branch NAME` -- Change target branch
- `--squash-before-merge` -- Toggle squash on merge
- `--remove-source-branch` -- Toggle removal on merge
- `--lock-discussion` / `--unlock-discussion` -- Lock or unlock discussion
- `--yes` -- Skip confirmation

### Merge

Merge a merge request. **`--auto-merge` defaults to `true`** — when a pipeline is running, this queues the MR for auto-merge when checks pass. Use `--auto-merge=false` only when immediate merge is intended.

```bash
glab mr merge 123 --auto-merge=false --squash  # Merge immediately with squash
glab mr merge 123 --squash --remove-source-branch  # Auto-merge (default) + cleanup
glab mr merge 123 --sha abc1234  # Safety: merge only if HEAD matches
```

Flags:
- `--auto-merge` -- Default: `true`. Queue for auto-merge when a pipeline is running. Use `--auto-merge=false` to merge immediately.
- `--squash` -- Squash commits
- `--rebase` -- Rebase onto base before merge
- `--remove-source-branch` -- Delete source branch after merge
- `--message TEXT` -- Merge commit message
- `--squash-message TEXT` -- Squash commit message
- `--sha SHA` -- Safety check: merge only if MR HEAD matches this SHA
- `--yes` -- Skip confirmation

### Approve / Revoke

Approve or revoke (alias: `unapprove`) approval on a merge request. Supports batch approval — pass multiple IDs.

```bash
glab mr approve 123
glab mr approve 123 345  # Batch approve
glab mr approve 123 --sha abc1234  # Safety: verify HEAD before approving
glab mr revoke 123
```

Flags:
- `--sha SHA` -- Safety check: approve only if MR HEAD matches this SHA

Self-approval restrictions are server-side GitLab settings, not CLI-enforced.

### Approvers

List approval requirements and current approval status for a merge request.

```bash
glab mr approvers 123
glab mr approvers 123 --output json --jq '.rules[] | {name, approvals_required, approved}'
```

Flags: `--output text|json`, `--jq`.

### Diff

View the file changes in a merge request as a unified diff. There is no `--name-only` flag — use the API to list changed files.

```bash
glab mr diff 123 --color=never  # Recommended for agents
glab mr diff 123 --raw  # Raw diff format (pipeable)
glab api projects/:fullpath/merge_requests/123/diffs | jq '.[].new_path'  # List changed files
```

Flags:
- `--color VALUE` -- `always`, `never`, `auto` (default: `auto`). Use `--color=never` for agent consumption.
- `--raw` -- Raw diff format, suitable for piping

### Issues

List issues that would be closed by a merge request.

```bash
glab mr issues 123
```

### Checkout

Check out an MR's branch locally for testing or further development. Accepts MR ID, branch name, or full MR URL.

```bash
glab mr checkout 123
glab mr checkout 123 --branch my-local-name
glab mr checkout 123 --force  # Reset diverged local branch to remote
```

Flags:
- `--branch NAME` -- Custom local branch name
- `--set-upstream-to REMOTE/BRANCH` -- Set tracking to a specific remote branch
- `--force` -- Reset local branch to remote if it diverged; the command refuses if working tree changes would be lost

### Rebase

Rebase an MR's source branch onto its target. This is a **server-side async operation** (API call, not local `git rebase`) — returns 403 without push access to the source branch.

```bash
glab mr rebase 123
glab mr rebase 123 --skip-ci  # Skip CI pipeline on rebase
```

### Notes and Discussions

Use explicit `mr note` subcommands for comments and discussion management. These subcommands are experimental in `glab` 1.106.0 and were added gradually: `list`/`resolve`/`reopen` in v1.90, `create` in v1.93, `--reply` and diff-comment flags in v1.94, `update`/`delete` in v1.98.1, and `--resolvable` in v1.101. Verify `glab mr note <subcommand> --help` if a flag fails.

```bash
# General discussion comment
glab mr note create 123 --message "LGTM, approving."

# Skip if an identical note already exists
glab mr note create 123 --unique --message "Status: CI passed"

# Non-resolvable status note (does not block "All threads must be resolved")
glab mr note create 123 --message "Build status: green" --resolvable=false

# Reply to an existing discussion thread (full ID or unique 8+ char prefix)
glab mr note create 123 --reply abc12345 --message "I agree."

# Diff comments on the latest MR diff version
glab mr note create 123 --file src/main.go --line 42 --message "Handle this error."
glab mr note create 123 --file src/main.go --line 10:15 --message "Extract this block."
glab mr note create 123 --file src/main.go --old-line 7 --message "Why remove this?"
glab mr note create 123 --file src/main.go --message "File-level comment."
```

Flag rules:
- `--line` and `--old-line` require `--file` and cannot be used together.
- `--file`, `--reply`, and `--unique` are mutually exclusive.
- `--resolvable=false` cannot be combined with `--reply` or `--file`.

List, edit, delete, resolve, and reopen discussions:

```bash
glab mr note list 123 --state unresolved
glab mr note list 123 --type diff --file src/main.go
glab mr note list 123 --output json --jq '.[].notes[].body'
glab mr note update 123 <note-id> --message "Updated comment"
glab mr note delete 123 <note-id> --yes
glab mr note resolve 123 <discussion-id-or-prefix>
glab mr note reopen 123 <discussion-id-or-prefix>
```

`mr note list` has no pagination flags; use `--state`, `--type`, and `--file` filters to reduce output before requesting JSON.

When passing both an MR and a note or discussion identifier, put the MR IID/branch first and the note/discussion ID last. `note update` and `note delete` use numeric note IDs. `note resolve` and `note reopen` accept a full discussion ID, an unambiguous 8+ character discussion ID prefix, or a note ID. These subcommands are experimental.

### Close / Reopen / Delete

```bash
glab mr close 123
glab mr close 123 456  # Close multiple
glab mr close username:branch  # Close by branch
glab mr reopen 123
glab mr delete 123
glab mr delete 123,456  # Comma-separated IDs
```

### Other

```bash
glab mr todo 123  # Add to your to-do list
glab mr subscribe 123  # Subscribe to notifications
glab mr unsubscribe 123
```

## Workflows

### Reviewing an MR

1. **Read the MR description and metadata:**
   ```bash
   glab mr view 123
   ```

   For unresolved discussion review:
   ```bash
   glab mr view 123 --unresolved
   ```

2. **List changed files** (no `--name-only` on `mr diff` — use the API):
   ```bash
   glab api projects/:fullpath/merge_requests/123/diffs | jq '.[].new_path'
   ```

3. **Read the diff:**
   ```bash
   glab mr diff 123 --color=never
   ```

4. **Check CI status:**
   ```bash
   glab ci status --compact
   ```

5. **Approve or leave feedback:**
   ```bash
   glab mr approve 123
   glab mr note create 123 --message "Requested changes: ..."
   ```

### Creating an MR for the current branch

1. **Verify the branch has commits ahead of the target:**
   ```bash
   git log --oneline main..HEAD
   ```

2. **Push the branch if not yet pushed** (skip if using `--fill`, which pushes automatically):
   ```bash
   git push -u origin HEAD
   ```

3. **Create the MR:**
   ```bash
   glab mr create --fill
   ```

   Or with explicit title and description:
   ```bash
   glab mr create --title "Feature: description" --description "## Summary\n- Change 1\n- Change 2"
   ```

## Troubleshooting

- **Self-approval rejected** -- The GitLab project has "Prevent MR approval by the author" enabled. Another user must approve.
- **Branch protection rejects merge** -- The target branch requires additional approvals or passing CI. Check `glab mr approvers` and `glab ci status`.
- **Rebase returns 403** -- `mr rebase` is a server-side API call. The authenticated user needs push access to the MR's source branch.

## Documentation

- [Merge requests](https://docs.gitlab.com/ee/user/project/merge_requests/) -- GitLab merge request documentation
- [glab mr](https://docs.gitlab.com/cli/mr/) -- CLI command reference for merge requests
