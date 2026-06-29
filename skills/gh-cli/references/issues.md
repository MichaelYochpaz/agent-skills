# Issues

Advanced issue management with `gh issue`: issue types, sub-issues, parent relationships, blocking dependencies, and duplicate closure.

Basic issue list/view/create/edit/comment/close/status commands are in the main skill body. Write operations below modify GitHub state — confirm with the user before running.

## Version and Platform

- Requires `gh` 2.94+ for issue types, sub-issues, and blocking relationships.
- Platform: GitHub.com; GHES 3.17+ for issue types and sub-issues; GHES 3.19+ for blocking relationships.
- If a flag is missing or rejected, run `gh issue <subcommand> --help` and verify the target host supports the feature.

## Issue Types

Set or filter by issue type when the organization has issue types configured:

```bash
gh issue create --title "Crash on startup" --body "Details..." --type Bug
gh issue edit 123 --type Bug
gh issue edit 123 --remove-type
gh issue list --type Bug --json number,title,issueType
```

View structured type data:

```bash
gh issue view 123 --json number,title,issueType
```

## Sub-Issues and Parent Relationships

Create an issue under a parent, set or remove a parent, or manage a parent's sub-issues:

```bash
# Create a sub-issue under issue 100
gh issue create --title "Implement validation" --body "Details..." --parent 100

# Set or remove parent relationship
gh issue edit 123 --parent 100
gh issue edit 123 --remove-parent

# Add or remove sub-issues from a parent
gh issue edit 100 --add-sub-issue 123,124
gh issue edit 100 --remove-sub-issue 124
```

Parent and sub-issue references accept issue numbers or URLs.

View hierarchy fields:

```bash
gh issue view 100 --json number,title,parent,subIssues,subIssuesSummary
```

`subIssues` is shaped as `{ "nodes": [...], "totalCount": N }`; `gh` queries up to 100 nodes. `subIssuesSummary` is shaped as `{ "total": N, "completed": N, "percentCompleted": N }`.

## Blocking Relationships

Track blocked-by and blocking relationships:

```bash
# New issue blocked by 200 and blocking 300
gh issue create --title "Deploy service" --body "Details..." --blocked-by 200 --blocking 300

# Add or remove dependencies on an existing issue
gh issue edit 123 --add-blocked-by 200 --add-blocking 300,301
gh issue edit 123 --remove-blocked-by 200 --remove-blocking 300
```

View dependency fields:

```bash
gh issue view 123 --json number,title,blockedBy,blocking
```

`blockedBy` and `blocking` are shaped as `{ "nodes": [...], "totalCount": N }`; `gh` queries up to 50 nodes for each. Compare `nodes | length` against `totalCount` to detect CLI query truncation.

## Duplicate Closure

Close an issue as a duplicate of another issue:

```bash
gh issue close 123 --duplicate-of 456
```

`--duplicate-of` sets the close reason to `duplicate` and sends `duplicateIssueId` to GitHub's `closeIssue` mutation. If you pass `--reason` with `--duplicate-of`, use `--reason duplicate`; other reasons are rejected. Using `--reason duplicate` alone closes with duplicate state reason but does not send `duplicateIssueId`, so the CLI request does not associate the issue with an original issue.

## Documentation

- [Issue dependencies](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies) -- GitHub platform behavior for blocking and blocked-by relationships
- [Duplicate issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/administering-issues/marking-issues-or-pull-requests-as-a-duplicate) -- GitHub platform behavior for duplicate relationships
