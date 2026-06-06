# RepoAnchor

RepoAnchor is an autonomous, entirely on-device, CPU-optimal developer utility that maps, builds, and maintains a condensed structural blueprint of a repository.

By intercepting your local Git pre-commit pipeline, RepoAnchor incrementally parses modified codebase components. It strips procedural function and class bodies while retaining vital context definitions, including docstrings, type annotations, signatures, and module call-graphs.

The output is a single, portable Markdown blueprint (`.repo-anchor.md`) located at your repository root. This file can be instantly provided to any external Large Language Model (LLM) to establish context awareness at a fraction of the cost of standard codebase inclusion.

---

## The Problem Space: Context Amnesia

Modern software workflows leveraging LLMs (e.g., Claude, GPT, DeepSeek) suffer from three key architectural problems:

1. **Redundancy and Duplication**: Without high-level repository awareness, LLMs generate duplicate utilities or classes buried in other directories.
2. **Architectural Drift**: Conversational boundaries cause models to drift from your established architecture (e.g., introducing raw database calls into projects using strict ORM wrappers).
3. **Token Latency & Expense**: Injecting entire codebases into active context windows causes severe processing lag, high costs, and triggers performance degradation.

---

## The RepoAnchor Solution

RepoAnchor creates a lightweight bridge between your local repository states and LLM prompts:

- **Event-Driven Analysis**: Tracks staged changes using native git plumbing commands, skipping calculations for unmodified files.
- **Decomposition**: Compiles files into structural AST blocks, removing procedural execution logic while keeping architectural metadata.
- **Dependency & Sequence Extraction**: Analyzes import aliasing maps and static call chains to discover execution paths.
- **Compact Assembly**: Compresses outputs down to space-optimized Markdown layouts.

---

## Directory Layout

````text
repoanchor/
├── pyproject.toml              # Packaging configuration
├── .gitignore                  # Git exclude criteria
├── src/
│   └── repoanchor/
│       ├── __init__.py
│       ├── cli.py              # CLI & Pre-commit orchestrator
│       ├── cache/
│       │   ├── __init__.py
│       │   └── manager.py      # SHA-256 state database manager
│       └── parser/
│           ├── __init__.py
│           ├── python_parser.py # Python AST skeleton parser
│           ├── relation_analyzer.py # Static import & call tracker
│           ├── structural_fallback.py # Regex structural scanner (JS/TS/Go)
│           ├── markdown_compiler.py # Space-optimized markdown generator
│           └── registry.py      # Multi-language router
└── tests/                       # Complete unit & integration suites

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Git (initialized repository)

### 1. Installation
To register the tool in editable mode so changes are reflected instantly during development, run:
```bash
python -m pip install -e .
````

### 2. Verify Installation

Ensure that the unit and integration tests execute successfully:

```bash
python -m unittest discover -s tests
```

### 3. Install the Git Pre-commit Hook

To automatically trigger signature builds on every commit execution, install the hook:

```bash
repoanchor --install
```

This writes a portable shell hook inside `.git/hooks/pre-commit`.

---

## Usage

### Command Line Interface

RepoAnchor can be executed manually at any point or controlled via CLI parameters:

```bash
# Run a full scan over all supported files in the repository
python -m repoanchor.cli

# For running an automatic git hook
python -m repoanchor.cli --install
```

### CLI Arguments Summary

| Flag             | Default                   | Description                                                                                 |
| :--------------- | :------------------------ | :------------------------------------------------------------------------------------------ |
| `--pre-commit`   | `False`                   | Run inside hook mode (checks staged files only, automatically re-stages output blueprints). |
| `--install`      | `False`                   | Installs the pre-commit shell hook in `.git/hooks/`.                                        |
| `--cache-file`   | `.repo-anchor.cache.json` | Path to the JSON snapshot cache database.                                                   |
| `--output`, `-o` | `.repo-anchor.md`         | Target file for the compiled markdown blueprint.                                            |

---
