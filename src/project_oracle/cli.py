"""Command-line interface for ProjectOracle."""

import os
import sys
from pathlib import Path

import click

from .core import Scanner, PythonParser, OracleEngine, ConfigManager
from .utils import logger, setup_logging


@click.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--interactive', '-i', is_flag=True, help='Interactive configuration mode')
@click.option('--dry-run', is_flag=True, help='Preview cost without analyzing')
@click.option('--force', '-f', is_flag=True, help='Force regeneration')
@click.option('--max-files', default=5000, help='Max files to analyze')
@click.option('--max-cost', default=0.50, type=float, help='Max LLM cost in USD')
@click.option('--verbose', '-v', is_flag=True, help='Verbose logging')
def main(project_path, interactive, dry_run, force, max_files, max_cost, verbose):
    """Analyze a project and generate .ProjectOracle report."""
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level)
    
    project_path = Path(project_path).resolve()
    
    # Interactive prompts
    if interactive:
        click.echo("\n🔮 ProjectOracle Interactive Mode\n")
        project_path = click.prompt('Project root path', default=str(project_path), type=click.Path(exists=True))
        project_path = Path(project_path)
        max_files = click.prompt('Max files to analyze', default=5000, type=int)
        max_cost = click.prompt('Max LLM cost (USD)', default=0.50, type=float)
        force = click.confirm('Force regenerate?', default=False)
        dry_run = click.confirm('Dry run only?', default=False)
    
    # Load configuration
    config_mgr = ConfigManager(project_path)
    config = config_mgr.load({
        "scan": {"max_files": max_files},
        "llm": {"max_cost_usd": max_cost}
    })
    
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key and not dry_run:
        click.echo("❌ Error: ANTHROPIC_API_KEY environment variable not set", err=True)
        click.echo("   Set it with: export ANTHROPIC_API_KEY=your-key-here")
        sys.exit(1)
    
    # Initialize components
    click.echo("\n🔍 Scanning project...\n")
    
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
    click.echo(f"  • Estimated time: ~{stats.estimated_seconds}s")
    
    # Rough cost estimation
    estimated_cost = min(stats.included_files * 0.0001, max_cost)
    click.echo(f"  • Estimated cost: ~${estimated_cost:.4f} USD\n")
    
    if dry_run:
        click.echo("✅ Dry run complete (no changes made)")
        return
    
    # Confirm before proceeding
    if estimated_cost > max_cost * 0.8:
        click.echo(f"⚠️  WARNING: Approaching cost limit ${max_cost:.2f}")
        if not click.confirm('Continue anyway?'):
            click.echo("Aborted.")
            return
    
    if not force and stats.included_files > 1000:
        if not click.confirm(f'\nAnalyze {stats.included_files:,} files?'):
            click.echo("Aborted.")
            return
    
    # Run analysis
    click.echo("\n🚀 Starting analysis...\n")
    
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
                with open(entry_files[0], 'r') as f:
                    entry_content = f.read()
            except:
                pass
        
        # Collect uncertain imports
        uncertain = set()
        for sym_data in symbols.values():
            uncertain.update(sym_data.imports.uncertain)
        
        # Analyze
        click.echo("\n🤖 Analyzing with LLM...")
        
        engine = OracleEngine(api_key=api_key, max_cost_usd=max_cost)
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
        click.echo(f"  • Functions found: {total_functions}\n")
    
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
