# Discussions

Work with GitHub Discussions using `gh discussion`. The command set is preview in `gh` 2.94 and may change; verify flags with `gh discussion <subcommand> --help` before relying on automation.

Write operations (`create`, `edit`, `comment --edit`, `comment --delete`, and posting comments/replies) modify GitHub state — confirm with the user before running.

## List Discussions

List discussions in a repository. Discussions must be enabled on the repository.

```bash
gh discussion list --repo owner/repo --limit 10
gh discussion list --repo owner/repo --category "Q&A" --answered=false --json number,title,url
```

Key filters: `--state open|closed|all`, `--category`, `--author`, `--label`, `--answered`, `--search`, `--sort created|updated`, `--order asc|desc`, `--limit`, `--after`.

For list/create/edit commands, category values accept a category name or slug.

`--search` is passed through to GitHub Discussions search via GraphQL `search(type: DISCUSSION)`. Use discussion-specific qualifiers such as `in:title`, `in:body`, `in:comments`, `is:answered`, `is:unanswered`, `category:`, and `label:`.

JSON output is wrapped, not a bare array:

```text
{
  "totalCount": 123,
  "discussions": [ ... ],
  "next": "cursor-if-more-results"
}
```

`next` is omitted when there is no next page. `cursor` may appear when listing from an existing `--after` cursor. Use `.discussions[]` in `--jq` filters.

## View Discussions and Replies

```bash
# View discussion body
gh discussion view 123 --repo owner/repo

# Include comments; newest first by default
gh discussion view 123 --repo owner/repo --comments --limit 10

# View a full reply thread by comment URL or node ID
gh discussion view 'https://github.com/OWNER/REPO/discussions/123#discussioncomment-456'
gh discussion view DC_abc123 --repo owner/repo --limit 10
```

`--comments` retrieves discussion comments plus the latest 4 replies for each comment. To inspect one full reply thread, pass a comment URL or node ID as the argument.

Key JSON fields: `number`, `title`, `body`, `author`, `category`, `comments`, `answered`, `answerChosenAt`, `url`.

## Create and Edit Discussions

Non-interactive creation requires a title, body (or body file), and category:

```bash
gh discussion create --repo owner/repo --title "My question" --category "Q&A" --body "Details here"
gh discussion create --repo owner/repo --title "Release idea" --category Ideas --body-file discussion.md
```

Edit title, body, category, or labels:

```bash
gh discussion edit 123 --repo owner/repo --title "Updated title" --body-file body.md
gh discussion edit 123 --repo owner/repo --add-label bug --remove-label stale
```

## Comment and Reply

The argument determines whether a comment is top-level or a reply:

```bash
# Add a top-level comment to discussion 123
gh discussion comment 123 --repo owner/repo --body "Thanks for the context."

# Reply to a specific comment using URL or node ID
gh discussion comment 'https://github.com/OWNER/REPO/discussions/123#discussioncomment-456' --body "Reply text"
gh discussion comment DC_abc123 --repo owner/repo --body-file reply.md

# Edit or delete a comment/reply
gh discussion comment DC_abc123 --repo owner/repo --edit --body "Updated text"
gh discussion comment DC_abc123 --repo owner/repo --delete --yes
```

## GraphQL Fallback

Use `gh api graphql` when preview commands lack a needed operation or field. GitHub Discussions are primarily exposed through GraphQL, so GraphQL is the fallback for custom queries.

## Documentation

- [GitHub Discussions search syntax](https://docs.github.com/en/search-github/searching-on-github/searching-discussions) -- Qualifiers for `--search`
- [GraphQL Discussions guide](https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions) -- GraphQL fallback patterns
