# Pull Requests

Creating, reviewing, merging, and managing pull requests with `gh pr`. Write operations (`create`, `merge`, `review`, `close`) modify GitHub state — see Safety in the main skill body.

## Commands

### Create

Create a pull request from the current branch. If the branch hasn't been pushed yet, `gh` will prompt to push it. Use `--fill` to auto-populate the title and body from commit messages.

```bash
gh pr create --title "Feature: description" --body "Details..."
gh pr create --fill                          # Auto-fill from commits
gh pr create --base develop --draft --reviewer user1,user2 --label enhancement
```

Flags:
- `--fill` / `--fill-verbose` / `--fill-first` -- Auto-populate from commits (all, verbose, or first only)
- `--draft` -- Mark as draft (not ready for review)
- `--dry-run` -- Print details without creating (may still push git changes)
- `--base BRANCH` -- Target branch (default: repo default branch)
- `--head BRANCH` -- Source branch (default: current branch)
- `--reviewer HANDLE` -- Request reviews (comma-separated or repeated)
- `--label NAME` -- Add labels
- `--assignee LOGIN` -- Assign people (`@me` for self)
- `--milestone NAME` -- Add to milestone
- `--body-file FILE` -- Read body from file
- `--no-maintainer-edit` -- Prevent maintainers from modifying the PR

### Diff

View the file changes in a pull request as a unified diff. Use `--name-only` first to scope the changes before fetching the full diff, which can be very large.

```bash
gh pr diff 123 --name-only               # List changed files (start here)
gh pr diff 123                           # Full diff
gh pr diff 123 --patch                   # Patch format (for git apply)
```

For a token-efficient summary of changes without full patches, use the API:
```bash
gh api "repos/{owner}/{repo}/pulls/123/files" --jq '.[] | "\(.status) \(.filename) +\(.additions) -\(.deletions)"'
```

### Checks

Show the CI/CD check statuses (GitHub Actions, third-party integrations) for a pull request. Without an argument, shows checks for the current branch's PR.

```bash
gh pr checks 123
gh pr checks 123 --required              # Only required checks
gh pr checks 123 --watch --fail-fast     # Watch until complete, stop on first failure
```

Flags:
- `--required` -- Only required checks
- `--watch` -- Watch until complete
- `--fail-fast` -- Stop watching on first failure (with `--watch`)
- `--json FIELDS` -- JSON output

JSON fields: `name`, `state`, `bucket`, `link`, `description`, `event`, `workflow`, `startedAt`, `completedAt`

The `bucket` field categorizes states into: `pass`, `fail`, `pending`, `skipping`, `cancel`.

### Review

Submit a review on a pull request: approve it, request changes, or leave a general comment. For inline comments on specific file lines, use `gh api` (see below).

```bash
gh pr review 123 --approve --body "LGTM"
gh pr review 123 --request-changes --body "Please fix..."
gh pr review 123 --comment --body "Some observations..."
```

Flags:
- `--approve` / `--request-changes` / `--comment` -- Review action
- `--body TEXT` / `--body-file FILE` -- Review body

For inline review comments on specific files and lines, use `gh api`. See [API Patterns](api-patterns.md).

### Merge

Merge a pull request using squash, merge commit, or rebase strategy. Supports auto-merge (merges automatically once all requirements are met) and admin override to bypass branch protection rules.

```bash
gh pr merge 123 --squash --delete-branch
gh pr merge 123 --squash --auto          # Auto-merge when requirements are met
gh pr merge 123 --disable-auto           # Cancel pending auto-merge
```

Flags:
- `--squash` / `--merge` / `--rebase` -- Merge strategy
- `--delete-branch` -- Delete head branch after merge
- `--auto` -- Enable auto-merge when requirements are met
- `--disable-auto` -- Cancel a pending auto-merge
- `--admin` -- Merge even if requirements are not met (admin override)
- `--subject TEXT` / `--body TEXT` -- Customize merge commit message
- `--body-file FILE` -- Read merge commit body from file
- `--match-head-commit SHA` -- Safety check: merge only if head matches this SHA
- `--author-email EMAIL` -- Email for merge commit author

### Checkout

Check out a pull request's branch locally for testing or further development.

```bash
gh pr checkout 123
gh pr checkout 123 --branch my-local-name
```

Flags:
- `--branch NAME` -- Custom local branch name
- `--force` -- Discard local changes
- `--detach` -- Checkout with detached HEAD
- `--recurse-submodules` -- Update submodules after checkout

### Edit

Update a PR's title, body, base branch, labels, reviewers, assignees, milestone, or project membership. All flags can be combined in a single call.

Flags:
- `--title TEXT` / `--body TEXT` / `--body-file FILE` -- Update title or body
- `--base BRANCH` -- Change base branch
- `--add-label NAME` / `--remove-label NAME` -- Modify labels
- `--add-reviewer HANDLE` / `--remove-reviewer HANDLE` -- Modify reviewers
- `--add-assignee LOGIN` / `--remove-assignee LOGIN` -- Modify assignees
- `--milestone NAME` / `--remove-milestone` -- Set or remove milestone
- `--add-project NAME` / `--remove-project NAME` -- Modify project membership

### Comment

Add, edit, or delete comments on a pull request. Use `--edit-last` with `--create-if-none` for idempotent status updates (creates or updates a single comment).

```bash
gh pr comment 123 --body "Comment text"
gh pr comment 123 --edit-last --create-if-none --body "Status update"  # Idempotent upsert
```

Flags:
- `--body TEXT` / `--body-file FILE` -- Comment body
- `--edit-last` -- Edit your last comment instead of creating a new one
- `--create-if-none` -- With `--edit-last`: create if no comments exist
- `--delete-last --yes` -- Delete your last comment

### Ready / Draft

Toggle a PR's draft status. Mark a draft PR as ready for review, or convert a published PR back to draft with `--undo`.

```bash
gh pr ready 123                          # Mark draft as ready for review
gh pr ready 123 --undo                   # Convert back to draft
```

### Update branch

Update a PR's branch with the latest changes from the base branch. Defaults to a merge commit; use `--rebase` to rebase on top of the base branch instead.

```bash
gh pr update-branch 123                  # Merge latest base branch
gh pr update-branch 123 --rebase         # Rebase on top of base
```

### Close / Reopen

Close or reopen a pull request. Optionally leave a comment and delete the branch on close.

```bash
gh pr close 123 --comment "Closing because..." --delete-branch
gh pr reopen 123 --comment "Reopening because..."
```

### Other Commands

These commands are rarely needed. Run `gh pr <command> --help` for flags and usage.

- `gh pr revert <number>` -- Create a new PR that reverts a previously merged PR.
- `gh pr lock <number>` / `gh pr unlock <number>` -- Lock or unlock a PR's conversation thread (with optional `--reason`: `off_topic`, `resolved`, `spam`, `too_heated`).

## Workflows

### Reviewing a PR

1. **Read the PR description and metadata:**
   ```bash
   gh pr view 123 --repo owner/repo
   gh pr view 123 --json title,body,files,reviews,reviewDecision
   ```

2. **View the list of changed files:**
   ```bash
   gh pr diff 123 --name-only
   ```

3. **Read the diff:**
   ```bash
   gh pr diff 123
   ```

4. **Check CI status:**
   ```bash
   gh pr checks 123
   ```

5. **Read existing review comments** (if any, requires `gh api`):
   ```bash
   gh api "repos/{owner}/{repo}/pulls/123/comments" --jq '.[] | "\(.user.login) on \(.path):\(.line)\n\(.body)\n"'
   ```

6. **Submit the review:**
   ```bash
   gh pr review 123 --approve --body "Looks good"
   gh pr review 123 --request-changes --body "Issues found..."
   ```

   For inline comments on specific lines, see [API Patterns - Inline Reviews](api-patterns.md).

### Responding to review comments on your PR

1. **View the review summary:**
   ```bash
   gh pr view 123 --json reviews --jq '.reviews[] | "\(.author.login) \(.state): \(.body)"'
   ```

2. **Fetch inline review comments with file and line context:**
   ```bash
   gh api "repos/{owner}/{repo}/pulls/123/comments" --jq '.[] | {id, user: .user.login, path, line, body, in_reply_to_id}'
   ```

3. **Reply to a specific comment:**
   ```bash
   gh api --method POST "repos/{owner}/{repo}/pulls/123/comments/<COMMENT_ID>/replies" -f body="Reply text"
   ```

   Use the `id` from step 2. Replying to either the top-level comment or any reply in the thread appends to the same thread.

### Creating a PR for the current branch

1. **Verify the branch has commits ahead of base:**
   ```bash
   git log --oneline main..HEAD
   ```

2. **Push the branch if not yet pushed:**
   ```bash
   git push -u origin HEAD
   ```

3. **Create the PR:**
   ```bash
   gh pr create --fill
   ```

   Or with explicit title/body:
   ```bash
   gh pr create --title "Feature: description" --body "## Summary\n- Change 1\n- Change 2"
   ```

   For longer bodies, write content to a file and use `--body-file`:
   ```bash
   gh pr create --title "Feature: description" --body-file pr-body.md
   ```
