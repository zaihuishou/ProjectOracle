"""Python AST-based symbol extractor with three-category import classification."""

import ast
from pathlib import Path
from typing import Optional

from ..models import (
    SymbolData, ClassInfo, FunctionInfo, MethodInfo,
    ImportInfo
)
from ..utils import logger, PYTHON_STDLIB


class PythonParser:
    """Extract symbols from Python files using AST."""
    
    def __init__(self, project_root: str, requirements_path: Optional[str] = None):
        self.project_root = Path(project_root)
        self.requirements = self._load_requirements(requirements_path)
        self.stdlib_modules = PYTHON_STDLIB
    
    def _load_requirements(self, requirements_path: Optional[str]) -> set[str]:
        """Load package names from requirements.txt."""
        if not requirements_path:
            req_file = self.project_root / 'requirements.txt'
            if not req_file.exists():
                return set()
            requirements_path = req_file
        
        packages = set()
        try:
            with open(requirements_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    # Extract package name (before ==, >=, etc.)
                    pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('[')[0].strip()
                    packages.add(pkg_name.lower())
        except Exception as e:
            logger.warning(f"Failed to load requirements: {e}")
        
        return packages
    
    def extract(self, file_path: Path) -> SymbolData:
        """Extract classes, functions, and imports from Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            classes = []
            functions = []
            imports = ImportInfo()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Only extract top-level classes
                    if self._is_top_level(node, tree):
                        classes.append(self._extract_class_info(node))
                
                elif isinstance(node, ast.FunctionDef):
                    # Only extract top-level functions
                    if self._is_top_level(node, tree):
                        functions.append(self._extract_function_info(node))
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    self._extract_imports(node, imports)
            
            return SymbolData(
                file_path=str(file_path),
                classes=classes,
                functions=functions,
                imports=imports
            )
        
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return SymbolData(file_path=str(file_path))
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return SymbolData(file_path=str(file_path))
    
    def _is_top_level(self, node, tree) -> bool:
        """Check if node is a top-level definition."""
        for item in tree.body:
            if item == node:
                return True
        return False
    
    def _extract_class_info(self, node: ast.ClassDef) -> ClassInfo:
        """Extract information from a class definition."""
        # Get base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(self._get_attribute_name(base))
        
        # Get decorators
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        
        # Get methods (exclude private)
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith('_'):
                methods.append(self._extract_method_info(item))
        
        # Get docstring
        docstring = ast.get_docstring(node)
        if docstring:
            docstring = docstring.split('\n')[0]  # First line only
        
        return ClassInfo(
            name=node.name,
            bases=bases,
            decorators=decorators,
            methods=methods,
            docstring=docstring
        )
    
    def _extract_function_info(self, node: ast.FunctionDef) -> FunctionInfo:
        """Extract information from a function definition."""
        # Get arguments with type hints
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += ": " + self._get_annotation(arg.annotation)
            args.append(arg_str)
        
        # Get defaults
        defaults = node.args.defaults
        if defaults:
            num_defaults = len(defaults)
            for i, default in enumerate(defaults):
                idx = len(args) - num_defaults + i
                if idx < len(args) and '=' not in args[idx]:
                    args[idx] += " = " + self._get_default_value(default)
        
        # Get return type
        returns = None
        if node.returns:
            returns = self._get_annotation(node.returns)
        
        # Get decorators
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        
        # Get docstring
        docstring = ast.get_docstring(node)
        if docstring:
            docstring = docstring.split('\n')[0]
        
        return FunctionInfo(
            name=node.name,
            args=args,
            returns=returns,
            decorators=decorators,
            docstring=docstring
        )
    
    def _extract_method_info(self, node: ast.FunctionDef) -> MethodInfo:
        """Extract information from a method definition."""
        func_info = self._extract_function_info(node)
        return MethodInfo(
            name=func_info.name,
            args=func_info.args,
            returns=func_info.returns,
            decorators=func_info.decorators,
            docstring=func_info.docstring
        )
    
    def _extract_imports(self, node, imports: ImportInfo):
        """Extract and classify imports."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                category = self.classify_import(alias.name)
                
                if category == "internal":
                    imports.internal_confirmed.append(alias.name)
                elif category == "external":
                    imports.external_confirmed.append(alias.name)
                else:
                    imports.uncertain.append(alias.name)
                
                # Track aliases
                if alias.asname:
                    imports.aliased[alias.asname] = alias.name
        
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            category = self.classify_import(module)
            
            for alias in node.names:
                if alias.name == '*':
                    import_name = f"{module}.*"
                else:
                    import_name = f"{module}.{alias.name}" if module else alias.name
                
                if category == "internal":
                    imports.internal_confirmed.append(import_name)
                elif category == "external":
                    imports.external_confirmed.append(import_name)
                else:
                    imports.uncertain.append(import_name)
                
                # Track aliases
                if alias.asname:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    imports.aliased[alias.asname] = full_name
    
    def classify_import(self, import_name: str) -> str:
        """
        Classify import as internal, external, or uncertain.
        
        Returns:
            "internal" | "external" | "uncertain"
        """
        if not import_name:
            return "uncertain"
        
        # Rule 1: Relative imports are always internal
        if import_name.startswith('.'):
            return "internal"
        
        # Get base package name
        base_module = import_name.split('.')[0]
        
        # Rule 2: Check against Python stdlib
        if base_module in self.stdlib_modules:
            return "external"
        
        # Rule 3: Check against requirements.txt
        if base_module.lower() in self.requirements:
            return "external"
        
        # Rule 4: Everything else is uncertain
        return "uncertain"
    
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get full attribute name (e.g., 'models.Base')."""
        parts = []
        current = node
        
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        
        if isinstance(current, ast.Name):
            parts.append(current.id)
        
        return '.'.join(reversed(parts))
    
    def _get_decorator_name(self, node) -> str:
        """Get decorator name."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
            elif isinstance(node.func, ast.Attribute):
                return self._get_attribute_name(node.func)
        return "unknown"
    
    def _get_annotation(self, node) -> str:
        """Get type annotation as string."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Subscript):
            value = self._get_annotation(node.value)
            slice_val = self._get_annotation(node.slice)
            return f"{value}[{slice_val}]"
        elif isinstance(node, ast.Attribute):
            return self._get_attribute_name(node)
        elif isinstance(node, ast.Tuple):
            elts = [self._get_annotation(e) for e in node.elts]
            return f"({', '.join(elts)})"
        return "Any"
    
    def _get_default_value(self, node) -> str:
        """Get default value as string."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return f'"{node.value}"'
            return str(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.List):
            return "[]"
        elif isinstance(node, ast.Dict):
            return "{}"
        return "..."
