"""Generic parser for multi-language support."""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from .language_detector import LanguageDetector
from ..utils import logger


@dataclass
class FileContent:
    """Generic file content representation (language-agnostic)."""
    path: str
    language: str
    content: str
    size: int
    lines: int
    encoding: str = 'utf-8'


class GenericParser:
    """
    Generic parser for any programming language.
    
    Unlike PythonParser which does AST analysis, this parser simply
    reads file content and lets the AI understand the code structure.
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.max_file_size = 500 * 1024  # 500KB limit
        self.max_content_chars = 10000  # Max chars to read per file
    
    def extract(self, file_path: Path) -> FileContent:
        """
        Extract file content.
        
        Args:
            file_path: Path to file
            
        Returns:
            FileContent object with file information
        """
        try:
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                logger.debug(f"Skipping large file: {file_path} ({file_size} bytes)")
                return FileContent(
                    path=str(file_path.relative_to(self.project_root)),
                    language=self._detect_language(file_path),
                    content=f"[File too large: {file_size} bytes]",
                    size=file_size,
                    lines=0
                )
            
            # Try to read file
            content = self._read_file(file_path)
            
            # Truncate if too long
            if len(content) > self.max_content_chars:
                content = content[:self.max_content_chars] + "\n\n[... truncated ...]"
            
            return FileContent(
                path=str(file_path.relative_to(self.project_root)),
                language=self._detect_language(file_path),
                content=content,
                size=file_size,
                lines=content.count('\n') + 1
            )
        
        except Exception as e:
            logger.warning(f"Failed to extract {file_path}: {e}")
            return FileContent(
                path=str(file_path.relative_to(self.project_root)),
                language='unknown',
                content=f"[Error reading file: {e}]",
                size=0,
                lines=0
            )
    
    def _read_file(self, file_path: Path) -> str:
        """Read file with encoding detection."""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                return file_path.read_text(encoding=encoding)
            except (UnicodeDecodeError, LookupError):
                continue
        
        # Fallback: read as binary and decode with errors='ignore'
        return file_path.read_bytes().decode('utf-8', errors='ignore')
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect language from file extension."""
        ext = file_path.suffix.lower()
        return LanguageDetector.get_language_from_extension(ext)
    
    def extract_batch(self, file_paths: list[Path]) -> dict[str, FileContent]:
        """
        Extract content from multiple files.
        
        Returns:
            Dictionary mapping file path to FileContent
        """
        results = {}
        for file_path in file_paths:
            content = self.extract(file_path)
            results[content.path] = content
        return results
