"""Project scanner with gitignore support and intelligent file prioritization."""

import os
import hashlib
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import pathspec

from ..models import DirectoryTree, DirectoryNode, ScanStats
from ..utils import logger


class Scanner:
    """Scans project directory respecting gitignore rules."""
    
    DEFAULT_IGNORES = [
        'node_modules/', 'venv/', '.venv/', 'env/',
        '__pycache__/', '*.pyc', '*.pyo', '*.pyd',
        '.git/', '.svn/', '.hg/',
        'dist/', 'build/', 'target/', 'out/',
        '*.egg-info/', '.pytest_cache/', '.tox/',
        'coverage/', '.coverage', 'htmlcov/',
        'logs/', '*.log', '.DS_Store'
    ]
    
    SENSITIVE_PATTERNS = [
        '.env', '.env.*', '*.env',
        'id_rsa', 'id_dsa', 
        '*.pem', '*.key', '*.crt', '*.p12', '*.jks', '*.keystore',
        'secrets.json', 'client_secrets.json', 'credentials.json'
    ]
    
    SENSITIVE_DIRS = ['.aws/', '.ssh/', '.gnupg/', 'credentials/']
    
    def __init__(self, root_path: str, max_files: int = 5000, workers: int = 4, language: str = 'auto'):
        self.root_path = Path(root_path).resolve()
        self.max_files = max_files
        self.workers = workers
        self.language = language
        self.gitignore_spec = self._load_gitignore()
        self.ignore_spec = self._merge_ignore_rules()
    
    def _load_gitignore(self) -> Optional[pathspec.PathSpec]:
        """Load .gitignore file if exists."""
        gitignore_path = self.root_path / '.gitignore'
        if not gitignore_path.exists():
            return None
        
        try:
            with open(gitignore_path, 'r') as f:
                patterns = f.read().splitlines()
            return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
        except Exception as e:
            logger.warning(f"Failed to load .gitignore: {e}")
            return None
    
    def _merge_ignore_rules(self) -> pathspec.PathSpec:
        """Merge default patterns with user .gitignore."""
        all_patterns = self.DEFAULT_IGNORES.copy()
        
        if self.gitignore_spec:
            all_patterns.extend(self.gitignore_spec.patterns)
        
        return pathspec.PathSpec.from_lines('gitwildmatch', all_patterns)
    
    def _is_ignored(self, path: Path) -> bool:
        """Check if path should be ignored."""
        try:
            rel_path = path.relative_to(self.root_path)
            return self.ignore_spec.match_file(str(rel_path))
        except ValueError:
            return False
    
    def _is_sensitive_file(self, path: Path) -> bool:
        """Check if file contains sensitive data."""
        name_lower = path.name.lower()
        
        # Check filename patterns
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern.startswith('*') and pattern.endswith('*'):
                if pattern[1:-1] in name_lower:
                    return True
            elif pattern.startswith('*.'):
                if name_lower.endswith(pattern[1:]):
                    return True
            elif name_lower == pattern:
                return True
        
        # Check if in sensitive directory
        path_str = str(path)
        for sens_dir in self.SENSITIVE_DIRS:
            if sens_dir in path_str:
                return True
        
        return False
    
    def get_directory_tree(self, max_depth: int = 4) -> DirectoryTree:
        """Generate directory tree structure."""
        root_node = DirectoryNode(name=self.root_path.name, is_dir=True)
        total_files = 0
        
        def _build_tree(current_path: Path, current_node: DirectoryNode, depth: int):
            nonlocal total_files
            
            if depth > max_depth:
                return
            
            try:
                items = sorted(current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
            except PermissionError:
                return
            
            file_count = 0
            
            for item in items:
                if self._is_ignored(item):
                    continue
                
                if item.is_file():
                    file_count += 1
                    total_files += 1
                    if depth < max_depth:  # Only add file nodes if not at max depth
                        child = DirectoryNode(name=item.name, is_dir=False)
                        current_node.children.append(child)
                
                elif item.is_dir():
                    child = DirectoryNode(name=item.name, is_dir=True)
                    current_node.children.append(child)
                    _build_tree(item, child, depth + 1)
                    file_count += child.file_count
            
            current_node.file_count = file_count
        
        _build_tree(self.root_path, root_node, 0)
        
        return DirectoryTree(root=root_node, depth=max_depth, total_files=total_files)
    
    def get_scannable_files(self, extensions: list[str] = None) -> dict:
        """
        Get list of files to analyze.
        
        Args:
            extensions: List of file extensions (e.g., ['.py', '.java'])
                       If None, auto-detect language and use appropriate extensions
        
        Returns:
            dict with keys: files, strategy, total_found, included, language
        """
        # Auto-detect language if extensions not specified
        detected_language = None
        if extensions is None:
            from .language_detector import LanguageDetector
            detected_language = LanguageDetector.detect(self.root_path)
            extensions = LanguageDetector.get_extensions(detected_language)
            
            if not extensions:
                # Fallback to all code extensions
                extensions = LanguageDetector.get_all_code_extensions()
        
        all_files = []
        
        # Discovery phase
        for root, dirs, files in os.walk(self.root_path, followlinks=False):
            root_path = Path(root)
            
            # Prune ignored directories
            dirs[:] = [d for d in dirs if not self._is_ignored(root_path / d)]
            
            for filename in files:
                file_path = root_path / filename
                
                # Check extension
                if not any(filename.endswith(ext) for ext in extensions):
                    # logger.debug(f"Skipping extension mismatch: {filename}")
                    continue
                
                # Check if ignored
                if self._is_ignored(file_path):
                    logger.debug(f"Skipping ignored file: {file_path}")
                    continue
                
                # Check if sensitive
                if self._is_sensitive_file(file_path):
                    logger.warning(f"!!! Skipping SENSITIVE file: {file_path} !!!")
                    continue
                
                # Check file size (skip > 500KB)
                try:
                    if file_path.stat().st_size > 500 * 1024:
                        logger.debug(f"Skipping large file: {file_path}")
                        continue
                except:
                    continue
                
                all_files.append(file_path)
        
        total_found = len(all_files)
        
        # Apply sampling if needed
        if total_found <= self.max_files:
            return {
                "files": all_files,
                "strategy": "full",
                "total_found": total_found,
                "included": total_found,
                "language": detected_language or 'unknown'
            }
        else:
            # Prioritize and sample
            prioritized = self._prioritize_files(all_files)
            sampled = prioritized[:self.max_files]
            
            logger.warning(
                f"Project has {total_found} files. Sampling {self.max_files} for analysis."
            )
            
            return {
                "files": sampled,
                "strategy": "sampled",
                "total_found": total_found,
                "included": len(sampled),
                "language": detected_language or 'unknown'
            }
    
    def _prioritize_files(self, files: list[Path]) -> list[Path]:
        """Sort files by importance score (higher = more important)."""
        scored_files = []
        
        for file_path in files:
            score = 0
            rel_path = str(file_path.relative_to(self.root_path))
            depth = len(file_path.relative_to(self.root_path).parts)
            
            # Entry point files
            if file_path.name in ['main.py', 'app.py', 'index.js', 'server.js', '__main__.py']:
                score += 1000
            
            # Config files
            if file_path.name in ['settings.py', 'config.py', '.env.example', 'setup.py']:
                score += 500
            
            # Core directories
            if any(d in rel_path for d in ['src/', 'lib/', 'app/', 'core/']):
                score += 100
            
            # Prefer shallower files
            score += (10 - min(depth, 10)) * 10
            
            # Penalize test files
            if 'test' in rel_path.lower():
                score -= 50
            
            scored_files.append((score, file_path))
        
        # Sort by score (descending)
        scored_files.sort(key=lambda x: x[0], reverse=True)
        
        return [f for _, f in scored_files]
    
    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file content."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return ""
    
    def get_scan_stats(self, extensions: list[str] = ['.py']) -> ScanStats:
        """Get statistics about scannable files."""
        result = self.get_scannable_files(extensions)
        
        # Rough time estimation (ms per file)
        estimated_seconds = (result['included'] * 50) // 1000  # 50ms per file
        
        return ScanStats(
            total_files=result['total_found'],
            included_files=result['included'],
            excluded_files=result['total_found'] - result['included'],
            strategy=result['strategy'],
            estimated_seconds=estimated_seconds
        )
