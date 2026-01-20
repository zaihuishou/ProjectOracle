# MCP Testing Guide

This guide explains how to test the ProjectOracle MCP Server using standard MCP tools.

## Method 1: MCP Inspector (Recommended for Debugging)

The **MCP Inspector** is an official developer tool that provides a web interface to interact with your MCP server. It allows you to list tools, resources, and prompts, and execute them directly.

### 1. Prerequisites
- Node.js installed (to use `npx`)
- ProjectOracle installed in your virtual environment

### 2. Run Inspector
Run the following command in your terminal:

```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Start Inspector pointing to your server
npx @modelcontextprotocol/inspector python3 -m project_oracle.server
```

### 3. Usage
A browser window will open (usually at http://localhost:5173).

- **Tools Tab**:
    - Select `analyze_project`.
    - Arguments:
        ```json
        {
          "path": "/Users/beste/PythonProjects/ProjectOracle",
          "llm_provider": "gemini",
          "force": true
        }
        ```
    - Click "Run Tool" to see the output.

- **Resources Tab**:
    - You should see a list of files from the last analyzed project.
    - Click on a resource (e.g., `project:///src/project_oracle/cli.py`) to read its content.
    - *Note: Run `analyze_project` tool first to set the active project context.*

- **Prompts Tab**:
    - Select `analyze-architecture`.
    - Arguments: `{"focus": "security"}`.
    - Click "Get Prompt" to see the generated messages.

---

## Method 2: Claude Desktop (Integration Test)

Test how the server behaves inside the Claude Desktop application.

### 1. Configure
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "project-oracle": {
      "command": "/absolute/path/to/ProjectOracle/venv/bin/python3",
      "args": ["-m", "project_oracle.server"],
      "env": {
        "ANTHROPIC_API_KEY": "your-key",
        "GEMINI_API_KEY": "your-key"
      }
    }
  }
}
```

### 2. Test Scenarios
Open Claude and try these prompts:

1.  **Analysis**: "Please use project-oracle to analyze this project (path: /Users/beste/PythonProjects/ProjectOracle) using Gemini."
2.  **Resource Access**: "Can you show me the content of `src/project_oracle/server.py` from the project resources?"
3.  **Prompt Usage**: "Run the architectural analysis prompt on this project."

---

## Method 3: CLI Testing (Quick Check)

You can also run a quick internal test using the CLI, which shares the same core logic:

```bash
project-oracle . --llm-provider gemini
```
