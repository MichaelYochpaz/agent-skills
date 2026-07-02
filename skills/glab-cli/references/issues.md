# Issues

Creating, updating, closing, commenting, triaging, subscribing, and deleting issues with `glab issue`. Write operations (`create`, `update`, `close`, `reopen`, `note`, `subscribe`, `unsubscribe`, `delete`) modify GitLab state — see Safety in the main skill body.

## Triage Queries

Use `issue list` filters for compact planning queries. `--epic` requires `--group` and does not support pagination.

```bash
glab issue list --issue-type issue --iteration 123 --output json --jq '.[].iid'
glab issue list --group my-group --epic 456 --output-format ids
glab issue list --label bug --not-label stale --assignee @me --per-page 20
```

Key filters: `--search` with `--in title,description`, `--label`/`--not-label`, `--assignee @me`/`--not-assignee`, `--author`, `--milestone`, `--issue-type`, `--iteration`, `--closed`/`--all`, `--group` + `--epic`.

## Create

Create a new issue with a title, description, labels, and assignees. Avoid editor prompts by passing title/description or `--no-editor`.

```bash
glab issue create --title "Bug: description" --description "Details..." --label bug --assignee user1
glab issue create --title "Bug report" --template bug --yes
glab issue create --title "Investigate" --description "Details" --time-estimate 2h --no-editor
```

Key flags:
- `--title TEXT` / `--description TEXT` -- Issue title and description (`"-"` opens editor)
- `--assignee USER` / `--label NAME` -- Assign users or labels (comma-separated or repeat)
- `--milestone VALUE` / `--epic ID` -- Attach to milestone or epic
- `--linked-issues IIDs` + `--link-type VALUE` -- Link related issues (`relates_to`, `blocks`, `is_blocked_by`)
- `--linked-mr IID` -- MR IID to resolve issues in
- `--template NAME` -- Use `.gitlab/issue_templates/` template (`.md` optional; requires v1.93.0+)
- `--time-estimate TEXT` / `--time-spent TEXT` -- Set time tracking values
- `--confidential`, `--weight N`, `--due-date YYYY-MM-DD`, `--recover`, `--yes`

## Update

Update an issue's title, description, labels, assignees, milestone, visibility, weight, or due date. There is no `issue edit` command — use `issue update`.

```bash
glab issue update 123 --title "New title"
glab issue update 123 --assignee +user2                   # Add assignee
glab issue update 123 --assignee '!user1'                 # Remove assignee
glab issue update 123 --label new-label --unlabel old-label
glab issue update 123 --milestone ""                      # Remove milestone
```

Assignee modifier syntax is load-bearing: `+user` adds, `!user` or `-user` removes, and a plain username replaces all assignees. Use `--unassign` to remove all assignees.

Key flags: `--title`, `--description` (`"-"` opens a pre-filled editor), `--label`, `--unlabel`, `--milestone` (`""` or `0` clears), `--confidential`/`--public`, `--lock-discussion`/`--unlock-discussion`, `--weight`, `--due-date`.

## Close, Reopen, and Comment

`issue close` has no `--comment` flag and no close reason. Add a note separately before or after closing. `issue note` uses `--message`, not `--body`.

```bash
glab issue note 123 --message "Investigation complete."
glab issue close 123
glab issue reopen 123
```

For comment bodies containing shell metacharacters, load a file into the flag instead of inlining text in double quotes:

```bash
glab issue note 123 --message "$(<body.md)"
```

## Housekeeping

Subscribe, unsubscribe, and delete issues. All take an issue ID or URL as an argument with no command-specific flags. Aliases: `subscribe` → `sub`, `unsubscribe` → `unsub`, `delete` → `del`.

```bash
glab issue subscribe 123
glab issue unsubscribe 123
glab issue delete 123
```

## Documentation

- [GitLab issues](https://docs.gitlab.com/ee/user/project/issues/) -- Issue concepts and workflows
- [glab issue](https://docs.gitlab.com/cli/issue/) -- CLI command reference for issues
