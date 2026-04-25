# Contributing to readme-score 🔥

Thanks for wanting to make README roasting even better! Here's how to get involved.

## Quick Start for Contributors

```bash
# 1. Fork & clone
git clone https://github.com/<your-username>/readme_score_mcp.git
cd readme_score_mcp

# 2. Set up dev environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

# 3. Install with dev dependencies
pip install -e ".[dev]"

# 4. Run tests to make sure everything works
python -m pytest tests/ -v
```

## How to Contribute

### 🐛 Found a Bug?

1. Check [existing issues](https://github.com/ViswaSrimaan/readme_score_mcp/issues) to avoid duplicates
2. Open a new issue with:
   - What you expected to happen
   - What actually happened
   - Steps to reproduce
   - Your Python version and OS

### 💡 Have an Idea?

Open an issue first before writing code — let's discuss the approach before you invest time. Tag it with `enhancement`.

### 🔧 Submitting a PR

1. **Fork** the repo and create a feature branch:
   ```bash
   git checkout -b feature/your-amazing-feature
   ```

2. **Write tests** for any new functionality. We don't merge untested code.

3. **Run the test suite** and make sure everything passes:
   ```bash
   python -m pytest tests/ -v
   ```

4. **Keep commits clean** — use descriptive commit messages:
   ```
   ✅ Add RST format support to fetcher
   ❌ fixed stuff
   ```

5. **Push** and open a PR against `main`:
   ```bash
   git push origin feature/your-amazing-feature
   ```

## Project Structure

```
readme_score/
├── __init__.py        # Package version
├── fetcher.py         # GitHub README fetching logic
└── server.py          # FastMCP server + tool definitions
prompts/
└── roast_system.txt   # Scoring prompt template
tests/
├── test_fetcher.py    # Fetcher unit tests
├── test_scorer.py     # Server/prompt construction tests
└── fixtures/          # Sample READMEs for testing
```

## What We're Looking For

Here are some areas where contributions would be especially welcome:

- **New scoring dimensions** — got an idea for an 8th dimension? Pitch it
- **Better roast lines** — make `roast_system.txt` funnier (hard requirement: still actionable)
- **More README format support** — `.rst`, `.txt`, org-mode, AsciiDoc
- **Batch scoring** — score all repos in a GitHub org
- **GitHub Action** — fail CI if README score drops below a threshold

## Code Style

- Python 3.10+ with type hints
- Docstrings on all public functions
- Keep it simple — this project's charm is its minimalism

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Just fetcher tests
python -m pytest tests/test_fetcher.py -v

# Just server/prompt tests
python -m pytest tests/test_scorer.py -v
```

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
