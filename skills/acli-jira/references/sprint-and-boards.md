# Sprints & Boards

Commands for sprint and board context. Board and sprint IDs are required for most commands -- find them using the search and list commands below.

## Find Boards

Search for boards by project or name:

```bash
# Boards for a project
acli jira board search --project PROJ --csv

# Boards by name
acli jira board search --name "PROJ" --csv

# Filter by board type
acli jira board search --project PROJ --type scrum --csv

# JSON for board IDs (use when you need to extract IDs programmatically)
acli jira board search --project PROJ --json
```

## List Sprints

List sprints for a board (requires board ID from board search):

```bash
# Active sprints only
acli jira board list-sprints --id BOARD_ID --state active --csv

# Active and closed sprints
acli jira board list-sprints --id BOARD_ID --state active,closed --csv

# All sprints including future
acli jira board list-sprints --id BOARD_ID --state active,closed,future --csv

# JSON for sprint IDs and dates (use when you need to extract IDs programmatically)
acli jira board list-sprints --id BOARD_ID --state active --json
```

## View Sprint Details

```bash
acli jira sprint view --id SPRINT_ID
acli jira sprint view --id SPRINT_ID --json
```

## List Sprint Work Items

List issues in a sprint (requires both sprint ID and board ID):

```bash
acli jira sprint list-workitems --sprint SPRINT_ID --board BOARD_ID --csv

# With specific fields
acli jira sprint list-workitems --sprint SPRINT_ID --board BOARD_ID --fields "key,summary,status,assignee" --csv

# Filter with JQL
acli jira sprint list-workitems --sprint SPRINT_ID --board BOARD_ID --jql "assignee = currentUser()" --csv

# All items (paginated)
acli jira sprint list-workitems --sprint SPRINT_ID --board BOARD_ID --paginate --csv
```

## Typical Workflow

To find current sprint work items for a project:

```bash
# 1. Find the board ID
acli jira board search --project PROJ --json

# 2. List active sprints for that board
acli jira board list-sprints --id BOARD_ID --state active --json

# 3. List work items in the sprint
acli jira sprint list-workitems --sprint SPRINT_ID --board BOARD_ID --fields "key,summary,status,assignee" --csv
```

Alternative: use JQL search directly (simpler when you only need work items, not sprint metadata):

```bash
acli jira workitem search --jql "project = PROJ AND sprint in openSprints()" --fields "key,summary,status,assignee" --csv
```
