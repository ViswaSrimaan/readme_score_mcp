# readme-score — Detailed Project Plan

> A lightweight MCP server that roasts and scores README quality with savage-but-constructive commentary.  
> Plugs into any MCP-compatible agent via stdio transport.

---

## 1. Project Overview

| Field | Detail |
|---|---|
| **Project Name** | `readme-score` |
| **Type** | Python FastMCP Server |
| **Transport** | stdio (local, subprocess-based) |
| **Primary Language** | Python 3.10+ |
| **Target Users** | Developers, open source maintainers, AI agents |
| **Integration** | Claude Code, IBM Bob Shell, any MCP-compatible agent |
| **Persona** | Brutally honest grumpy senior dev — sharp, funny, specific |

---

## 2. Goals

- Expose README analysis as MCP tools so any agent can call them
- Score READMEs across 7 quality dimensions (0–100 each)
- Produce roast-style commentary that is funny but actionable
- Support both GitHub repo URLs and raw pasted README text as input
- Keep the server zero-dependency-bloat — only `fastmcp`, `httpx`, `anthropic`
- Make it publishable on PyPI and GitHub with a good README (meta)

---

## 3. Repository Structure

```
readme-score/
├── readme_score/
│   ├── __init__.py
│   ├── server.py          # FastMCP server + tool registration
│   ├── fetcher.py         # GitHub README fetcher logic
│   ├── scorer.py          # Claude API call + prompt logic
│   └── formatter.py       # Markdown/JSON output formatting
├── prompts/
│   └── roast_system.txt   # System prompt for roast persona
├── tests/
│   ├── test_fetcher.py
│   ├── test_scorer.py
│   └── fixtures/
│       ├── good_readme.md
│       ├── bad_readme.md
│       └── empty_readme.md
├── .env.example
├── pyproject.toml
├── README.md              # Must score 90+ on its own tool (dogfooding)
└── CONTRIBUTING.md
```

---

## 4. MCP Tools Specification

### Tool 1: `readme_roast`

**Purpose:** Score and roast a single README.

**Inputs:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `source` | string | Yes | GitHub repo URL (`https://github.com/owner/repo`) or raw README text |
| `response_format` | enum | No | `markdown` (default) or `json` |
| `roast_intensity` | enum | No | `mild`, `medium` (default), `savage` |

**Behaviour:**
- If `source` starts with `https://github.com`, fetch README via GitHub raw API
- Try `main` branch first, fall back to `master`, then `readme.md` casing variants
- Truncate README to 12,000 characters before sending to Claude (cost guard)
- Call Claude API with roast system prompt and structured output schema
- Return formatted roast report

**Output (markdown format):**
```
# README Roast Report: owner/repo

Overall Score: 63/100  Grade: C
████████░░  "The README equivalent of a half-eaten sandwich."

## Dimension Scores
| Dimension            | Score | Roast |
|---|---|---|
| Purpose              | 80    | ... |
| Installation         | 40    | ... |
| Usage & Examples     | 55    | ... |
| Documentation Depth  | 60    | ... |
| Badges & Metadata    | 70    | ... |
| Contributing Guide   | 50    | ... |
| License              | 90    | ... |

## Top 3 Sins
1. ...
2. ...
3. ...

## Quick Wins
1. ...
2. ...
3. ...

## Verdict
...
```

**Output (json format):**
```json
{
  "overall_score": 63,
  "grade": "C",
  "one_liner_roast": "...",
  "dimensions": {
    "purpose": { "score": 80, "comment": "..." },
    "installation": { "score": 40, "comment": "..." },
    "usage_examples": { "score": 55, "comment": "..." },
    "documentation_depth": { "score": 60, "comment": "..." },
    "badges_and_metadata": { "score": 70, "comment": "..." },
    "contributing_guide": { "score": 50, "comment": "..." },
    "license": { "score": 90, "comment": "..." }
  },
  "top_3_sins": ["...", "...", "..."],
  "quick_wins": ["...", "...", "..."],
  "verdict": "..."
}
```

---

### Tool 2: `readme_compare`

**Purpose:** Compare two READMEs head-to-head and declare a winner.

**Inputs:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `source_a` | string | Yes | GitHub URL or raw README text for project A |
| `source_b` | string | Yes | GitHub URL or raw README text for project B |
| `response_format` | enum | No | `markdown` (default) or `json` |

**Behaviour:**
- Fetch/validate both READMEs independently
- Run `readme_roast` logic on both (two Claude API calls)
- Compute dimension-level winner (A vs B per row)
- Declare overall winner based on total score
- Generate a head-to-head verdict with personality

**Output:**
```
# README Battle: repo-a vs repo-b

Winner: repo-a (74 vs 58)

| Dimension            | repo-a | repo-b | Winner  |
|---|---|---|---|
| Purpose              | 85     | 60     | repo-a  |
| Installation         | 70     | 55     | repo-a  |
| Usage & Examples     | 65     | 70     | repo-b  |
...

## Verdict
repo-b's README looks like it was written during a fire drill...
```

---

## 5. Scoring Dimensions

| Dimension | Weight | What Claude checks |
|---|---|---|
| **Purpose** | 20% | Does the first paragraph clearly explain what the project does and who it's for? No jargon, no vague mission statements. |
| **Installation** | 18% | Are there step-by-step install instructions? Are prerequisites listed? Does it cover pip, conda, brew, or whichever is relevant? |
| **Usage & Examples** | 18% | Are there real code snippets? Not pseudocode. Not `# TODO: add examples`. Actual runnable examples. |
| **Documentation Depth** | 15% | Are there API docs, config options, environment variables, or architecture notes for anything non-trivial? |
| **Badges & Metadata** | 10% | CI status, license badge, PyPI version, coverage. Not mandatory but signals a maintained project. |
| **Contributing Guide** | 10% | Is there a CONTRIBUTING section or link? PR process? Issue templates? |
| **License** | 9% | Is the license clearly stated? Bonus if SPDX identifier is used. |

**Grade Scale:**

| Score | Grade | Label |
|---|---|---|
| 90–100 | S | Exceptional — you'd star this repo just for the README |
| 75–89 | A | Solid — gets the job done with minor gaps |
| 60–74 | B | Decent — some sections feel rushed |
| 45–59 | C | Mediocre — the developer clearly had places to be |
| 30–44 | D | Sad — like a CV with just a name on it |
| 0–29 | F | A war crime against documentation |

---

## 6. Claude API Integration

### System Prompt Persona
```
You are a brutally honest, slightly grumpy senior open source maintainer who has reviewed 
thousands of READMEs. You roast bad READMEs like a code review from hell — sharp, funny, 
specific, and occasionally savage. But you're not mean for sport; every roast comes with 
a concrete improvement suggestion. Your scoring is strict and consistent.
```

### Roast Intensity Modifier
- `mild` — constructive criticism, light sarcasm
- `medium` — dry wit, punchy one-liners, direct callouts (default)
- `savage` — no mercy, maximum roast energy, still actionable

### Model & Cost
- Model: `claude-sonnet-4-6` (fast, cheap, good enough for structured output)
- Max input tokens: ~3,000 (12,000 chars of README)
- Max output tokens: 1,500
- Estimated cost per roast: ~$0.003

---

## 7. GitHub README Fetcher Logic (`fetcher.py`)

```
Input URL: https://github.com/owner/repo

Resolution order:
1. https://raw.githubusercontent.com/owner/repo/main/README.md
2. https://raw.githubusercontent.com/owner/repo/master/README.md
3. https://raw.githubusercontent.com/owner/repo/main/readme.md
4. https://raw.githubusercontent.com/owner/repo/main/README.rst
5. Raise ValueError with helpful message if all fail

Timeout: 15 seconds
Max README size: 500KB (guard against massive monorepo READMEs)
```

---

## 8. Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |
| `ROAST_DEFAULT_INTENSITY` | No | Default: `medium` |
| `ROAST_MAX_README_CHARS` | No | Default: `12000` |

`.env.example`:
```env
ANTHROPIC_API_KEY=sk-ant-...
ROAST_DEFAULT_INTENSITY=medium
ROAST_MAX_README_CHARS=12000
```

---

## 9. Dependencies

```toml
[project]
name = "readme-score"
version = "0.1.0"
requires-python = ">=3.10"

dependencies = [
    "fastmcp>=2.0.0",
    "httpx>=0.27.0",
    "anthropic>=0.40.0",
    "python-dotenv>=1.0.0",
]

[project.scripts]
readme-score = "readme_score.server:main"
```

---

## 10. Claude Code / Bob Shell Integration

### Claude Code (`~/.claude.json` or project `.mcp.json`)
```json
{
  "mcpServers": {
    "readme-score": {
      "command": "python",
      "args": ["-m", "readme_score.server"],
      "env": {
        "ANTHROPIC_API_KEY": "<your-key>"
      }
    }
  }
}
```

### Bob Shell (`~/.bob/shell/config.json`)
```json
{
  "mcpServers": [
    {
      "name": "readme-score",
      "command": "python",
      "args": ["-m", "readme_score.server"],
      "env": {
        "ANTHROPIC_API_KEY": "<your-key>"
      }
    }
  ]
}
```

### Example Agent Invocations
```
# Roast a GitHub repo
readme_roast(source="https://github.com/owner/repo")

# Roast raw text with savage intensity
readme_roast(source="# My Project\nIt does stuff.", roast_intensity="savage")

# Compare two repos
readme_compare(source_a="https://github.com/org/repo-a", source_b="https://github.com/org/repo-b")

# Get JSON output for programmatic use
readme_roast(source="https://github.com/owner/repo", response_format="json")
```

---

## 11. Build Phases

### Phase 1 — Core (Day 1)
- [ ] Scaffold repo with `pyproject.toml`, `.env.example`, folder structure
- [ ] Implement `fetcher.py` — GitHub URL resolver + raw README fetcher
- [ ] Implement `scorer.py` — Claude API call with structured JSON output schema
- [ ] Implement `formatter.py` — markdown + JSON output renderers
- [ ] Implement `server.py` — FastMCP server with `readme_roast` tool registered
- [ ] Manual smoke test via `npx @modelcontextprotocol/inspector`

### Phase 2 — Second Tool + Polish (Day 2)
- [ ] Implement `readme_compare` tool
- [ ] Add `roast_intensity` parameter with system prompt modifiers
- [ ] Add input validation (Pydantic models for all tool inputs)
- [ ] Add error handling — bad URLs, private repos, no README found, API failures
- [ ] Write `tests/` with 3 fixture READMEs (good, bad, empty)
- [ ] Write the project's own README (must score 90+ — dogfood it)

### Phase 3 — Publish (Day 3)
- [ ] Publish to PyPI (`pip install readme-score`)
- [ ] Push to GitHub with topics: `mcp`, `readme`, `developer-tools`, `llm`, `cli`
- [ ] Write LinkedIn post with a screenshot of a real roast output
- [ ] Add to your MCP server portfolio

---

## 12. LinkedIn / GitHub Positioning

**GitHub description:**
> 🔥 MCP server that roasts your README. Scores 7 quality dimensions with savage-but-actionable commentary. Plug into Claude Code, Bob Shell, or any MCP agent.

**Topics:** `mcp`, `mcp-server`, `readme`, `developer-tools`, `llm`, `fastmcp`, `python`, `open-source`

**LinkedIn angle:**
> Built a weekend tool that does what every senior dev wants to say about bad READMEs but can't. `readme-score` is an MCP server — plug it into Claude Code or Bob Shell and roast any GitHub README in seconds. Scores Purpose, Installation, Examples, and more. Because your README is the first PR anyone reads.

---

## 13. Future Ideas (Post v0.1)

- `readme_fix` tool — auto-generates improved sections based on the roast
- GitHub Action integration — fail CI if README score drops below threshold
- Batch mode — score all repos in a GitHub org
- Web UI wrapper (reference the Roast My Code artifact for inspiration)
- `--watch` mode — re-score on file save during local README editing