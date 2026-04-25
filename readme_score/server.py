"""FastMCP server for readme-score — README roasting as MCP tools.

Architecture: The server handles README fetching and prompt construction.
The agent's own LLM does the actual scoring — no separate API key needed.
"""

from pathlib import Path

from fastmcp import FastMCP

from readme_score.fetcher import fetch_readme

# Load the scoring prompt template
_PROMPT_DIR = Path(__file__).parent.parent / "prompts"
_ROAST_PROMPT = (_PROMPT_DIR / "roast_system.txt").read_text(encoding="utf-8")

# Intensity modifiers
_INTENSITY_MODIFIERS = {
    "mild": (
        "ROAST INTENSITY: MILD. "
        "Be constructive with light sarcasm. Think helpful code review, "
        "not stand-up comedy. Still be honest, but gentle."
    ),
    "medium": (
        "ROAST INTENSITY: MEDIUM. "
        "Use dry wit, punchy one-liners, and direct callouts. "
        "Don't sugarcoat, but keep it professional-ish."
    ),
    "savage": (
        "ROAST INTENSITY: SAVAGE. "
        "No mercy. Maximum roast energy. Channel your inner Gordon Ramsay "
        "reviewing a microwave dinner. Still actionable, but devastatingly funny."
    ),
}

VALID_INTENSITIES = set(_INTENSITY_MODIFIERS.keys())
VALID_FORMATS = {"markdown", "json"}

# Max README chars to include (cost guard for the agent's LLM context)
DEFAULT_MAX_CHARS = 12000

mcp = FastMCP(
    "readme-score",
    instructions=(
        "README quality scorer and roaster. "
        "Use `readme_roast` to score a single README, or "
        "`readme_compare` to pit two READMEs against each other. "
        "Accepts GitHub repo URLs or raw README text. "
        "No API keys required — scoring is done by you, the agent."
    ),
)


def _build_roast_instructions(
    readme_content: str,
    source_label: str,
    intensity: str,
    response_format: str,
) -> str:
    """Build the full prompt for the agent to score a README."""
    truncated = readme_content[:DEFAULT_MAX_CHARS]
    if len(readme_content) > DEFAULT_MAX_CHARS:
        truncated += f"\n\n[... README truncated at {DEFAULT_MAX_CHARS} characters ...]"

    intensity_mod = _INTENSITY_MODIFIERS.get(intensity, _INTENSITY_MODIFIERS["medium"])

    format_instruction = ""
    if response_format == "json":
        format_instruction = (
            "\n\nIMPORTANT: Return the result as a raw JSON object matching the schema "
            "described in the scoring instructions. Do NOT wrap it in markdown code fences."
        )
    else:
        format_instruction = (
            "\n\nIMPORTANT: Format the result as a beautiful markdown report with:\n"
            f"- Title: `# 🔥 README Roast Report: {source_label}`\n"
            "- Overall score with grade and a progress bar (█░ characters)\n"
            "- A dimension scores table (Dimension | Score | Roast)\n"
            "- A 🚨 Top 3 Sins section\n"
            "- A ⚡ Quick Wins section\n"
            "- A 🎯 Verdict section"
        )

    return (
        f"Score and roast the following README from **{source_label}**.\n\n"
        f"--- SCORING INSTRUCTIONS ---\n\n"
        f"{_ROAST_PROMPT}\n\n"
        f"{intensity_mod}\n"
        f"{format_instruction}\n\n"
        f"--- README TO SCORE ---\n\n"
        f"{truncated}"
    )


@mcp.tool
async def readme_roast(
    source: str,
    response_format: str = "markdown",
    roast_intensity: str = "medium",
) -> str:
    """Score and roast a README with savage-but-constructive commentary.

    Fetches the README and returns it with scoring instructions for you to analyze.
    Scores across 7 dimensions: Purpose, Installation, Usage & Examples,
    Documentation Depth, Badges & Metadata, Contributing Guide, and License.

    Args:
        source: GitHub repo URL (https://github.com/owner/repo) or raw README text.
        response_format: Output format — 'markdown' (default) or 'json'.
        roast_intensity: How savage the roast should be — 'mild', 'medium' (default), or 'savage'.

    Returns:
        The README content with scoring instructions for the agent to process.
    """
    # Validate inputs
    response_format = response_format.lower().strip()
    if response_format not in VALID_FORMATS:
        return (
            f"❌ Invalid response_format: '{response_format}'. "
            f"Choose from: {', '.join(sorted(VALID_FORMATS))}"
        )

    roast_intensity = roast_intensity.lower().strip()
    if roast_intensity not in VALID_INTENSITIES:
        return (
            f"❌ Invalid roast_intensity: '{roast_intensity}'. "
            f"Choose from: {', '.join(sorted(VALID_INTENSITIES))}"
        )

    try:
        content, label = await fetch_readme(source)
        return _build_roast_instructions(content, label, roast_intensity, response_format)
    except ValueError as e:
        return f"❌ Error: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {type(e).__name__}: {e}"


@mcp.tool
async def readme_compare(
    source_a: str,
    source_b: str,
    response_format: str = "markdown",
) -> str:
    """Compare two READMEs head-to-head and declare a winner.

    Fetches both READMEs and returns them with comparison instructions for you
    to analyze. Scores both across 7 dimensions and produces a side-by-side report.

    Args:
        source_a: GitHub repo URL or raw README text for project A.
        source_b: GitHub repo URL or raw README text for project B.
        response_format: Output format — 'markdown' (default) or 'json'.

    Returns:
        Both README contents with comparison instructions for the agent to process.
    """
    response_format = response_format.lower().strip()
    if response_format not in VALID_FORMATS:
        return (
            f"❌ Invalid response_format: '{response_format}'. "
            f"Choose from: {', '.join(sorted(VALID_FORMATS))}"
        )

    try:
        content_a, label_a = await fetch_readme(source_a)
        content_b, label_b = await fetch_readme(source_b)
    except ValueError as e:
        return f"❌ Error: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {type(e).__name__}: {e}"

    # Truncate both
    max_chars = DEFAULT_MAX_CHARS
    trunc_a = content_a[:max_chars]
    trunc_b = content_b[:max_chars]

    intensity_mod = _INTENSITY_MODIFIERS["medium"]

    format_instruction = ""
    if response_format == "json":
        format_instruction = (
            "\n\nReturn the result as a JSON object with keys: "
            "project_a, project_b (each with full scoring), and winner."
        )
    else:
        format_instruction = (
            "\n\nFormat the result as a markdown report with:\n"
            f"- Title: `# ⚔️ README Battle: {label_a} vs {label_b}`\n"
            "- Winner declaration with scores\n"
            "- A dimension breakdown table (Dimension | Project A | Project B | Winner)\n"
            "- Individual verdicts for each project"
        )

    return (
        f"Compare these two READMEs head-to-head and declare a winner.\n\n"
        f"--- SCORING INSTRUCTIONS ---\n\n"
        f"{_ROAST_PROMPT}\n\n"
        f"{intensity_mod}\n"
        f"{format_instruction}\n\n"
        f"--- README A: {label_a} ---\n\n"
        f"{trunc_a}\n\n"
        f"--- README B: {label_b} ---\n\n"
        f"{trunc_b}"
    )


def main():
    """Entry point for the readme-score MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
