"""Language detection and utilities for multi-language support."""

from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter


class LanguageDetector:
    """Detect programming language of a project."""
    
    # Language to file extensions mapping
    LANGUAGE_EXTENSIONS: Dict[str, List[str]] = {
        # Mainstream languages
        'python': ['.py', '.pyw', '.pyx', '.pyi'],
        'java': ['.java'],
        'kotlin': ['.kt', '.kts'],
        'javascript': ['.js', '.jsx', '.mjs', '.cjs'],
        'typescript': ['.ts', '.tsx', '.mts', '.cts'],
        'go': ['.go'],
        'rust': ['.rs'],
        'c++': ['.cpp', '.cc', '.cxx', '.hpp', '.h', '.hxx', '.hh'],
        'c': ['.c', '.h'],
        'c#': ['.cs', '.csx'],
        'ruby': ['.rb', '.rake', '.gemspec'],
        'php': ['.php', '.phtml', '.php3', '.php4', '.php5'],
        'swift': ['.swift'],
        'objective-c': ['.m', '.mm', '.h'],
        'scala': ['.scala', '.sc'],
        
        # Functional languages
        'haskell': ['.hs', '.lhs'],
        'clojure': ['.clj', '.cljs', '.cljc', '.edn'],
        'elixir': ['.ex', '.exs'],
        'erlang': ['.erl', '.hrl'],
        'ocaml': ['.ml', '.mli'],
        'f#': ['.fs', '.fsi', '.fsx'],
        
        # JVM languages
        'groovy': ['.groovy', '.gvy'],
        
        # Scripting languages
        'perl': ['.pl', '.pm', '.t'],
        'lua': ['.lua'],
        'shell': ['.sh', '.bash', '.zsh', '.fish'],
        'powershell': ['.ps1', '.psm1', '.psd1'],
        'r': ['.r', '.R', '.rmd'],
        
        # Web languages
        'html': ['.html', '.htm'],
        'css': ['.css', '.scss', '.sass', '.less'],
        'vue': ['.vue'],
        'svelte': ['.svelte'],
        
        # Mobile
        'dart': ['.dart'],
        
        # Systems programming
        'zig': ['.zig'],
        'nim': ['.nim'],
        'crystal': ['.cr'],
        'v': ['.v'],
        
        # Data & ML
        'julia': ['.jl'],
        'matlab': ['.m'],
        'sql': ['.sql'],
        
        # Modern languages
        'solidity': ['.sol'],  # Blockchain
        'move': ['.move'],  # Blockchain
        'cairo': ['.cairo'],  # Blockchain
        
        # Configuration & markup
        'yaml': ['.yaml', '.yml'],
        'json': ['.json'],
        'toml': ['.toml'],
        'xml': ['.xml'],
        
        # Other
        'assembly': ['.asm', '.s'],
        'fortran': ['.f', '.f90', '.f95'],
        'cobol': ['.cob', '.cbl'],
        'pascal': ['.pas'],
        'ada': ['.ada', '.adb', '.ads'],
    }
    
    # Extension to language reverse mapping
    EXTENSION_TO_LANGUAGE: Dict[str, str] = {}
    
    @classmethod
    def _init_reverse_mapping(cls):
        """Initialize reverse mapping from extension to language."""
        if not cls.EXTENSION_TO_LANGUAGE:
            for lang, exts in cls.LANGUAGE_EXTENSIONS.items():
                for ext in exts:
                    cls.EXTENSION_TO_LANGUAGE[ext] = lang
    
    @classmethod
    def detect(cls, project_path: Path, sample_size: int = 1000) -> str:
        """
        Detect the primary programming language of a project.
        
        Args:
            project_path: Path to project root
            sample_size: Number of files to sample for detection
            
        Returns:
            Language name (e.g., 'python', 'java', 'javascript')
        """
        cls._init_reverse_mapping()
        
        if not project_path.exists():
            return 'unknown'
        
        # Count files by extension
        extension_counts = Counter()
        file_count = 0
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in cls.EXTENSION_TO_LANGUAGE:
                    extension_counts[ext] += 1
                    file_count += 1
                    
                    if file_count >= sample_size:
                        break
        
        if not extension_counts:
            return 'unknown'
        
        # Find most common extension
        most_common_ext = extension_counts.most_common(1)[0][0]
        return cls.EXTENSION_TO_LANGUAGE.get(most_common_ext, 'unknown')
    
    @classmethod
    def get_extensions(cls, language: str) -> List[str]:
        """Get file extensions for a language."""
        return cls.LANGUAGE_EXTENSIONS.get(language, [])
    
    @classmethod
    def get_language_from_extension(cls, extension: str) -> str:
        """Get language name from file extension."""
        cls._init_reverse_mapping()
        return cls.EXTENSION_TO_LANGUAGE.get(extension.lower(), 'unknown')
    
    @classmethod
    def get_all_code_extensions(cls) -> List[str]:
        """Get all supported code file extensions."""
        all_exts = []
        for exts in cls.LANGUAGE_EXTENSIONS.values():
            all_exts.extend(exts)
        return all_exts
    
    @classmethod
    def detect_with_confidence(cls, project_path: Path) -> Tuple[str, float]:
        """
        Detect language with confidence score.
        
        Returns:
            Tuple of (language, confidence) where confidence is 0.0-1.0
        """
        cls._init_reverse_mapping()
        
        extension_counts = Counter()
        total_files = 0
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in cls.EXTENSION_TO_LANGUAGE:
                    extension_counts[ext] += 1
                    total_files += 1
        
        if not extension_counts or total_files == 0:
            return 'unknown', 0.0
        
        # Most common extension
        most_common_ext, count = extension_counts.most_common(1)[0]
        language = cls.EXTENSION_TO_LANGUAGE[most_common_ext]
        confidence = count / total_files
        
        return language, confidence
    
    @classmethod
    def is_multi_language(cls, project_path: Path, threshold: float = 0.3) -> bool:
        """
        Check if project uses multiple languages significantly.
        
        Args:
            threshold: Minimum ratio for secondary language to be considered significant
        """
        cls._init_reverse_mapping()
        
        language_counts = Counter()
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in cls.EXTENSION_TO_LANGUAGE:
                    lang = cls.EXTENSION_TO_LANGUAGE[ext]
                    language_counts[lang] += 1
        
        if len(language_counts) < 2:
            return False
        
        total = sum(language_counts.values())
        if total == 0:
            return False
        
        # Check if second language exceeds threshold
        sorted_langs = language_counts.most_common(2)
        if len(sorted_langs) >= 2:
            second_ratio = sorted_langs[1][1] / total
            return second_ratio >= threshold
        
        return False
    
    @classmethod
    def get_language_display_name(cls, language: str) -> str:
        """Get human-readable language name."""
        display_names = {
            # Mainstream
            'python': 'Python',
            'java': 'Java',
            'kotlin': 'Kotlin',
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'go': 'Go',
            'rust': 'Rust',
            'c++': 'C++',
            'c': 'C',
            'c#': 'C#',
            'ruby': 'Ruby',
            'php': 'PHP',
            'swift': 'Swift',
            'objective-c': 'Objective-C',
            'scala': 'Scala',
            # Functional
            'haskell': 'Haskell',
            'clojure': 'Clojure',
            'elixir': 'Elixir',
            'erlang': 'Erlang',
            'ocaml': 'OCaml',
            'f#': 'F#',
            # JVM
            'groovy': 'Groovy',
            # Scripting
            'r': 'R',
            'perl': 'Perl',
            'lua': 'Lua',
            'shell': 'Shell',
            'powershell': 'PowerShell',
            # Web
            'html': 'HTML',
            'css': 'CSS',
            'vue': 'Vue',
            'svelte': 'Svelte',
            # Mobile
            'dart': 'Dart',
            # Systems
            'zig': 'Zig',
            'nim': 'Nim',
            'crystal': 'Crystal',
            'v': 'V',
            # Data & ML
            'julia': 'Julia',
            'matlab': 'MATLAB',
            'sql': 'SQL',
            # Blockchain
            'solidity': 'Solidity',
            'move': 'Move',
            'cairo': 'Cairo',
            # Config
            'yaml': 'YAML',
            'json': 'JSON',
            'toml': 'TOML',
            'xml': 'XML',
            # Other
            'assembly': 'Assembly',
            'fortran': 'Fortran',
            'cobol': 'COBOL',
            'pascal': 'Pascal',
            'ada': 'Ada',
            'unknown': 'Unknown',
        }
        return display_names.get(language, language.title())
