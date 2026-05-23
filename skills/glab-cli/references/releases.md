# Releases

Creating, uploading, downloading, deleting releases, and generating changelogs with `glab release` and `glab changelog`. Release commands output text only. Write operations modify GitLab state — see Safety in the main skill body.

## Commands

### Create

Create a release for a tag. **Default behavior is upsert** — updates an existing release if the tag already exists. Use `--no-update` to error instead.

```bash
glab release create v1.2.0 --notes "## What's New\n- Feature X"
glab release create v1.2.0 --notes-file CHANGELOG.md
glab release create v1.2.0 --ref main --notes "Initial release"
glab release create v1.2.0 --milestone "Sprint 5" --no-close-milestone
```

Attach files using positional arguments after the tag with `path/to/file#display-name#type` format (type: `other`, `image`, `package`, `runbook`):

```bash
glab release create v1.2.0 --notes "Release" dist/app.tar.gz#"App Archive"#package
```

Flags:
- `--name TEXT` -- Release name (defaults to tag name)
- `--ref REF` -- Create from this ref if tag does not exist. Accepts SHA, tag, or branch.
- `--tag-message TEXT` -- Message for new annotated tag
- `--notes TEXT` -- Release notes (Markdown)
- `--notes-file FILE` -- Read notes from file (`-` for stdin). Short flag is `-F`.
- `--released-at DATETIME` -- ISO 8601 datetime
- `--milestone NAME` -- Milestone titles (comma-separated or repeat). **Auto-closes associated milestones** unless `--no-close-milestone` is set.
- `--assets-links JSON` -- JSON string of asset links array
- `--no-update` -- Error if release already exists (prevents upsert)
- `--no-close-milestone` -- Prevent auto-closing milestones
- `--use-package-registry` -- Upload assets to generic package registry
- `--package-name NAME` -- Package name (default `release-assets`)

**Gotchas:**
- If the tag does not exist and `--ref` is not provided, the release is created from the default branch.
- `--milestone` auto-closes associated milestones — use `--no-close-milestone` to prevent this.

### Upload

Upload additional assets to an existing release. Same file naming syntax as `create`.

```bash
glab release upload v1.2.0 dist/app-linux.tar.gz#"Linux Build"#package dist/app-darwin.tar.gz#"macOS Build"#package
```

Flags:
- `--assets-links JSON` -- JSON string of asset links array
- `--use-package-registry` -- Upload to generic package registry
- `--package-name NAME` -- Package name (default `release-assets`)

### Download

Download release assets. Defaults to the latest release if no tag is specified. **Errors if a file already exists** in the target directory (uses `O_EXCL`).

```bash
glab release download v1.2.0
glab release download v1.2.0 --asset-name "*.tar.gz"      # Glob pattern
glab release download --dir ./artifacts                    # Download latest to specific directory
```

Flags:
- `--asset-name PATTERN` -- Download only matching assets. Uses `filepath.Match` glob patterns (e.g., `*.tar.gz`), not regex. Repeat for multiple patterns.
- `--dir PATH` -- Target directory (default `.`)

### Delete

Delete a release. **Requires `--yes` in non-interactive mode** — errors without it.

```bash
glab release delete v1.2.0 --yes
glab release delete v1.2.0 --yes --with-tag               # Also delete the Git tag
```

Flags:
- `--yes` -- Skip confirmation (required in non-interactive/CI environments)
- `--with-tag` -- Also delete the associated Git tag

### Changelog Generate

Generate a changelog using GitLab's Changelog API. Requires commits with appropriate Git trailers (default: `Changelog`). **No `-R` flag** — only works in the current repository context.

```bash
glab changelog generate --version 1.2.0
glab changelog generate --version 1.2.0 --from abc1234 --to def5678
```

Flags:
- `--version TEXT` -- Version string (semver). Auto-detected via `git describe` if omitted.
- `--config-file PATH` -- Config file path (default `.gitlab/changelog_config.yml`)
- `--date DATETIME` -- Release date, ISO 8601 datetime (e.g., `2026-01-01T00:00:00Z`)
- `--from SHA` -- Start SHA (excluded from list)
- `--to SHA` -- End SHA (included, default: HEAD of default branch)
- `--trailer NAME` -- Git trailer to use (default `Changelog`)

## Workflows

### Publishing a release

1. **Tag the release commit:**
   ```bash
   git tag v1.2.0
   git push origin v1.2.0
   ```

2. **Generate the changelog:**
   ```bash
   glab changelog generate --version 1.2.0 > CHANGELOG.md
   ```

3. **Create the release with notes and assets:**
   ```bash
   glab release create v1.2.0 --notes-file CHANGELOG.md dist/app.tar.gz#"App"#package
   ```

4. **Upload additional assets if needed:**
   ```bash
   glab release upload v1.2.0 dist/checksums.txt#"Checksums"#other
   ```

## Documentation

- [Releases](https://docs.gitlab.com/ee/user/project/releases/) -- GitLab release documentation
- [Changelog API](https://docs.gitlab.com/ee/api/repositories.html#generate-changelog-data) -- Changelog generation API
- [glab release](https://docs.gitlab.com/cli/release/) -- CLI command reference for releases
