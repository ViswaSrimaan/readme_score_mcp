"""GitHub README fetcher with fallback resolution."""

import re
from urllib.parse import urlparse

import httpx

# Maximum README size to accept (500KB guard)
MAX_README_BYTES = 500 * 1024

# Timeout for HTTP requests
REQUEST_TIMEOUT = 15.0

# Resolution order for raw GitHub URLs
_RAW_URL_PATTERNS = [
    "https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
    "https://raw.githubusercontent.com/{owner}/{repo}/master/README.md",
    "https://raw.githubusercontent.com/{owner}/{repo}/main/readme.md",
    "https://raw.githubusercontent.com/{owner}/{repo}/main/README.rst",
]

_GITHUB_URL_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/?$"
)


def _parse_github_url(url: str) -> tuple[str, str]:
    """Extract owner and repo from a GitHub URL.

    Returns:
        Tuple of (owner, repo).

    Raises:
        ValueError: If the URL doesn't match the expected GitHub format.
    """
    match = _GITHUB_URL_RE.match(url.strip().rstrip("/"))
    if not match:
        raise ValueError(
            f"Invalid GitHub URL: {url}\n"
            "Expected format: https://github.com/owner/repo"
        )
    return match.group("owner"), match.group("repo")


def _is_github_url(source: str) -> bool:
    """Check if a source string looks like a GitHub URL."""
    return source.strip().startswith("https://github.com/")


async def _fetch_from_github(owner: str, repo: str) -> str:
    """Try each raw URL pattern and return the first successful response.

    Raises:
        ValueError: If no README could be found at any of the tried URLs.
    """
    tried_urls = []
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        for pattern in _RAW_URL_PATTERNS:
            url = pattern.format(owner=owner, repo=repo)
            tried_urls.append(url)
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    content = resp.text
                    if len(content.encode("utf-8")) > MAX_README_BYTES:
                        raise ValueError(
                            f"README from {owner}/{repo} exceeds {MAX_README_BYTES // 1024}KB limit. "
                            "That's less a README and more a novel."
                        )
                    return content
            except httpx.TimeoutException:
                continue
            except httpx.HTTPError:
                continue

    raise ValueError(
        f"Could not find a README for {owner}/{repo}.\n"
        f"Tried: {', '.join(tried_urls)}\n"
        "Make sure the repo exists, is public, and has a README file."
    )


async def fetch_readme(source: str) -> tuple[str, str]:
    """Fetch README content from a GitHub URL or treat as raw text.

    Args:
        source: A GitHub repo URL (https://github.com/owner/repo) or raw README text.

    Returns:
        Tuple of (readme_content, source_label).
        - For GitHub URLs: source_label is "owner/repo"
        - For raw text: source_label is "pasted-readme"

    Raises:
        ValueError: If the GitHub URL is invalid or the README cannot be fetched.
    """
    source = source.strip()

    if _is_github_url(source):
        owner, repo = _parse_github_url(source)
        content = await _fetch_from_github(owner, repo)
        return content, f"{owner}/{repo}"

    # Treat as raw README text
    if not source:
        raise ValueError("Empty README provided. There's nothing to roast here.")

    return source, "pasted-readme"
