# AwesomeLib 🚀

> A lightning-fast Python library for processing and transforming data pipelines with zero configuration.

[![PyPI version](https://badge.fury.io/py/awesomelib.svg)](https://badge.fury.io/py/awesomelib)
[![CI Status](https://github.com/example/awesomelib/actions/workflows/ci.yml/badge.svg)](https://github.com/example/awesomelib/actions)
[![Coverage](https://codecov.io/gh/example/awesomelib/branch/main/graph/badge.svg)](https://codecov.io/gh/example/awesomelib)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is AwesomeLib?

AwesomeLib makes it dead simple to build data transformation pipelines in Python. Whether you're processing CSV files, streaming API responses, or transforming database records — AwesomeLib handles the plumbing so you can focus on your logic.

**Who is this for?**
- Data engineers building ETL pipelines
- Backend developers processing API data
- Anyone tired of writing the same boilerplate transformation code

## Installation

```bash
pip install awesomelib
```

**Prerequisites:**
- Python 3.10 or higher
- pip 21.0+

For development:
```bash
git clone https://github.com/example/awesomelib.git
cd awesomelib
pip install -e ".[dev]"
```

## Quick Start

```python
from awesomelib import Pipeline, transforms

# Create a simple pipeline
pipeline = Pipeline([
    transforms.read_csv("input.csv"),
    transforms.filter(lambda row: row["age"] > 18),
    transforms.rename({"name": "full_name"}),
    transforms.write_json("output.json"),
])

# Run it
result = pipeline.execute()
print(f"Processed {result.row_count} rows in {result.duration}s")
```

## Usage Examples

### Streaming API Data

```python
from awesomelib import Pipeline, transforms, sources

pipeline = Pipeline([
    sources.http_json("https://api.example.com/users", paginate=True),
    transforms.flatten("$.data[*]"),
    transforms.select(["id", "email", "created_at"]),
    transforms.write_parquet("users.parquet"),
])

pipeline.execute()
```

### Custom Transform Functions

```python
from awesomelib import Pipeline, transforms

@transforms.custom
def normalize_email(row):
    row["email"] = row["email"].lower().strip()
    return row

pipeline = Pipeline([
    transforms.read_csv("contacts.csv"),
    normalize_email,
    transforms.deduplicate(key="email"),
    transforms.write_csv("cleaned_contacts.csv"),
])
```

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `AWESOMELIB_WORKERS` | `4` | Number of parallel workers |
| `AWESOMELIB_BATCH_SIZE` | `1000` | Rows per batch |
| `AWESOMELIB_LOG_LEVEL` | `INFO` | Logging verbosity |

## API Reference

### `Pipeline(steps, config=None)`

| Parameter | Type | Description |
|---|---|---|
| `steps` | `list[Transform]` | Ordered list of transforms |
| `config` | `PipelineConfig` | Optional configuration |

### `Pipeline.execute() -> Result`

Runs the pipeline and returns a `Result` object with `.row_count`, `.duration`, and `.errors`.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Write tests for your changes
4. Submit a PR

## License

MIT License — see [LICENSE](LICENSE) for details.
