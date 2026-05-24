# ADF Formatting

Jira Cloud uses Atlassian Document Format (ADF) for rich text in descriptions and comments. Plain markdown syntax produces literal text — use ADF JSON for any formatting beyond plain text.

Pass ADF JSON to `--body`, `--body-file`, `--description`, or `--description-file`. `acli` auto-detects the format (valid JSON is treated as ADF; everything else is plain text).

## When to Use ADF vs Plain Text

**Plain text** is the default. Use it for short updates where formatting adds no value:

```bash
acli jira workitem comment create --key PROJ-123 --body "Investigated the build failure. Root cause was a missing dependency on numpy>=2.0. Fixed in commit abc123."
```

**ADF JSON** is for content that benefits from structure — headings, lists, code blocks, tables, panels, or mentions:

```bash
acli jira workitem comment create --key PROJ-123 --body-file investigation-report.json
acli jira workitem edit --key PROJ-123 --description-file description.json
```

Guidelines:
- **Use plain text** for status updates, short comments, simple descriptions — most agent interactions
- **Use ADF** for investigation reports, structured summaries, descriptions with code samples, content with sections and checklists
- Construct ADF JSON in a temporary file and use `--body-file` or `--description-file`. Inline `--body` with ADF is practical only for single-paragraph formatting.

## Usage with acli

For short formatted content, pass ADF JSON directly to `--body` or `--description`:

```bash
acli jira workitem comment create --key PROJ-123 --body '{"type":"doc","version":1,"content":[{"type":"paragraph","content":[{"type":"text","text":"Done.","marks":[{"type":"strong"}]}]}]}'
```

For longer content, write ADF JSON to a file and use `--body-file` or `--description-file`:

```bash
acli jira workitem comment create --key PROJ-123 --body-file comment.json
acli jira workitem edit --key PROJ-123 --description-file description.json
```

## ADF Rules

- Root node is always `{"type": "doc", "version": 1, "content": [...]}`
- Text goes inside block nodes (paragraph, heading) — never directly in `doc.content`
- The `code` mark cannot combine with other marks — use it alone (Jira rejects `code` combined with `strong`, `em`, etc.)
- `localId` values must be unique within the document (for taskList/taskItem)
- Malformed ADF returns an `INVALID_INPUT` error from Jira

## Document Structure

Every ADF document has the same root:

```json
{
  "type": "doc",
  "version": 1,
  "content": [ ... ]
}
```

`content` contains an array of block-level nodes. Each block node may contain inline nodes (text, hardBreak) or other block nodes (nested lists).

## Block Nodes

### Paragraph

```json
{
  "type": "paragraph",
  "content": [
    { "type": "text", "text": "Plain text." }
  ]
}
```

### Heading

Levels 1-6. Use `attrs.level`:

```json
{
  "type": "heading",
  "attrs": { "level": 2 },
  "content": [{ "type": "text", "text": "Section Title" }]
}
```

### Bullet List

```json
{
  "type": "bulletList",
  "content": [
    {
      "type": "listItem",
      "content": [
        { "type": "paragraph", "content": [{ "type": "text", "text": "Item one" }] }
      ]
    },
    {
      "type": "listItem",
      "content": [
        { "type": "paragraph", "content": [{ "type": "text", "text": "Item two" }] }
      ]
    }
  ]
}
```

### Ordered List

Same structure as bullet list, with `orderedList` type:

```json
{ "type": "orderedList", "content": [{ "type": "listItem", "content": [...] }] }
```

### Nested Lists

Nest a list inside a `listItem` alongside its paragraph:

```json
{
  "type": "listItem",
  "content": [
    { "type": "paragraph", "content": [{ "type": "text", "text": "Parent" }] },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Child" }] }]
        }
      ]
    }
  ]
}
```

Bullet and ordered lists can be mixed at any nesting level.

### Code Block

```json
{
  "type": "codeBlock",
  "attrs": { "language": "python" },
  "content": [{ "type": "text", "text": "def hello():\n    print(\"Hello!\")" }]
}
```

Omit `attrs` or `language` for a plain code block.

### Blockquote

```json
{
  "type": "blockquote",
  "content": [
    { "type": "paragraph", "content": [{ "type": "text", "text": "Quoted text." }] }
  ]
}
```

### Horizontal Rule

```json
{ "type": "rule" }
```

### Table

Tables require three node types: `table` > `tableRow` > `tableHeader` or `tableCell`. Each cell contains block nodes (typically paragraphs).

```json
{
  "type": "table",
  "attrs": { "isNumberColumnEnabled": false, "layout": "default" },
  "content": [
    {
      "type": "tableRow",
      "content": [
        {
          "type": "tableHeader",
          "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Column A" }] }]
        },
        {
          "type": "tableHeader",
          "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Column B" }] }]
        }
      ]
    },
    {
      "type": "tableRow",
      "content": [
        {
          "type": "tableCell",
          "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Value 1" }] }]
        },
        {
          "type": "tableCell",
          "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Value 2" }] }]
        }
      ]
    }
  ]
}
```

Use `tableHeader` for header row cells and `tableCell` for data row cells. Marks and other inline formatting work inside cells.

### Panel

Colored callout boxes with icons. Panel types: `info`, `note`, `warning`, `error`, `success`.

```json
{
  "type": "panel",
  "attrs": { "panelType": "info" },
  "content": [
    { "type": "paragraph", "content": [{ "type": "text", "text": "Informational message." }] }
  ]
}
```

### Action Items (Task List)

Interactive checklists with TODO/DONE states. Each item requires a unique `localId`. Marks (bold, italic, etc.) work inside task items.

```json
{
  "type": "taskList",
  "attrs": { "localId": "list-1" },
  "content": [
    {
      "type": "taskItem",
      "attrs": { "localId": "task-1", "state": "TODO" },
      "content": [{ "type": "text", "text": "Unchecked task" }]
    },
    {
      "type": "taskItem",
      "attrs": { "localId": "task-2", "state": "DONE" },
      "content": [{ "type": "text", "text": "Completed task" }]
    }
  ]
}
```

`localId` values must be unique within the document. Use any string (e.g., `"task-1"`, a UUID).

## Inline Nodes

### Text with Marks

Apply formatting via the `marks` array on text nodes:

```json
{ "type": "text", "text": "bold text", "marks": [{ "type": "strong" }] }
```

Available marks:
- `strong` -- Bold
- `em` -- Italic
- `strike` -- Strikethrough
- `code` -- Inline code (use alone — cannot combine with other marks)
- `underline` -- Underline
- `link` -- Hyperlink (requires `attrs.href`)

**Combining marks:** Multiple marks can be applied to the same text node by adding them to the array:

```json
{ "type": "text", "text": "bold italic", "marks": [{ "type": "strong" }, { "type": "em" }] }
```

### Link

Use the `link` mark with `attrs.href`:

```json
{
  "type": "text",
  "text": "Atlassian",
  "marks": [{ "type": "link", "attrs": { "href": "https://www.atlassian.com" } }]
}
```

Links can be combined with other marks (e.g., bold link):

```json
{
  "type": "text",
  "text": "Bold link",
  "marks": [{ "type": "strong" }, { "type": "link", "attrs": { "href": "https://example.com" } }]
}
```

### Mention

Reference a Jira user inline. Requires the user's **account ID** — email addresses and display names render as "@unknown".

```json
{
  "type": "mention",
  "attrs": {
    "id": "712020:50c77ee2-9fb9-4f2d-bdd1-939ff6d07d0a",
    "text": "@Display Name"
  }
}
```

The `text` field controls what is displayed; `id` must be the account ID.

To get a user's account ID, extract it from issue metadata (assignee, reporter, creator, or comment author) via `--json` output:

```bash
acli jira workitem view PROJ-123 --fields assignee --json
# → fields.assignee.accountId
```

### Emoji

Insert emoji by short name:

```json
{ "type": "emoji", "attrs": { "shortName": ":thumbsup:" } }
```

### Hard Break

Line break within a paragraph (without starting a new paragraph):

```json
{
  "type": "paragraph",
  "content": [
    { "type": "text", "text": "Line one" },
    { "type": "hardBreak" },
    { "type": "text", "text": "Line two" }
  ]
}
```

## Documentation

- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/) -- Official document structure, nodes, marks, and JSON schema link
