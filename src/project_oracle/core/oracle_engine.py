"""Oracle Engine - LLM-powered project analysis and report generation."""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from anthropic import Anthropic, APITimeoutError

from ..models import DirectoryTree, SymbolData, AnalysisResult, CostLimitExceeded
from ..utils import logger


class OracleEngine:
    """Manages LLM analysis and report generation."""
    
    def __init__(self, api_key: str, max_cost_usd: float = 0.50):
        self.client = Anthropic(api_key=api_key)
        self.max_cost_usd = max_cost_usd
        
        # Claude 3.5 Sonnet pricing
        self.input_price_per_1k = 0.003
        self.output_price_per_1k = 0.015
    
    def estimate_cost(self, input_tokens: int, output_tokens: int = 2000) -> float:
        """Estimate API cost."""
        input_cost = (input_tokens / 1000) * self.input_price_per_1k
        output_cost = (output_tokens / 1000) * self.output_price_per_1k
        return input_cost + output_cost
    
    def estimate_input_tokens(self, tree_str: str, symbols: str, entry_point: str) -> int:
        """Rough token estimation (4 chars ≈ 1 token)."""
        total_chars = len(tree_str) + len(symbols) + len(entry_point) + 2000
        return total_chars // 4
    
    def analyze_project(
        self,
        tree: DirectoryTree,
        symbols: Dict[str, SymbolData],
        entry_point_content: str,
        uncertain_imports: list[str],
        dry_run: bool = False
    ) -> AnalysisResult:
        """Analyze project using LLM."""
        
        # Build prompt
        tree_str = tree.to_string()
        symbols_json = self._serialize_symbols(symbols)
        
        # Estimate cost
        estimated_tokens = self.estimate_input_tokens(tree_str, symbols_json, entry_point_content)
        estimated_cost = self.estimate_cost(estimated_tokens)
        
        logger.info(f"Estimated tokens: {estimated_tokens}, cost: ${estimated_cost:.4f}")
        
        # Cost protection
        if estimated_cost > self.max_cost_usd:
            raise CostLimitExceeded(
                f"Estimated cost ${estimated_cost:.4f} exceeds limit ${self.max_cost_usd:.2f}"
            )
        
        if dry_run:
            return AnalysisResult(
                business_domain=f"[DRY RUN] Estimated cost: ${estimated_cost:.4f}",
                architecture_pattern="N/A",
                core_modules=[],
                data_flow="N/A",
                entry_points=[],
                fragile_points=[],
                resolved_uncertain_imports={},
                estimated_cost=estimated_cost,
                estimated_tokens=estimated_tokens
            )
        
        # Build and send prompt
        prompt = self._build_prompt(tree_str, symbols_json, entry_point_content, uncertain_imports)
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Log actual cost
            actual_cost = self.estimate_cost(
                response.usage.input_tokens,
                response.usage.output_tokens
            )
            logger.info(f"Actual cost: ${actual_cost:.4f}")
            
            # Parse response
            return self._parse_response(response.content[0].text)
        
        except APITimeoutError:
            logger.error("LLM API timeout")
            return self._fallback_analysis()
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return self._fallback_analysis()
    
    def _build_prompt(self, tree: str, symbols: str, entry_point: str, uncertain: list[str]) -> str:
        """Build analysis prompt."""
        return f"""You are analyzing a software project. Generate insights about its architecture.

## Directory Tree:
```
{tree}
```

## Extracted Symbols (first 6000 chars):
```json
{symbols[:6000]}
```

## Entry Point Content (first 2000 chars):
```python
{entry_point[:2000]}
```

## Uncertain Imports:
{', '.join(uncertain) if uncertain else 'None'}

---

Generate a JSON response with this schema:
```json
{{
  "business_domain": "One sentence description",
  "architecture_pattern": "e.g., MVC, Clean Architecture, Microservices",
  "core_modules": [
    {{
      "module": "module_name",
      "purpose": "What it does",
      "key_components": ["Component1", "Component2"],
      "responsibilities": "Detailed responsibilities"
    }}
  ],
  "data_flow": "2-3 sentence description of typical request flow",
  "entry_points": ["file paths of entry points"],
  "fragile_points": ["Areas needing attention"],
  "resolved_uncertain_imports": {{"import_name": "internal" or "external"}},
  "architecture_diagram": "Simple mermaid graph TD diagram (max 8 nodes, use only A-H IDs and [] brackets)"
}}
```

CRITICAL: Only mention components found in the symbols list. Be accurate, not creative."""
    
    def _parse_response(self, response_text: str) -> AnalysisResult:
        """Parse LLM JSON response."""
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end]
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end]
            
            data = json.loads(response_text.strip())
            
            return AnalysisResult(
                business_domain=data.get("business_domain", "Unknown"),
                architecture_pattern=data.get("architecture_pattern", "Unknown"),
                core_modules=data.get("core_modules", []),
                data_flow=data.get("data_flow", ""),
                entry_points=data.get("entry_points", []),
                fragile_points=data.get("fragile_points", []),
                resolved_uncertain_imports=data.get("resolved_uncertain_imports", {}),
                architecture_diagram=data.get("architecture_diagram")
            )
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._fallback_analysis()
    
    def _fallback_analysis(self) -> AnalysisResult:
        """Generate basic fallback analysis."""
        return AnalysisResult(
            business_domain="Analysis failed - using fallback",
            architecture_pattern="Unknown",
            core_modules=[],
            data_flow="Unable to analyze data flow",
            entry_points=[],
            fragile_points=["Analysis incomplete - LLM call failed"],
            resolved_uncertain_imports={}
        )
    
    def _serialize_symbols(self, symbols: Dict[str, SymbolData]) -> str:
        """Convert symbols to JSON string."""
        result = []
        for file_path, symbol_data in list(symbols.items())[:50]:  # Limit files
            file_data = {
                "file": file_path,
                "classes": [
                    {
                        "name": cls.name,
                        "methods": [m.name for m in cls.methods[:5]],  # Limit methods
                        "docstring": cls.docstring
                    }
                    for cls in symbol_data.classes[:10]  # Limit classes
                ],
                "functions": [
                    {
                        "name": func.name,
                        "args": func.args,
                        "docstring": func.docstring
                    }
                    for func in symbol_data.functions[:10]  # Limit functions
                ]
            }
            result.append(file_data)
        
        return json.dumps(result, indent=2)
    
    def generate_report(self, analysis: AnalysisResult, stats: dict, project_name: str) -> str:
        """Generate Markdown report.

"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        report = f"""# 🔮 ProjectOracle Report

> **Generated**: {now}  
> **Project**: {project_name}
> **Analyzer Version**: 1.0.0

---

## 1. 🏗️ Foundation

- **Business Domain**: {analysis.business_domain}
- **Architecture Pattern**: {analysis.architecture_pattern}
- **Files Scanned**: {stats.get('total_files', 0):,}
- **Files Analyzed**: {stats.get('included_files', 0):,}
- **Analysis Strategy**: {stats.get('strategy', 'unknown')}

---

## 2. 🏛️ Architecture

{self._format_architecture(analysis)}

---

## 3. 🗺️ Core Modules

{self._format_modules(analysis.core_modules)}

---

## 4. 📊 Data Flow

{analysis.data_flow}

---

## 5. 🤖 AI Development Guide

### Entry Points
{self._format_list(analysis.entry_points)}

### Fragile Points ⚠️
{self._format_list(analysis.fragile_points)}

---

## 6. 📈 Statistics

- **Total Files**: {stats.get('total_files', 0):,}
- **Files Analyzed**: {stats.get('included_files', 0):,}
- **Classes Found**: {stats.get('classes', 0)}
- **Functions Found**: {stats.get('functions', 0)}

---

*Generated by ProjectOracle v1.0.0*
"""
        return report
    
    def _format_architecture(self, analysis: AnalysisResult) -> str:
        """Format architecture section."""
        if analysis.architecture_diagram:
            return f"```mermaid\n{analysis.architecture_diagram}\n```"
        return f"**Pattern**: {analysis.architecture_pattern}"
    
    def _format_modules(self, modules: list[dict]) -> str:
        """Format modules as table."""
        if not modules:
            return "No modules detected."
        
        lines = ["| Module | Purpose | Key Components |", "|--------|---------|----------------|"]
        for mod in modules[:10]:
            name = mod.get('module', 'Unknown')
            purpose = mod.get('purpose', 'N/A')
            components = ', '.join(mod.get('key_components', [])[:3])
            lines.append(f"| **{name}** | {purpose} | {components} |")
        
        return '\n'.join(lines)
    
    def _format_list(self, items: list[str]) -> str:
        """Format list items."""
        if not items:
            return "None identified."
        return '\n'.join(f"- `{item}`" for item in items[:10])
