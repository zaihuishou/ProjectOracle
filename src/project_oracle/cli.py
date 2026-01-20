"""Command-line interface for ProjectOracle - Simplified version."""

import os
import sys
from pathlib import Path

import click

from .core import Scanner, PythonParser, OracleEngine, ConfigManager
from .core.llm_providers import create_provider
from .utils import logger, setup_logging


@click.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--force', '-f', is_flag=True, help='Force regeneration')
@click.option('--max-files', default=5000, help='Max files to analyze')
@click.option('--verbose', '-v', is_flag=True, help='Verbose logging')
def main(project_path, force, max_files, verbose):
    """Analyze a project and generate .ProjectOracle report.
    
    Interactive mode: Choose between scan-only or AI analysis.
    """
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level)
    
    project_path = Path(project_path).resolve()
    
    # 欢迎界面
    click.echo("\n" + "="*60)
    click.echo("🔮 ProjectOracle - AI-Powered Code Analysis")
    click.echo("="*60)
    click.echo(f"\n📁 Project: {project_path.name}")
    click.echo("")
    
    # 步骤1: 选择分析模式
    click.echo("📋 Step 1: Choose analysis mode")
    click.echo("")
    click.echo("  1. Scan Only (FREE - No API key needed)")
    click.echo("     → Quick scan, basic statistics")
    click.echo("")
    click.echo("  2. AI Analysis (Requires API key)")
    click.echo("     → Deep analysis with architecture insights")
    click.echo("")
    
    mode = click.prompt(
        'Select mode',
        type=click.Choice(['1', '2']),
        default='1'
    )
    
    use_ai = (mode == '2')
    llm_provider = 'none'
    api_key = None
    
    # 步骤2: 如果选择AI分析，选择provider
    if use_ai:
        click.echo("\n" + "-"*60)
        click.echo("🤖 Step 2: Choose AI Provider")
        click.echo("")
        click.echo("  1. Claude (Anthropic) - Best quality")
        click.echo("     Cost: ~$0.01-0.50 per analysis")
        click.echo("")
        click.echo("  2. GPT-4 (OpenAI) - High quality")
        click.echo("     Cost: ~$0.03-1.00 per analysis")
        click.echo("")
        click.echo("  3. Gemini (Google) - FREE tier available!")
        click.echo("     Cost: FREE (with limits) or very cheap")
        click.echo("")
        
        provider_choice = click.prompt(
            'Select AI provider',
            type=click.Choice(['1', '2', '3']),
            default='3'
        )
        
        # 映射选择到provider
        provider_map = {
            '1': ('anthropic', 'ANTHROPIC_API_KEY', 'https://console.anthropic.com/'),
            '2': ('openai', 'OPENAI_API_KEY', 'https://platform.openai.com/api-keys'),
            '3': ('gemini', 'GEMINI_API_KEY', 'https://makersuite.google.com/app/apikey')
        }
        
        llm_provider, env_key, api_url = provider_map[provider_choice]
        
        # 获取API密钥
        api_key = os.getenv(env_key)
        if not api_key:
            click.echo(f"\n⚠️  {env_key} not found in environment")
            click.echo(f"   Get your API key: {api_url}")
            click.echo("")
            api_key = click.prompt(f'Enter your {env_key} (or press Enter to use scan-only)', 
                                  default='', show_default=False)
            
            if not api_key:
                click.echo("\n💡 Switching to Scan-Only mode")
                use_ai = False
                llm_provider = 'none'
    
    # 显示配置摘要
    click.echo("\n" + "-"*60)
    click.echo("⚙️  Configuration Summary")
    click.echo(f"   Mode: {'AI Analysis' if use_ai else 'Scan Only'}")
    if use_ai:
        provider_names = {'anthropic': 'Claude', 'openai': 'GPT-4', 'gemini': 'Gemini'}
        click.echo(f"   AI Provider: {provider_names.get(llm_provider, llm_provider)}")
    click.echo(f"   Max Files: {max_files}")
    click.echo("-"*60)
    
    if not click.confirm('\n▶️  Start analysis?', default=True):
        click.echo("Cancelled.")
        return
    
    # 加载配置
    config_mgr = ConfigManager(project_path)
    config = config_mgr.load({
        "scan": {"max_files": max_files}
    })
    
    # 初始化组件
    click.echo("\n🔍 Scanning project...\n")
    
    scanner = Scanner(
        str(project_path),
        max_files=config["scan"]["max_files"],
        workers=config["scan"]["workers"]
    )
    
    # 获取扫描统计
    stats = scanner.get_scan_stats(extensions=['.py'])
    
    click.echo(f"📊 Scan Results:")
    click.echo(f"  • Total files found: {stats.total_files:,}")
    click.echo(f"  • Files to analyze: {stats.included_files:,}")
    click.echo(f"  • Strategy: {stats.strategy}")
    
    if not force and stats.included_files > 1000:
        if not click.confirm(f'\n⚠️  Analyze {stats.included_files:,} files?'):
            click.echo("Cancelled.")
            return
    
    # 运行分析
    click.echo("\n🚀 Starting analysis...\n")
    
    try:
        # 扫描和提取
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
        
        # 获取入口点
        entry_files = [f for f in files_info['files'] if f.name in ['main.py', 'app.py', '__main__.py']]
        entry_content = ""
        if entry_files:
            try:
                with open(entry_files[0], 'r', encoding='utf-8') as f:
                    entry_content = f.read()
            except (IOError, UnicodeDecodeError) as e:
                logger.warning(f"Failed to read entry point {entry_files[0]}: {e}")
        
        # 收集不确定的导入
        uncertain = set()
        for sym_data in symbols.values():
            uncertain.update(sym_data.imports.uncertain)
        
        # 创建provider
        try:
            provider = create_provider(
                provider_name=llm_provider,
                api_key=api_key
            )
        except ImportError as e:
            click.echo(f"\n❌ Error: {e}", err=True)
            sys.exit(1)
        except ValueError as e:
            click.echo(f"\n❌ Error: {e}", err=True)
            sys.exit(1)
        
        # 分析
        if use_ai:
            provider_names = {'anthropic': 'Claude', 'openai': 'GPT-4', 'gemini': 'Gemini'}
            click.echo(f"\n🤖 Analyzing with {provider_names.get(llm_provider, llm_provider)}...")
        else:
            click.echo("\n📋 Generating scan-only report...")
        
        engine = OracleEngine(provider=provider, max_cost_usd=config["llm"]["max_cost_usd"])
        analysis = engine.analyze_project(
            tree=tree,
            symbols=symbols,
            entry_point_content=entry_content,
            uncertain_imports=list(uncertain),
            dry_run=False
        )
        
        # 生成报告
        click.echo("📄 Generating report...")
        
        report_stats = {
            "total_files": stats.total_files,
            "included_files": stats.included_files,
            "strategy": stats.strategy,
            "classes": total_classes,
            "functions": total_functions
        }
        
        report = engine.generate_report(analysis, report_stats, project_path.name)
        
        # 创建 .ProjectOracle 文件夹
        output_dir = project_path / ".ProjectOracle"
        output_dir.mkdir(exist_ok=True)
        
        # 生成报告文件名: 项目名_analysis.md
        report_filename = f"{project_path.name}_analysis.md"
        output_path = output_dir / report_filename
        
        # 备份旧报告
        if output_path.exists() and not force:
            backup_path = output_dir / f"{project_path.name}_analysis.backup.md"
            output_path.rename(backup_path)
            click.echo(f"  📦 Backed up old report to: {backup_path.name}")
        
        output_path.write_text(report, encoding='utf-8')
        
        # 成功消息
        click.echo("\n" + "="*60)
        click.echo("✅ Analysis Complete!")
        click.echo("="*60)
        click.echo(f"\n📄 Report: {output_path}")
        click.echo(f"\n📊 Statistics:")
        click.echo(f"  • Files scanned: {stats.total_files:,}")
        click.echo(f"  • Files analyzed: {stats.included_files:,}")
        click.echo(f"  • Classes found: {total_classes}")
        click.echo(f"  • Functions found: {total_functions}")
        
        if not use_ai:
            click.echo(f"\n💡 Tip: Run again and choose AI Analysis for deeper insights!")
        
        click.echo("")
    
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
