"""Tests for the GitHub README fetcher."""

import pytest

from readme_score.fetcher import _is_github_url, _parse_github_url, fetch_readme


class TestParseGitHubUrl:
    """Tests for GitHub URL parsing."""

    def test_valid_url(self):
        owner, repo = _parse_github_url("https://github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_valid_url_with_trailing_slash(self):
        owner, repo = _parse_github_url("https://github.com/owner/repo/")
        assert owner == "owner"
        assert repo == "repo"

    def test_valid_url_with_whitespace(self):
        owner, repo = _parse_github_url("  https://github.com/owner/repo  ")
        assert owner == "owner"
        assert repo == "repo"

    def test_invalid_url_no_repo(self):
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            _parse_github_url("https://github.com/owner")

    def test_invalid_url_not_github(self):
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            _parse_github_url("https://gitlab.com/owner/repo")

    def test_invalid_url_with_path(self):
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            _parse_github_url("https://github.com/owner/repo/tree/main")


class TestIsGitHubUrl:
    """Tests for GitHub URL detection."""

    def test_github_url(self):
        assert _is_github_url("https://github.com/owner/repo") is True

    def test_raw_text(self):
        assert _is_github_url("# My README\nSome content") is False

    def test_other_url(self):
        assert _is_github_url("https://gitlab.com/owner/repo") is False

    def test_empty_string(self):
        assert _is_github_url("") is False


class TestFetchReadme:
    """Tests for the main fetch_readme function."""

    @pytest.mark.asyncio
    async def test_raw_text_passthrough(self):
        content, label = await fetch_readme("# My Project\nThis does stuff")
        assert content == "# My Project\nThis does stuff"
        assert label == "pasted-readme"

    @pytest.mark.asyncio
    async def test_empty_text_raises(self):
        with pytest.raises(ValueError, match="Empty README"):
            await fetch_readme("")

    @pytest.mark.asyncio
    async def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="Empty README"):
            await fetch_readme("   ")

    @pytest.mark.asyncio
    async def test_invalid_github_url_raises(self):
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            await fetch_readme("https://github.com/just-owner")
