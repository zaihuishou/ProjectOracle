# Installation and Usage Guide

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/beste/PythonProjects/ProjectOracle

# Using pip
pip install -e .

# OR using Poetry (recommended)
poetry install
```

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 3. Run Analysis

```bash
# As CLI
project-oracle /path/to/your/project

# Interactive mode
project-oracle /path/to/your/project --interactive

# Dry run
project-oracle /path/to/your/project --dry-run

# With custom limits
project-oracle /path/to/your/project --max-files 10000 --max-cost 1.00
```

### 4. Use as MCP Server

Add to your MCP client config (e.g., `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "project-oracle": {
      "command": "python3",
      "args": ["-m", "project_oracle.server"],
      "cwd": "/Users/beste/PythonProjects/ProjectOracle",
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Testing

Test on this project itself:

```bash
# Dry run first
project-oracle . --dry-run

# Full analysis  
project-oracle . --max-cost 0.20

# Check the generated report
cat .ProjectOracle
```

## Project Structure

```
ProjectOracle/
├── src/project_oracle/
│   ├── __init__.py
│   ├── models.py          # Data models
│   ├── server.py          # MCP server
│   ├── cli.py             # CLI interface
│   ├── core/
│   │   ├── config.py      # Configuration manager
│   │   ├── scanner.py     # File scanner
│   │   ├── symbol_extractor.py  # AST parser
│   │   └── oracle_engine.py     # LLM engine
│   └── utils/
│       └── __init__.py    # Utilities
├── pyproject.toml
└── README.md
```

## Features Implemented

✅ **Scanner** - Respects .gitignore, intelligent sampling
✅ **Symbol Extractor** - Python AST parsing with import classification  
✅ **Oracle Engine** - LLM analysis with cost control
✅ **MCP Server** - Full MCP tool integration
✅ **CLI** - Interactive mode, progress bars
✅ **Configuration** - JSON and TOML support
✅ **Error Handling** - Graceful failures and fallbacks

## Next Steps

To enhance this MVP:

1. Add LockManager for incremental updates
2. Add MermaidValidator with auto-fix
3. Add security secret scanning
4. Add support for JavaScript/TypeScript
5. Add comprehensive tests
6. Package for PyPI distribution
