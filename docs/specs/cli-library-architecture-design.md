# Design Document

## Overview

This design document outlines the architecture for transforming the PDF Layout Extractor and Rebuilder into `pdfrebuilder`, a dual-purpose tool that functions both as a CLI application and as a Python library. The design follows Python 3.12+ best practices for configuration management, logging, temporary file handling, and package distribution.

## Architecture

### High-Level Architecture

```
pdfrebuilder/
├── src/
│   └── pdfrebuilder/                # Main package
│       ├── __init__.py              # Library API exports
│       ├── __main__.py              # CLI entry point (python -m pdfrebuilder)
│       ├── cli/                     # CLI-specific modules
│       │   ├── __init__.py
│       │   ├── main.py              # CLI application logic
│       │   ├── commands.py          # CLI command implementations
│       │   └── console.py           # Rich console output utilities
│       ├── core/                    # Core library functionality
│       │   ├── __init__.py
│       │   ├── extractor.py         # PDF extraction logic
│       │   ├── rebuilder.py         # PDF rebuilding logic
│       │   ├── comparator.py        # PDF comparison utilities
│       │   └── processor.py         # Document processing pipeline
│       ├── config/                  # Configuration management
│       │   ├── __init__.py
│       │   ├── manager.py           # Configuration manager
│       │   ├── defaults.py          # Default configuration values
│       │   └── migration.py         # Configuration migration utilities
│       ├── engines/                 # Processing engines
│       │   ├── __init__.py
│       │   ├── base.py              # Base engine interface
│       │   ├── fitz_engine.py       # PyMuPDF engine
│       │   ├── reportlab_engine.py  # ReportLab engine
│       │   └── wand_engine.py       # ImageMagick/Wand engine
│       ├── models/                  # Data models and schemas
│       │   ├── __init__.py
│       │   ├── document.py          # Document structure models
│       │   ├── config.py            # Configuration models
│       │   └── exceptions.py        # Custom exception classes
│       ├── utils/                   # Utility modules
│       │   ├── __init__.py
│       │   ├── logging.py           # Logging utilities
│       │   ├── paths.py             # Path management utilities
│       │   ├── resources.py         # Resource management
│       │   └── security.py          # Security utilities
│       └── py.typed                 # Type hints marker
├── tests/                           # Test suite
├── docs/                            # Documentation
├── examples/                        # Usage examples
└── pyproject.toml                   # Project configuration
```

## Components and Interfaces

### 1. Library API Interface (`pdfrebuilder/__init__.py`)

The main library interface provides high-level functions for common operations:

```python
# High-level API functions
def extract(
    input_path: Union[str, Path, BinaryIO],
    output_config: Optional[Union[str, Path]] = None,
    engine: str = "auto",
    **options
) -> DocumentStructure:
    """Extract PDF layout to configuration."""

def rebuild(
    config: Union[str, Path, dict, DocumentStructure],
    output_path: Union[str, Path, BinaryIO],
    engine: str = "auto",
    **options
) -> None:
    """Rebuild PDF from configuration."""

def compare(
    pdf1: Union[str, Path, BinaryIO],
    pdf2: Union[str, Path, BinaryIO],
    output_diff: Optional[Union[str, Path]] = None,
    **options
) -> ComparisonResult:
    """Compare two PDFs visually."""

def process_pipeline(
    input_path: Union[str, Path, BinaryIO],
    output_path: Union[str, Path, BinaryIO],
    config_path: Optional[Union[str, Path]] = None,
    **options
) -> PipelineResult:
    """Run full extract-rebuild-compare pipeline."""

# Configuration and context managers
class PDFRebuilder:
    """Main class for advanced usage with configuration."""

    def __init__(self, config: Optional[ConfigManager] = None):
        self.config = config or ConfigManager()

    async def extract_async(self, ...): ...
    async def rebuild_async(self, ...): ...

    def __enter__(self): ...
    def __exit__(self, ...): ...
```

### 2. CLI Interface (`pdfrebuilder/cli/`)

The CLI interface maintains backward compatibility while providing modern argument parsing:

```python
# pdfrebuilder/cli/main.py
import typer
from typing_extensions import Annotated

app = typer.Typer(
    name="pdfrebuilder",
    help="Extract and rebuild PDF layouts with high fidelity.",
    no_args_is_help=True,
)

@app.command()
def extract(
    input_file: Annotated[Path, typer.Argument(help="Input PDF file")],
    config: Annotated[Optional[Path], typer.Option("--config", "-c")] = None,
    engine: Annotated[str, typer.Option("--engine", "-e")] = "auto",
    output_dir: Annotated[Optional[Path], typer.Option("--output-dir", "-o")] = None,
    log_level: Annotated[str, typer.Option("--log-level", "-l")] = "INFO",
    # ... other options
):
    """Extract PDF layout to JSON configuration."""

@app.command()
def rebuild(
    config: Annotated[Path, typer.Argument(help="Configuration file")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o")] = None,
    engine: Annotated[str, typer.Option("--engine", "-e")] = "auto",
    # ... other options
):
    """Rebuild PDF from configuration."""

@app.command()
def pipeline(
    input_file: Annotated[Path, typer.Argument(help="Input PDF file")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o")] = None,
    # ... other options
):
    """Run full extract-rebuild-compare pipeline."""

# Entry point function
def main():
    app()
```

### 3. Configuration Management (`pdfrebuilder/config/`)

Modern configuration management using platformdirs and hierarchical configuration:

```python
# pdfrebuilder/config/manager.py
from platformdirs import user_config_dir, user_data_dir, user_cache_dir
from pathlib import Path
import os
from typing import Any, Dict, Optional
import tomllib  # Python 3.11+ built-in TOML support

class ConfigManager:
    """Manages hierarchical configuration with platform-appropriate directories."""

    def __init__(self, app_name: str = "pdfrebuilder"):
        self.app_name = app_name
        self._config_dir = Path(user_config_dir(app_name))
        self._data_dir = Path(user_data_dir(app_name))
        self._cache_dir = Path(user_cache_dir(app_name))

        # Create directories
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from multiple sources in priority order."""
        config = {}

        # 1. Load defaults
        config.update(self._get_defaults())

        # 2. Load system config (if exists)
        system_config = self._load_system_config()
        if system_config:
            config.update(system_config)

        # 3. Load user config
        user_config = self._load_user_config()
        if user_config:
            config.update(user_config)

        # 4. Load environment variables
        env_config = self._load_env_config()
        config.update(env_config)

        return config

    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        prefix = f"{self.app_name.upper()}_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                # Convert string values to appropriate types
                config[config_key] = self._convert_env_value(value)

        return config

    @property
    def config_dir(self) -> Path:
        return self._config_dir

    @property
    def data_dir(self) -> Path:
        return self._data_dir

    @property
    def cache_dir(self) -> Path:
        return self._cache_dir

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support."""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any, persist: bool = True) -> None:
        """Set configuration value and optionally persist to file."""
        keys = key.split('.')
        config = self._config

        # Navigate to parent dict
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set value
        config[keys[-1]] = value

        if persist:
            self._save_user_config()
```

### 4. Logging System (`pdfrebuilder/utils/logging.py`)

Modern logging implementation following Python best practices:

```python
# pdfrebuilder/utils/logging.py
import logging
import logging.config
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'levelname', 'levelno',
                          'pathname', 'filename', 'module', 'lineno',
                          'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process',
                          'getMessage', 'exc_info', 'exc_text', 'stack_info'):
                log_entry[key] = value

        return json.dumps(log_entry)

def setup_logging(
    level: Union[str, int] = logging.INFO,
    format_type: str = "standard",  # "standard" or "json"
    log_file: Optional[Path] = None,
    logger_name: str = "pdfrebuilder"
) -> logging.Logger:
    """Setup logging configuration for the application."""

    # Don't configure root logger when used as library
    logger = logging.getLogger(logger_name)

    # Clear existing handlers
    logger.handlers.clear()

    # Set level
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    logger.setLevel(level)

    # Create formatters
    if format_type == "json":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name."""
    return logging.getLogger(f"pdfrebuilder.{name}")
```

### 5. Resource Management (`pdfrebuilder/utils/resources.py`)

Proper resource management with context managers and cleanup:

```python
# pdfrebuilder/utils/resources.py
import tempfile
import shutil
import atexit
from pathlib import Path
from typing import Optional, List, Union, ContextManager
from contextlib import contextmanager, ExitStack
import threading
import weakref

class ResourceManager:
    """Manages temporary files and directories with automatic cleanup."""

    def __init__(self):
        self._temp_dirs: List[Path] = []
        self._temp_files: List[Path] = []
        self._lock = threading.Lock()

        # Register cleanup on exit
        atexit.register(self.cleanup_all)

    @contextmanager
    def temp_directory(self, prefix: str = "pdfrebuilder_") -> ContextManager[Path]:
        """Create a temporary directory with automatic cleanup."""
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))

        with self._lock:
            self._temp_dirs.append(temp_dir)

        try:
            yield temp_dir
        finally:
            self._cleanup_directory(temp_dir)

    @contextmanager
    def temp_file(
        self,
        suffix: str = "",
        prefix: str = "pdfrebuilder_",
        delete: bool = True
    ) -> ContextManager[Path]:
        """Create a temporary file with automatic cleanup."""
        fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        temp_file = Path(temp_path)

        # Close the file descriptor immediately
        import os
        os.close(fd)

        if delete:
            with self._lock:
                self._temp_files.append(temp_file)

        try:
            yield temp_file
        finally:
            if delete:
                self._cleanup_file(temp_file)

    def _cleanup_directory(self, path: Path) -> None:
        """Clean up a specific directory."""
        try:
            if path.exists():
                shutil.rmtree(path)
            with self._lock:
                if path in self._temp_dirs:
                    self._temp_dirs.remove(path)
        except Exception as e:
            # Log but don't raise - cleanup should be best effort
            import logging
            logging.getLogger("pdfrebuilder.resources").warning(
                f"Failed to cleanup directory {path}: {e}"
            )

    def _cleanup_file(self, path: Path) -> None:
        """Clean up a specific file."""
        try:
            if path.exists():
                path.unlink()
            with self._lock:
                if path in self._temp_files:
                    self._temp_files.remove(path)
        except Exception as e:
            import logging
            logging.getLogger("pdfrebuilder.resources").warning(
                f"Failed to cleanup file {path}: {e}"
            )

    def cleanup_all(self) -> None:
        """Clean up all managed resources."""
        with self._lock:
            # Clean up files first
            for temp_file in self._temp_files.copy():
                self._cleanup_file(temp_file)

            # Then directories
            for temp_dir in self._temp_dirs.copy():
                self._cleanup_directory(temp_dir)

# Global resource manager instance
_resource_manager = ResourceManager()

def get_resource_manager() -> ResourceManager:
    """Get the global resource manager instance."""
    return _resource_manager
```

## Data Models

### Configuration Models (`pdfrebuilder/models/config.py`)

```python
# pdfrebuilder/models/config.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class EngineType(str, Enum):
    AUTO = "auto"
    FITZ = "fitz"
    REPORTLAB = "reportlab"
    WAND = "wand"
    PSD_TOOLS = "psd-tools"

class ExtractionConfig(BaseModel):
    """Configuration for PDF extraction."""
    include_text: bool = True
    include_images: bool = True
    include_drawings: bool = True
    include_raw_backgrounds: bool = False
    engine: EngineType = EngineType.AUTO

class RebuildConfig(BaseModel):
    """Configuration for PDF rebuilding."""
    engine: EngineType = EngineType.AUTO
    compression: bool = True
    embed_fonts: bool = True
    output_dpi: int = 300

class LoggingConfig(BaseModel):
    """Configuration for logging."""
    level: LogLevel = LogLevel.INFO
    format_type: str = "standard"  # "standard" or "json"
    log_file: Optional[Path] = None
    enable_console: bool = True

class PathConfig(BaseModel):
    """Configuration for paths and directories."""
    output_dir: Optional[Path] = None
    temp_dir: Optional[Path] = None
    cache_dir: Optional[Path] = None
    config_dir: Optional[Path] = None

class PDFRebuilderConfig(BaseModel):
    """Main configuration model."""
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    rebuild: RebuildConfig = Field(default_factory=RebuildConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    paths: PathConfig = Field(default_factory=PathConfig)

    # Environment-specific settings
    environment: str = "production"  # development, testing, production
    debug: bool = False

    class Config:
        env_prefix = "PDFREBUILDER_"
        case_sensitive = False
```

### Document Models (`pdfrebuilder/models/document.py`)

```python
# pdfrebuilder/models/document.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

class DocumentStructure(BaseModel):
    """Represents the extracted document structure."""
    version: str = "1.0"
    engine: str
    engine_version: str
    metadata: Dict[str, Any]
    document_structure: List[Dict[str, Any]]

    def save(self, path: Union[str, Path]) -> None:
        """Save document structure to JSON file."""
        import json
        with open(path, 'w') as f:
            json.dump(self.dict(), f, indent=2)

    @classmethod
    def load(cls, path: Union[str, Path]) -> 'DocumentStructure':
        """Load document structure from JSON file."""
        import json
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)

class ComparisonResult(BaseModel):
    """Result of PDF comparison."""
    similarity_score: float
    differences_found: bool
    diff_image_path: Optional[Path] = None
    metrics: Dict[str, Any] = {}

class PipelineResult(BaseModel):
    """Result of full pipeline execution."""
    input_path: Path
    output_path: Path
    config_path: Optional[Path]
    extraction_time: float
    rebuild_time: float
    comparison_result: Optional[ComparisonResult] = None
    success: bool = True
    errors: List[str] = []
```

## Error Handling

### Custom Exceptions (`pdfrebuilder/models/exceptions.py`)

```python
# pdfrebuilder/models/exceptions.py
class PDFRebuilderError(Exception):
    """Base exception for PDFRebuilder."""
    pass

class ExtractionError(PDFRebuilderError):
    """Error during PDF extraction."""
    pass

class RebuildError(PDFRebuilderError):
    """Error during PDF rebuilding."""
    pass

class ConfigurationError(PDFRebuilderError):
    """Error in configuration."""
    pass

class EngineError(PDFRebuilderError):
    """Error with processing engine."""
    pass

class ValidationError(PDFRebuilderError):
    """Error during validation."""
    pass
```

## Testing Strategy

### Test Structure

```
tests/
├── unit/                           # Unit tests
│   ├── test_config_manager.py
│   ├── test_logging.py
│   ├── test_resource_manager.py
│   └── test_models.py
├── integration/                    # Integration tests
│   ├── test_cli_integration.py
│   ├── test_library_integration.py
│   └── test_engine_integration.py
├── e2e/                           # End-to-end tests
│   ├── test_full_pipeline.py
│   └── test_cross_platform.py
├── fixtures/                      # Test data
│   ├── sample_pdfs/
│   ├── configs/
│   └── expected_outputs/
└── conftest.py                    # Pytest configuration
```

### Test Configuration

```python
# tests/conftest.py
import pytest
import tempfile
from pathlib import Path
from pdfrebuilder.config import ConfigManager
from pdfrebuilder.utils.resources import ResourceManager

@pytest.fixture
def temp_config_dir():
    """Provide a temporary configuration directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def test_config_manager(temp_config_dir):
    """Provide a ConfigManager instance for testing."""
    return ConfigManager(config_dir=temp_config_dir)

@pytest.fixture
def resource_manager():
    """Provide a ResourceManager instance for testing."""
    return ResourceManager()

@pytest.fixture(scope="session")
def sample_pdf():
    """Provide path to sample PDF for testing."""
    return Path(__file__).parent / "fixtures" / "sample_pdfs" / "simple.pdf"
```

## Package Configuration

### pyproject.toml Updates

```toml
[project]
name = "pdfrebuilder"
version = "0.1.0"
description = "Extract and rebuild PDF layouts with high fidelity"
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.12"
keywords = ["pdf", "layout", "extraction", "rebuilding", "document-processing"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing :: General",
    "Topic :: Multimedia :: Graphics :: Graphics Conversion",
]

dependencies = [
    "PyMuPDF>=1.26,<2.0",
    "Pillow>=10.2.0,<11.0",
    "typer>=0.9.0,<1.0",
    "rich>=13.7.0,<14.0",
    "pydantic>=2.0.0,<3.0",
    "platformdirs>=4.0.0,<5.0",
    "reportlab>=4.0.0,<5.0",
]

[project.optional-dependencies]
psd = [
    "psd-tools>=1.9.24,<2.0",
    "numpy>=1.24.0,<2.0"
]
wand = [
    "Wand>=0.6.13,<1.0"
]
validation = [
    "opencv-python>=4.8.0,<5.0",
    "numpy>=1.24.0,<2.0",
    "scikit-image>=0.22.0,<1.0"
]
dev = [
    "pytest>=7.4.0,<8.0",
    "pytest-cov>=4.1.0,<5.0",
    "black>=23.12.0,<24.0",
    "ruff>=0.1.9,<1.0",
    "mypy>=1.8.0,<2.0",
]
all = [
    "pdfrebuilder[psd,wand,validation,dev]"
]

[project.urls]
Homepage = "https://github.com/yourusername/pdfrebuilder"
Documentation = "https://pdfrebuilder.readthedocs.io"
Repository = "https://github.com/yourusername/pdfrebuilder"
Issues = "https://github.com/yourusername/pdfrebuilder/issues"

[project.scripts]
pdfrebuilder = "pdfrebuilder.cli.main:main"

[project.entry-points."console_scripts"]
pdfrebuilder = "pdfrebuilder.cli.main:main"

[project.entry-points."pdfrebuilder.engines"]
fitz = "pdfrebuilder.engines.fitz_engine:FitzEngine"
reportlab = "pdfrebuilder.engines.reportlab_engine:ReportLabEngine"
wand = "pdfrebuilder.engines.wand_engine:WandEngine"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/pdfrebuilder"]

[tool.hatch.build.targets.wheel.sources]
"src" = ""

[tool.hatch.metadata]
allow-direct-references = true
```

This design provides a solid foundation for a modern, dual-purpose Python package that follows Python 3.12+ best practices while maintaining backward compatibility and providing both CLI and library interfaces.
