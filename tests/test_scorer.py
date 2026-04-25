"""Tests for the server module — prompt construction and tool logic."""

import pytest

from readme_score.server import _build_roast_instructions, VALID_INTENSITIES, VALID_FORMATS


class TestBuildRoastInstructions:
    """Tests for the prompt construction logic."""

    def test_contains_readme_content(self):
        result = _build_roast_instructions(
            "# My Project\nThis is cool", "owner/repo", "medium", "markdown"
        )
        assert "# My Project" in result
        assert "This is cool" in result

    def test_contains_source_label(self):
        result = _build_roast_instructions(
            "# Test", "owner/repo", "medium", "markdown"
        )
        assert "owner/repo" in result

    def test_contains_scoring_dimensions(self):
        result = _build_roast_instructions(
            "# Test", "test", "medium", "markdown"
        )
        assert "Purpose" in result
        assert "Installation" in result
        assert "License" in result

    def test_mild_intensity(self):
        result = _build_roast_instructions(
            "# Test", "test", "mild", "markdown"
        )
        assert "MILD" in result

    def test_medium_intensity(self):
        result = _build_roast_instructions(
            "# Test", "test", "medium", "markdown"
        )
        assert "MEDIUM" in result

    def test_savage_intensity(self):
        result = _build_roast_instructions(
            "# Test", "test", "savage", "markdown"
        )
        assert "SAVAGE" in result

    def test_markdown_format_instructions(self):
        result = _build_roast_instructions(
            "# Test", "test", "medium", "markdown"
        )
        assert "Top 3 Sins" in result
        assert "Quick Wins" in result
        assert "Verdict" in result

    def test_json_format_instructions(self):
        result = _build_roast_instructions(
            "# Test", "test", "medium", "json"
        )
        assert "JSON" in result

    def test_truncation(self):
        long_content = "x" * 15000
        result = _build_roast_instructions(
            long_content, "test", "medium", "markdown"
        )
        assert "truncated" in result
        # Should not contain the full 15000 chars
        assert len(long_content) > len(result) or "truncated" in result

    def test_no_truncation_for_short_content(self):
        short_content = "# Short README"
        result = _build_roast_instructions(
            short_content, "test", "medium", "markdown"
        )
        assert "truncated" not in result


class TestValidConstants:
    """Tests for valid intensity and format constants."""

    def test_valid_intensities(self):
        assert "mild" in VALID_INTENSITIES
        assert "medium" in VALID_INTENSITIES
        assert "savage" in VALID_INTENSITIES

    def test_valid_formats(self):
        assert "markdown" in VALID_FORMATS
        assert "json" in VALID_FORMATS
