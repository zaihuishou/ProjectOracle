"""MCP Server for ProjectOracle."""

import os
import asyncio
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .core import Scanner, PythonParser, OracleEngine, ConfigManager
from .utils import logger, setup_logging


# Initialize MCP server
app = Server("project-oracle")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="analyze_project",
            description="Analyze a software project and generate .ProjectOracle report",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to project root"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force regeneration even if report exists",
                        "default": False
                    },
                    "max_files": {
                        "type": "integer",
                        "description": "Maximum files to analyze",
                        "default": 5000
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Preview cost without analyzing",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle MCP tool calls."""
    if name != "analyze_project":
        raise ValueError(f"Unknown tool: {name}")
    
    # Extract arguments
    project_path = Path(arguments["path"])
    force = arguments.get("force", False)
    max_files = arguments.get("max_files", 5000)
    dry_run = arguments.get("dry_run", False)
    
    if not project_path.exists():
        return [TextContent(
            type="text",
            text=f"Error: Project path does not exist: {project_path}"
        )]
    
    try:
        # Run analysis
        result = await asyncio.to_thread(
            analyze_project_sync,
            project_path,
            force,
            max_files,
            dry_run
        )
        
        return [TextContent(type="text", text=result)]
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error: Analysis failed - {str(e)}"
        )]


def analyze_project_sync(
    project_path: Path,
    force: bool,
    max_files: int,
    dry_run: bool
) -> str:
    """Synchronous project analysis (runs in thread)."""
    
    logger.info(f"Analyzing project: {project_path}")
    
    # Load configuration
    config_mgr = ConfigManager(project_path)
    config = config_mgr.load({
        "scan": {"max_files": max_files}
    })
    
    # Initialize components
    scanner = Scanner(
        str(project_path),
        max_files=config["scan"]["max_files"],
        workers=config["scan"]["workers"]
    )
    
    parser = PythonParser(str(project_path))
    
    # Get API key and create provider
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        # Try scan-only mode if no API key
        logger.warning("No ANTHROPIC_API_KEY found, using scan-only mode")
        from .core.llm_providers import NoLLMProvider
        provider = NoLLMProvider()
    else:
        from .core.llm_providers import AnthropicProvider
        provider = AnthropicProvider(api_key=api_key)
    
    engine = OracleEngine(
        provider=provider,
        max_cost_usd=config["llm"]["max_cost_usd"]
    )
    
    # Scan files
    logger.info("Scanning project files...")
    tree = scanner.get_directory_tree(max_depth=4)
    files_info = scanner.get_scannable_files(['.py'])
    
    stats = {
        "total_files": files_info["total_found"],
        "included_files": files_info["included"],
        "strategy": files_info["strategy"]
    }
    
    # Extract symbols
    logger.info(f"Extracting symbols from {len(files_info['files'])} files...")
    symbols = {}
    total_classes = 0
    total_functions = 0
    
    for file_path in files_info['files'][:100]:  # Limit for MVP
        symbol_data = parser.extract(file_path)
        symbols[str(file_path)] = symbol_data
        total_classes += len(symbol_data.classes)
        total_functions += len(symbol_data.functions)
    
    stats["classes"] = total_classes
    stats["functions"] = total_functions
    
    # Get entry point content
    entry_files = [f for f in files_info['files'] if f.name in ['main.py', 'app.py', '__main__.py']]
    entry_content = ""
    if entry_files:
        try:
            with open(entry_files[0], 'r') as f:
                entry_content = f.read()
        except:
            pass
    
    # Collect uncertain imports
    uncertain = set()
    for sym_data in symbols.values():
        uncertain.update(sym_data.imports.uncertain)
    
    # Analyze with LLM
    logger.info("Analyzing with LLM...")
    analysis = engine.analyze_project(
        tree=tree,
        symbols=symbols,
        entry_point_content=entry_content,
        uncertain_imports=list(uncertain),
        dry_run=dry_run
    )
    
    if dry_run:
        return f"Dry run complete. Estimated cost: ${analysis.estimated_cost:.4f} USD\nFiles to analyze: {stats['included_files']}"
    
    # Generate report
    logger.info("Generating report...")
    report = engine.generate_report(analysis, stats, project_path.name)
    
    # Create .ProjectOracle folder
    output_dir = project_path / ".ProjectOracle"
    output_dir.mkdir(exist_ok=True)
    
    # Generate report filename: project_name_analysis.md (use resolve().name for actual dir name)
    project_name = project_path.resolve().name
    report_filename = f"{project_name}_analysis.md"
    output_path = output_dir / report_filename
    
    # Backup if exists
    if output_path.exists() and not force:
        backup_path = output_dir / f"{project_name}_analysis.backup.md"
        output_path.rename(backup_path)
    
    output_path.write_text(report, encoding='utf-8')
    
    logger.info(f"Report written to: {output_path}")
    
    return f"""Analysis complete!

Report: {output_path}
Files scanned: {stats['total_files']:,}
Files analyzed: {stats['included_files']:,}
Classes found: {stats['classes']}
Functions found: {stats['functions']}
Strategy: {stats['strategy']}
"""


async def main():
    """Run MCP server."""
    # Setup logging
    setup_logging(level="INFO")
    
    logger.info("Starting ProjectOracle MCP server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
