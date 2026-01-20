"""Data models for ProjectOracle."""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class FunctionInfo:
    """Information about a function."""
    name: str
    args: list[str]
    returns: Optional[str]
    decorators: list[str]
    docstring: Optional[str]


@dataclass
class MethodInfo:
    """Information about a class method."""
    name: str
    args: list[str]
    returns: Optional[str]
    decorators: list[str]
    docstring: Optional[str]


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    bases: list[str]
    decorators: list[str]
    methods: list[MethodInfo]
    docstring: Optional[str]


@dataclass
class ImportInfo:
    """Categorized import information."""
    internal_confirmed: list[str] = field(default_factory=list)
    external_confirmed: list[str] = field(default_factory=list)
    uncertain: list[str] = field(default_factory=list)
    aliased: dict[str, str] = field(default_factory=dict)


@dataclass
class SymbolData:
    """Extracted symbols from a file."""
    file_path: str
    classes: list[ClassInfo] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    imports: ImportInfo = field(default_factory=ImportInfo)


@dataclass
class DirectoryNode:
    """A node in the directory tree."""
    name: str
    is_dir: bool
    file_count: int = 0
    children: list['DirectoryNode'] = field(default_factory=list)


@dataclass
class DirectoryTree:
    """Directory tree structure."""
    root: DirectoryNode
    depth: int
    total_files: int

    def to_string(self, max_depth: int = 4) -> str:
        """Convert tree to string representation."""
        lines = []
        
        def _format_node(node: DirectoryNode, depth: int, prefix: str = ""):
            if depth > max_depth:
                return
            
            if node.is_dir:
                lines.append(f"{prefix}{node.name}/ ({node.file_count} files)")
                for i, child in enumerate(node.children):
                    is_last = i == len(node.children) - 1
                    child_prefix = prefix + ("    " if is_last else "│   ")
                    connector = "└── " if is_last else "├── "
                    
                    if child.is_dir:
                        lines.append(f"{prefix}{connector}{child.name}/ ({child.file_count} files)")
                        _format_node(child, depth + 1, child_prefix)
                    else:
                        lines.append(f"{prefix}{connector}{child.name}")
            else:
                lines.append(f"{prefix}{node.name}")
        
        _format_node(self.root, 0)
        return "\n".join(lines)


@dataclass
class ScanStats:
    """Statistics from file scanning."""
    total_files: int
    included_files: int
    excluded_files: int
    strategy: str  # "full" or "sampled"
    estimated_seconds: int


@dataclass
class AnalysisResult:
    """Result from LLM analysis."""
    business_domain: str
    architecture_pattern: str
    core_modules: list[dict]
    data_flow: str
    entry_points: list[str]
    fragile_points: list[str]
    resolved_uncertain_imports: dict[str, str]
    architecture_diagram: Optional[str] = None
    estimated_cost: Optional[float] = None
    estimated_tokens: Optional[int] = None


@dataclass
class MonorepoConfig:
    """Monorepo configuration."""
    type: str
    workspaces: list[str] = field(default_factory=list)
    dependencies: dict[str, list[str]] = field(default_factory=dict)


class CostLimitExceeded(Exception):
    """Raised when estimated cost exceeds configured limit."""
    pass
