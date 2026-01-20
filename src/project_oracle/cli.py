"""Command-line interface for ProjectOracle."""

import os
import sys
from pathlib import Path

import click

from .core import Scanner, PythonParser, OracleEngine, ConfigManager
from .core.llm_providers import create_provider
from .utils import logger, setup_logging


@click.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--interactive', '-i', is_flag=True, help='Interactive configuration mode')
@click.option('--scan-only', is_flag=True, help='Scan-only mode (FREE - no API key needed)')
@click.option('--llm-provider', 
              type=click.Choice(['anthropic', 'openai', 'ollama', 'none'], case_sensitive=False),
              default='anthropic',
              help='LLM provider (anthropic/openai/ollama/none)')
@click.option('--llm-model', help='LLM model name (provider-specific)')
@click.option('--dry-run', is_flag=True, help='Preview cost without analyzing')
@click.option('--force', '-f', is_flag=True, help='Force regeneration')
@click.option('--max-files', default=5000, help='Max files to analyze')
@click.option('--max-cost', default=0.50, type=float, help='Max LLM cost in USD')
@click.option('--verbose', '-v', is_flag=True, help='Verbose logging')
def main(project_path, interactive, scan_only, llm_provider, llm_model,
         dry_run, force, max_files, max_cost, verbose):
    """Analyze a project and generate .ProjectOracle report.
    
    \b
    Examples:
      # FREE modes (no API key needed):
      project-oracle /path/to/project --scan-only
      project-oracle /path/to/project --llm-provider ollama
      
      # Paid modes:
      project-oracle /path/to/project --llm-provider anthropic
      project-oracle /path/to/project --llm-provider openai
    """
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level)
    
    project_path = Path(project_path).resolve()
    
    # Scan-only implies none provider
    if scan_only:
        llm_provider = 'none'
    
    # Interactive prompts
    if interactive:
        click.echo("\n🔮 ProjectOracle Interactive Mode\n")
        project_path = click.prompt('Project root path', default=str(project_path), type=click.Path(exists=True))
        project_path = Path(project_path)
        max_files = click.prompt('Max files to analyze', default=5000, type=int)
        
        llm_provider = click.prompt(
            'LLM provider',
            type=click.Choice(['anthropic', 'openai', 'ollama', 'none']),
            default='anthropic'
        )
        
        if llm_provider == 'ollama':
            llm_model = click.prompt('Ollama model', default='llama2')
        elif llm_provider in ['anthropic', 'openai']:
            max_cost = click.prompt('Max LLM cost (USD)', default=0.50, type=float)
        
        force = click.confirm('Force regenerate?', default=False)
        dry_run = click.confirm('Dry run only?', default=False)
    
    # Load configuration
    config_mgr = ConfigManager(project_path)
    config = config_mgr.load({
        "scan": {"max_files": max_files},
        "llm": {"max_cost_usd": max_cost}
    })
    
    # Get API key based on provider
    api_key = None
    if llm_provider == 'anthropic':
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key and not dry_run:
            click.echo("❌ Error: ANTHROPIC_API_KEY environment variable not set", err=True)
            click.echo("   Set it with: export ANTHROPIC_API_KEY=your-key-here")
            click.echo("\n💡 TIP: Use --scan-only or --llm-provider ollama for FREE analysis", err=True)
            sys.exit(1)
    elif llm_provider == 'openai':
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key and not dry_run:
            click.echo("❌ Error: OPENAI_API_KEY environment variable not set", err=True)
            click.echo("   Set it with: export OPENAI_API_KEY=your-key-here")
            click.echo("\n💡 TIP: Use --scan-only or --llm-provider ollama for FREE analysis", err=True)
            sys.exit(1)
    elif llm_provider == 'ollama':
        click.echo("💡 Using Ollama (local LLM) - FREE!")
        click.echo("   Make sure Ollama is running: ollama serve")
        if llm_model:
            click.echo(f"   Using model: {llm_model}")
            click.echo(f"   If not downloaded: ollama pull {llm_model}\n")
    elif llm_provider == 'none':
        click.echo("💡 Scan-only mode - FREE! No AI analysis, basic report only\n")
    
    # Initialize components
    click.echo("🔍 Scanning project...\n")
    
    scanner = Scanner(
        str(project_path),
        max_files=config["scan"]["max_files"],
        workers=config["scan"]["workers"]
    )
    
    # Get scan stats
    stats = scanner.get_scan_stats(extensions=['.py'])
    
    click.echo(f"📊 Scan Results:")
    click.echo(f"  • Total files found: {stats.total_files:,}")
    click.echo(f"  • Files to analyze: {stats.included_files:,}")
    click.echo(f"  • Strategy: {stats.strategy}")
    click.echo(f"  • Estimated time: ~{stats.estimated_seconds}s\n")
    
    if dry_run:
        click.echo("✅ Dry run complete (no changes made)")
        return
    
    # Confirm before proceeding for large projects
    if not force and stats.included_files > 1000:
        if not click.confirm(f'Analyze {stats.included_files:,} files?'):
            click.echo("Aborted.")
            return
    
    # Run analysis
    click.echo("🚀 Starting analysis...\n")
    
    try:
        # Scan and extract
        parser = PythonParser(str(project_path))
        tree = scanner.get_directory_tree(max_depth=4)
        files_info = scanner.get_scannable_files(['.py'])
        
        click.echo(f"📝 Extracting symbols from {len(files_info['files'])} files...")
        
        symbols = {}
        total_classes = 0
        total_functions = 0
        
        with click.progressbar(files_info['files'][:100], label='Processing') as files:
            for file_path in files:
                symbol_data = parser.extract(file_path)
                symbols[str(file_path)] = symbol_data
                total_classes += len(symbol_data.classes)
                total_functions += len(symbol_data.functions)
        
        # Get entry point
        entry_files = [f for f in files_info['files'] if f.name in ['main.py', 'app.py', '__main__.py']]
        entry_content = ""
        if entry_files:
            try:
                with open(entry_files[0], 'r', encoding='utf-8') as f:
                    entry_content = f.read()
            except (IOError, UnicodeDecodeError) as e:
                logger.warning(f"Failed to read entry point {entry_files[0]}: {e}")
        
        # Collect uncertain imports
        uncertain = set()
        for sym_data in symbols.values():
            uncertain.update(sym_data.imports.uncertain)
        
        # Create provider
        try:
            provider = create_provider(
                provider_name=llm_provider,
                api_key=api_key,
                model=llm_model
            )
        except ImportError as e:
            click.echo(f"\n❌ Error: {e}", err=True)
            sys.exit(1)
        except ValueError as e:
            click.echo(f"\n❌ Error: {e}", err=True)
            sys.exit(1)
        
        # Analyze
        if llm_provider == 'none':
            click.echo("\n📋 Generating scan-only report...")
        else:
            click.echo(f"\n🤖 Analyzing with {provider.name}...")
        
        engine = OracleEngine(provider=provider, max_cost_usd=max_cost)
        analysis = engine.analyze_project(
            tree=tree,
            symbols=symbols,
            entry_point_content=entry_content,
            uncertain_imports=list(uncertain),
            dry_run=False
        )
        
        # Generate report
        click.echo("📄 Generating report...")
        
        report_stats = {
            "total_files": stats.total_files,
            "included_files": stats.included_files,
            "strategy": stats.strategy,
            "classes": total_classes,
            "functions": total_functions
        }
        
        report = engine.generate_report(analysis, report_stats, project_path.name)
        
        # Write report
        output_path = project_path / ".ProjectOracle"
        
        if output_path.exists() and not force:
            backup_path = project_path / ".ProjectOracle.backup"
            output_path.rename(backup_path)
            click.echo(f"  Backed up old report to: {backup_path.name}")
        
        output_path.write_text(report, encoding='utf-8')
        
        click.echo(f"\n✅ Analysis complete!")
        click.echo(f"📄 Report saved to: {output_path}")
        click.echo(f"📊 Statistics:")
        click.echo(f"  • Files scanned: {stats.total_files:,}")
        click.echo(f"  • Files analyzed: {stats.included_files:,}")
        click.echo(f"  • Classes found: {total_classes}")
        click.echo(f"  • Functions found: {total_functions}")
        
        if llm_provider == 'none':
            click.echo(f"\n💡 For AI-powered analysis, use:")
            click.echo(f"   --llm-provider anthropic  (paid)")
            click.echo(f"   --llm-provider ollama     (free, local)")
    
    except KeyboardInterrupt:
        click.echo("\n\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
