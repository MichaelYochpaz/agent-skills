# Merge Requests

Creating, updating, merging, reviewing, and managing merge requests with `glab mr`. Write operations (`create`, `update`, `merge`, `approve`, `close`, `delete`, `note`) modify GitLab state — see Safety in the main skill body.

## Commands

### Create

Create a merge request from the current branch. Use `--fill` to auto-populate the title and body from commit messages — this implicitly pushes the branch.

```bash
glab mr create --title "Feature: description" --description "Details..."
glab mr create --fill                                     # Auto-fill from commits + push
glab mr create --fill --yes                               # Skip all prompts
glab mr create --target-branch develop --draft --reviewer user1 --label enhancement
glab mr create --related-issue 42 --copy-issue-labels     # Link to issue, copy its labels
```

Flags:
- `--title TEXT` -- MR title
- `--description TEXT` -- Description (`"-"` opens editor)
- `--fill` -- Auto-populate from commits. Implicitly sets `--push` to true.
- `--fill-commit-body` -- Fill description with each commit body (requires `--fill`)
- `--push` -- Push committed changes after creating
- `--draft` -- Mark as draft
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
- `--yes` -- Skip confirmation

### Update

Update an MR's title, description, labels, reviewers, or target branch. Modifier syntax for `--assignee` and `--reviewer`: `+user` to add, `!user` or `-user` to remove, plain name replaces all.

```bash
glab mr update 123 --title "New title" --ready
glab mr update 123 --assignee +user2 --reviewer +reviewer1
glab mr update 123 --label new-label --unlabel old-label
glab mr update 123 --draft                                # Convert to draft
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

Merge a merge request. **`--auto-merge` defaults to `true`** — this queues the MR for auto-merge when all checks pass rather than merging immediately. Use `--auto-merge=false` for immediate merge.

```bash
glab mr merge 123 --auto-merge=false --squash             # Merge immediately with squash
glab mr merge 123 --squash --remove-source-branch         # Auto-merge (default) + cleanup
glab mr merge 123 --sha abc1234                           # Safety: merge only if HEAD matches
```

Flags:
- `--auto-merge` -- Default: `true`. Queue for auto-merge. Use `--auto-merge=false` to merge immediately.
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
glab mr approve 123 345                                   # Batch approve
glab mr approve 123 --sha abc1234                         # Safety: verify HEAD before approving
glab mr revoke 123
```

Flags:
- `--sha SHA` -- Safety check: approve only if MR HEAD matches this SHA

Self-approval restrictions are server-side GitLab settings, not CLI-enforced.

### Approvers

List approval requirements and current approval status for a merge request. Text output only.

```bash
glab mr approvers 123
```

### Diff

View the file changes in a merge request as a unified diff. There is no `--name-only` flag — use the API to list changed files.

```bash
glab mr diff 123 --color=never                            # Recommended for agents
glab mr diff 123 --raw                                    # Raw diff format (pipeable)
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
```

Flags:
- `--branch NAME` -- Custom local branch name
- `--set-upstream-to REMOTE/BRANCH` -- Set tracking to a specific remote branch

### Rebase

Rebase an MR's source branch onto its target. This is a **server-side async operation** (API call, not local `git rebase`) — returns 403 without push access to the source branch.

```bash
glab mr rebase 123
glab mr rebase 123 --skip-ci                              # Skip CI pipeline on rebase
```

### Note

Add a comment to a merge request. The flag is `--message`, not `--body`.

```bash
glab mr note 123 --message "LGTM, approving."
glab mr note 123 --unique --message "Status: CI passed"   # Skip if identical comment exists
```

### Close / Reopen / Delete

```bash
glab mr close 123
glab mr close 123 456                                     # Close multiple
glab mr close username:branch                             # Close by branch
glab mr reopen 123
glab mr delete 123
glab mr delete 123,456                                    # Comma-separated IDs
```

### Other

```bash
glab mr todo 123                                          # Add to your to-do list
glab mr subscribe 123                                     # Subscribe to notifications
glab mr unsubscribe 123
```

## Workflows

### Reviewing an MR

1. **Read the MR description and metadata:**
   ```bash
   glab mr view 123
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
   glab mr note 123 --message "Requested changes: ..."
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
