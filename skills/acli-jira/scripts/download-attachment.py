# /// script
# requires-python = ">=3.11"
# ///
"""Download a Jira Cloud attachment by its content URL.

Usage:
    uv run scripts/download-attachment.py <url> -o <output_path>

The content URL is available in the attachment metadata returned by:
    acli jira workitem view PROJ-123 --fields attachment --json

Requires JIRA_API_TOKEN environment variable. Site and email are read from
the current acli profile (~/.config/acli/jira_config.yaml).
"""

import argparse
import base64
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import NamedTuple

# --- Constants ---

ACLI_CONFIG_PATH = Path.home() / ".config" / "acli" / "jira_config.yaml"
TOKEN_ENV_VAR = "JIRA_API_TOKEN"
TOKEN_MANAGEMENT_URL = "https://id.atlassian.com/manage-profile/security/api-tokens"

ATTACHMENT_ID_RE = re.compile(r"/attachment/content/(\d+)")
PROFILE_BLOCK_RE = re.compile(r"(?=\n\s*-\s+site:)")
DOWNLOAD_URL_TEMPLATE = (
    "https://{site}/rest/api/3/attachment/content/{attachment_id}?redirect=false"
)

HTTP_ERROR_LABELS: dict[int, str] = {
    401: "API token expired or invalid",
    403: "Permission denied",
    404: "Attachment not found",
}


# --- Data types ---


class AcliProfile(NamedTuple):
    """Jira Cloud profile from acli configuration."""

    site: str
    email: str


class FailedAttempt(NamedTuple):
    """Record of a failed download attempt against a profile."""

    profile: AcliProfile
    error: str


# --- Token and profile resolution ---


def resolve_token() -> str | None:
    """Read JIRA_API_TOKEN, handling GitLab CI File variables (value is a file path)."""
    value = os.environ.get(TOKEN_ENV_VAR)
    if not value:
        return None
    # GitLab CI File variables store the token at a file path
    token_path = Path(value)
    if token_path.is_file():
        return token_path.read_text(encoding="utf-8").strip()
    return value


def resolve_acli_profiles() -> list[AcliProfile]:
    """Read all acli profiles, current profile first.

    Parses ~/.config/acli/jira_config.yaml to extract (site, email) pairs.
    Profiles without an email are skipped. In multi-profile configs, the
    current profile (matched by cloud_id:account_id) is returned first.
    """
    if not ACLI_CONFIG_PATH.is_file():
        return []
    content = ACLI_CONFIG_PATH.read_text(encoding="utf-8")

    cp_match = re.search(r"current_profile:\s*(\S+)", content)
    current_id = cp_match.group(1) if cp_match else None

    profiles: list[tuple[AcliProfile, bool]] = []
    for block in PROFILE_BLOCK_RE.split(content):
        site_m = re.search(r"site:\s*(\S+)", block)
        email_m = re.search(r"email:\s*(\S+)", block)
        if not site_m or not email_m:
            continue

        is_current = False
        if current_id:
            cloud_m = re.search(r"cloud_id:\s*(\S+)", block)
            account_m = re.search(r"account_id:\s*(\S+)", block)
            if cloud_m and account_m:
                is_current = f"{cloud_m.group(1)}:{account_m.group(1)}" == current_id

        profiles.append(
            (
                AcliProfile(site=site_m.group(1), email=email_m.group(1)),
                is_current,
            )
        )

    profiles.sort(key=lambda p: not p[1])
    return [profile for profile, _ in profiles]


# --- Attachment operations ---


def extract_attachment_id(url: str) -> str:
    """Extract the numeric attachment ID from a Jira attachment content URL.

    Raises:
        ValueError: If the URL does not match the expected format.
    """
    match = ATTACHMENT_ID_RE.search(url)
    if not match:
        raise ValueError(
            f"Cannot extract attachment ID from URL: {url}\n"
            "Expected format: https://.../rest/api/3/attachment/content/<id>"
        )
    return match.group(1)


def download_attachment(
    attachment_id: str,
    profiles: list[AcliProfile],
    token: str,
    output: Path,
) -> list[FailedAttempt]:
    """Try downloading an attachment using each profile in order.

    Returns an empty list on success, or a list of FailedAttempt records
    if all profiles fail.
    """
    failures: list[FailedAttempt] = []

    for profile in profiles:
        url = DOWNLOAD_URL_TEMPLATE.format(
            site=profile.site, attachment_id=attachment_id
        )
        credentials = base64.b64encode(f"{profile.email}:{token}".encode()).decode(
            "ascii"
        )
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Basic {credentials}")

        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
        except urllib.error.HTTPError as exc:
            label = HTTP_ERROR_LABELS.get(exc.code, f"HTTP {exc.code}")
            failures.append(FailedAttempt(profile=profile, error=label))
            continue

        output.write_bytes(data)
        print(f"Downloaded {len(data)} bytes to {output}")
        return []

    return failures


def report_failure(failures: list[FailedAttempt]) -> None:
    """Print a detailed error report for failed download attempts."""
    print("Error: Download failed. Attempted profiles:", file=sys.stderr)
    for attempt in failures:
        print(
            f"  - {attempt.profile.site} ({attempt.profile.email}): {attempt.error}",
            file=sys.stderr,
        )

    errors = {attempt.error for attempt in failures}
    hints: list[str] = []
    if "API token expired or invalid" in errors:
        hints.append(f"Regenerate token: {TOKEN_MANAGEMENT_URL}")
    if "Attachment not found" in errors:
        hints.append(
            "Verify attachment exists: "
            "acli jira workitem attachment list --key <ISSUE-KEY> --json"
        )

    if hints:
        for hint in hints:
            print(hint, file=sys.stderr)


# --- Entry point ---


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a Jira Cloud attachment.")
    parser.add_argument("url", help="Attachment content URL from Jira API metadata")
    parser.add_argument(
        "-o", "--output", required=True, type=Path, help="Output file path"
    )
    parser.add_argument("--site", help="Jira site hostname (default: from acli config)")
    args = parser.parse_args()

    token = resolve_token()
    if not token:
        print(
            f"Error: '{TOKEN_ENV_VAR}' environment variable is not set.\n"
            f"Create a token: {TOKEN_MANAGEMENT_URL}\n"
            f'Set it: export {TOKEN_ENV_VAR}="<token>"',
            file=sys.stderr,
        )
        sys.exit(1)

    profiles = resolve_acli_profiles()
    if args.site:
        profiles = [p for p in profiles if p.site == args.site]
        if not profiles:
            print(
                f"Error: No acli profile found for site '{args.site}'.\n"
                "Authenticate acli for this site: acli jira auth login",
                file=sys.stderr,
            )
            sys.exit(1)

    if not profiles:
        print(
            "Error: No usable authenticated acli profiles found.\n"
            "Authenticate by running 'acli jira auth login'",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        attachment_id = extract_attachment_id(args.url)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    failures = download_attachment(attachment_id, profiles, token, args.output)
    if failures:
        report_failure(failures)
        sys.exit(1)


if __name__ == "__main__":
    main()
