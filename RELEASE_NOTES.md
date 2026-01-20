# ProjectOracle v1.1.0 Release Notes

## 🎉 Major Features

### FREE Usage Options
ProjectOracle now supports **completely free** usage through multiple options:

1. **Scan-Only Mode** - No API key needed
2. **Local Ollama** - Free local LLM
3. **Google Gemini** - Generous free tier
4. **Paid Options** - Anthropic Claude & OpenAI GPT-4

## 🆕 New Features

### Multi-LLM Provider Support
- ✅ Anthropic Claude 3.5 Sonnet (paid)
- ✅ OpenAI GPT-4 (paid)
- ✅ Google Gemini Pro (FREE tier available!)
- ✅ Ollama (local, completely FREE)
- ✅ Scan-Only mode (no LLM, FREE)

### Enhanced CLI
```bash
# Free options
project-oracle /path/to/project --scan-only
project-oracle /path/to/project --llm-provider ollama
project-oracle /path/to/project --llm-provider gemini

# Paid options
project-oracle /path/to/project --llm-provider anthropic
project-oracle /path/to/project --llm-provider openai
```

### Improved Architecture
- Provider abstraction layer for easy extensibility
- Better error handling and logging
- Cost estimation for all paid providers
- Fallback to scan-only mode if no API key

## 🐛 Bug Fixes

- Fixed f-string formatting errors
- Updated provider architecture in MCP server
- Improved exception handling
- Fixed module exports in core/__init__.py
- Updated docstrings to reflect all providers

## 📚 Documentation

- Comprehensive code review completed
- Bug fix summary documented
- Installation guide updated
- README enhanced with free usage examples

## 🚀 Usage Examples

### Free Usage
```bash
# Method 1: Scan-only (fastest, basic report)
export ANTHROPIC_API_KEY=""  # No key needed
project-oracle . --scan-only

# Method 2: Ollama (free, AI-powered)
ollama pull llama2
project-oracle . --llm-provider ollama

# Method 3: Gemini (free tier, cloud)
export GEMINI_API_KEY="your-key"
project-oracle . --llm-provider gemini
```

### Paid Usage
```bash
# Claude (recommended quality)
export ANTHROPIC_API_KEY="sk-ant-..."
project-oracle . --llm-provider anthropic

# GPT-4
export OPENAI_API_KEY="sk-..."
project-oracle . --llm-provider openai
```

## 📦 Installation

```bash
pip install project-oracle

# Optional: Install specific provider support
pip install project-oracle[gemini]
pip install project-oracle[openai]
pip install project-oracle[ollama]
pip install project-oracle[all-llm]  # All providers
```

## 🔄 Migration from v1.0.0

The default behavior remains the same (Anthropic Claude). 

If you want to use new providers:
1. Update to v1.1.0
2. Install optional dependencies if needed
3. Use `--llm-provider` flag

## 🙏 Contributors

Thanks to all contributors who helped make this release possible!

## 📊 Statistics

- **Code Changes**: 400+ lines added
- **New Files**: 1 (llm_providers.py)
- **Bug Fixes**: 5 critical bugs resolved
- **Providers Supported**: 5

---

**Full Changelog**: https://github.com/zaihuishou/ProjectOracle/compare/v1.0.0...v1.1.0
