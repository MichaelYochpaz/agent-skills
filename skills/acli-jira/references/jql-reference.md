# JQL Reference

Construction rules, operators, functions, and field guidance for writing JQL queries.

## Quick Rules

- Single-quote field names containing spaces: `'Story Points' > 5`
- Double-quote string values: `status = "In Progress"`
- No quotes for single-word values: `status = Done`
- Double-quote reserved words used as values: `summary ~ "order"`
- Null checks: use `IS EMPTY` / `IS NOT EMPTY` (preferred) or `= EMPTY` / `!= EMPTY` (also valid)
- `!= value` excludes issues where the field is empty — to include them: `field != value OR field IS EMPTY`
- Precedence: `NOT` > `AND` > `OR` — use parentheses to override: `(A OR B) AND C`
- `ORDER BY` goes last: `... ORDER BY priority DESC, created ASC`
- Escape special characters in text search with backslash: `summary ~ "foo\\*bar"`

## Operators

### Comparison (`=`, `!=`, `>`, `<`, `>=`, `<=`)

Work with date, number, priority, version, status, and user fields. For text fields, `=` is exact match only.

```
priority >= High
created >= "2025-01-01"
```

### Text (`~`, `!~`)

Fuzzy match on summary, description, comment, and text custom fields. Supports wildcards (`*`) and exact phrases.

```
summary ~ "dependency conflict"
summary ~ "build*"
description ~ "\"exact phrase\""
```

### List (`IN`, `NOT IN`)

Work with any field that supports `=`.

```
status IN ("Open", "In Progress", "In Review")
fixVersion NOT IN ("1.0", "2.0")
```

### Null (`IS`, `IS NOT`)

Used with `EMPTY` or `NULL` (interchangeable).

```
assignee IS EMPTY
fixVersion IS NOT EMPTY
```

### Historical (`WAS`, `WAS NOT`, `WAS IN`, `WAS NOT IN`)

Only supported on: Assignee, Fix Version, Priority, Reporter, Resolution, Status.

Predicates: `AFTER`, `BEFORE`, `BY`, `DURING`, `ON`.

```
status WAS "In Progress" BEFORE "2025-01-01"
assignee WAS currentUser()
priority WAS IN ("High", "Highest") DURING ("2025-01-01", "2025-06-01")
```

### Changed (`CHANGED`)

Same fields as WAS. Predicates: `AFTER`, `BEFORE`, `BY`, `DURING`, `ON`, `FROM`, `TO`.

```
status CHANGED FROM "Open" TO "Done" AFTER -7d
status CHANGED BY currentUser()
priority CHANGED AFTER startOfMonth()
```

### Operator / Field-Type Compatibility

| Operator | Text | Date/Number | Status/User/Type | Version/Priority | Labels/Components |
|---|---|---|---|---|---|
| `=`, `!=` | exact match | yes | yes | yes | yes |
| `~`, `!~` | fuzzy search | — | — | — | — |
| `>`, `<`, `>=`, `<=` | — | yes | — | yes | — |
| `IN`, `NOT IN` | — | yes | yes | yes | yes |
| `IS`, `IS NOT` | yes | yes | yes | yes | yes |
| `WAS`, `CHANGED` | — | — | status, user | version, priority | — |

## Functions

### User

- `currentUser()` — the authenticated user. Use with `=`/`!=`:
  `assignee = currentUser()`
- `membersOf("group")` — all members of a group. Use with `IN`/`NOT IN`:
  `assignee IN membersOf("developers")`

### Date / Time

- `now()` — current timestamp:
  `due < now()`
- `startOfDay()`, `endOfDay()` — midnight boundaries
- `startOfWeek()`, `endOfWeek()` — week boundaries (Saturday is last day by default)
- `startOfMonth()`, `endOfMonth()`, `startOfYear()`, `endOfYear()`

The `startOf*`/`endOf*` functions accept an offset: `(+/-)nn(y|M|w|d|h|m)` — uppercase `M` = months, lowercase `m` = minutes. Offset defaults to the function's natural period: `endOfDay("+1")` is equivalent to `endOfDay("+1d")`.

```
created >= startOfMonth("-1")
due < endOfWeek()
updated >= startOfDay("-3")
```

**Relative dates** (shorthand, no function needed): `-7d`, `-1w`, `-2h`, `-30m`. Pattern: `(+/-)N(m|h|d|w)`.

```
updated >= -7d
created >= -1w
```

**Date literals** in double quotes: `"2025-01-15"` or `"2025-01-15 14:30"`.

### Sprint

Use with `IN`/`NOT IN`:

- `openSprints()` — currently active sprints:
  `sprint in openSprints()`
- `closedSprints()` — completed sprints:
  `sprint in closedSprints()`
- `futureSprints()` — planned, not yet started:
  `sprint in futureSprints()`

### Work Item

- `linkedWorkItems(key)` — issues linked to a specific issue. Use with `IN`:
  `issue in linkedWorkItems(PROJ-123)`
- `linkedWorkItems(key, "link-type")` — restrict by link type:
  `issue in linkedWorkItems(PROJ-123, "blocks")`
- `workItemHistory()` — issues you recently viewed (up to 50):
  `issue in workItemHistory()`

## Field Guide

### `parent` vs `"Epic Link"`

Use `parent` for all new queries. `Epic Link` was retired February 2024. Existing filters still work, but new filters must use `parent`. Works in both team-managed and company-managed spaces.

```
parent = PROJ-100
parent IN (PROJ-100, PROJ-200)
```

### `statusCategory` vs `status`

`statusCategory` groups all workflow statuses into three values: `"To Do"`, `"In Progress"`, `"Done"`. More portable than exact status names, which vary per workflow. Use when querying across projects or when exact status names are unknown.

```
statusCategory = Done
statusCategory != "In Progress"
```

### `resolution` vs `statusCategory`

`resolution` does not exist in service team-managed spaces. Use `statusCategory = Done` as a portable alternative to check whether an issue is resolved.

### Custom Fields

Reference by name in quotes: `"Story Points" > 5`. To discover exact field names, use `acli jira workitem view KEY --fields '*all' --json` on a sample issue.

### `text`

Virtual master-field that searches summary, description, environment, comments, and free-text custom fields simultaneously. Only supports `~`.

```
text ~ "dependency conflict"
text ~ "\"exact phrase\""
```

## External References

- [JQL fields](https://support.atlassian.com/jira-service-management-cloud/docs/jql-fields/)
- [JQL operators](https://support.atlassian.com/jira-service-management-cloud/docs/jql-operators/)
- [JQL keywords](https://support.atlassian.com/jira-service-management-cloud/docs/jql-keywords/)
- [JQL functions](https://support.atlassian.com/jira-software-cloud/docs/jql-functions/)
